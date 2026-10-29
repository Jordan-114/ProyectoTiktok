"""Scraper didáctico de publicaciones públicas de TikTok.

"""

import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
SESION = BASE / "tiktok_state.json"
SALIDA = BASE / "resultado.json"

USUARIO = input("Usuario público de TikTok (sin @): ").strip().lstrip("@")
MAX_VIDEOS = 30

CAMPOS_METRICAS = (
    "visualizaciones",
    "me_gusta",
    "comentarios",
    "compartidos",
)

SELECTORES_CAPTION = [
    '[data-e2e="user-post-item-desc"]',
    '[data-e2e="video-desc"]',
    '[data-e2e="browse-video-desc"]',
]


def limpiar(texto):
    """Normaliza espacios en un texto."""
    return re.sub(r"\s+", " ", texto or "").strip()


def texto_util(texto):
    """True si el texto contiene letras y no es solo números/símbolos."""
    texto = limpiar(texto)
    return bool(texto and re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", texto))


def hashtags_de(texto):
    """Extrae hashtags sin repetirlos."""
    return list(dict.fromkeys(
        re.findall(r"(?<!\w)#([\wáéíóúñÁÉÍÓÚÑ]+)", texto or "")
    ))


def id_video(url):
    """Extrae el identificador numérico de una URL de video."""
    coincidencia = re.search(r"/video/(\d+)", url or "")
    return coincidencia.group(1) if coincidencia else None


def numero_valido(valor):
    """Convierte un valor numérico a entero no negativo; si no, devuelve None."""
    if valor is None or isinstance(valor, bool):
        return None

    if isinstance(valor, str):
        valor = valor.strip().replace(",", "")
        # No convertir abreviaturas como 1.2M en una cifra inventada.
        if not re.fullmatch(r"\d+", valor):
            return None

    try:
        numero = int(valor)
    except (ValueError, TypeError, OverflowError):
        return None

    return numero if numero >= 0 else None


def extraer_metricas(item):
    """Extrae métricas de los objetos de publicación de TikTok."""
    stats = item.get("stats") or item.get("statistics") or {}

    equivalencias = {
        "visualizaciones": ("playCount", "viewCount", "views", "play_count"),
        "me_gusta": ("diggCount", "likeCount", "likes", "digg_count"),
        "comentarios": ("commentCount", "comments", "comment_count"),
        "compartidos": ("shareCount", "shares", "share_count"),
    }

    resultado = {}
    for nombre, posibles_campos in equivalencias.items():
        valor = None
        for campo in posibles_campos:
            if campo in stats:
                valor = numero_valido(stats.get(campo))
                if valor is not None:
                    break
        resultado[nombre] = valor

    return resultado


def autor_item(item):
    """Devuelve el nombre de usuario del autor si viene en el JSON."""
    author = item.get("author") or item.get("authorInfo") or {}
    if isinstance(author, dict):
        return (
            author.get("uniqueId")
            or author.get("unique_id")
            or author.get("username")
            or ""
        ).lstrip("@").lower()
    return ""


def item_a_video(item):
    """Normaliza una publicación obtenida desde una respuesta JSON."""
    identificador = str(item.get("id") or "")
    descripcion = limpiar(item.get("desc") or item.get("description") or "")
    author = autor_item(item)

    text_extra = item.get("textExtra") or []
    hashtags = []
    for etiqueta in text_extra:
        if isinstance(etiqueta, dict) and etiqueta.get("hashtagName"):
            hashtags.append(etiqueta["hashtagName"])

    if not hashtags:
        hashtags = hashtags_de(descripcion)

    return {
        "id": identificador,
        "autor": author,
        "descripcion": descripcion,
        "hashtags": list(dict.fromkeys(hashtags)),
        **extraer_metricas(item),
    }


def buscar_datos_json(pagina):
    """Busca publicaciones en los JSON incrustados en la página."""
    encontrados = {}
    selectores = [
        "script#__UNIVERSAL_DATA_FOR_REHYDRATION__",
        "script#SIGI_STATE",
    ]

    def recorrer(obj):
        if isinstance(obj, dict):
            if obj.get("id") is not None and (
                obj.get("desc") is not None or obj.get("description") is not None
            ):
                video = item_a_video(obj)
                if video["id"]:
                    anterior = encontrados.get(video["id"], {})
                    combinado = {**anterior, **video}
                    for campo in CAMPOS_METRICAS:
                        if combinado.get(campo) is None:
                            combinado[campo] = anterior.get(campo)
                    if not combinado.get("descripcion"):
                        combinado["descripcion"] = anterior.get("descripcion", "")
                    encontrados[video["id"]] = combinado

            for valor in obj.values():
                recorrer(valor)

        elif isinstance(obj, list):
            for elemento in obj:
                recorrer(elemento)

    for selector in selectores:
        try:
            contenido = pagina.locator(selector).first.text_content(timeout=1500)
            if contenido:
                recorrer(json.loads(contenido))
        except Exception:
            continue

    return encontrados


def url_del_perfil(url, usuario):
    """Comprueba que una URL de video pertenezca al perfil solicitado."""
    try:
        ruta = urlparse(url).path.lower()
    except Exception:
        return False
    return ruta.startswith(f"/@{usuario.lower()}/video/")


def combinar_video(base, nuevo):
    """Combina fuentes sin reemplazar métricas válidas por valores ausentes."""
    resultado = dict(base or {})
    nuevo = nuevo or {}

    for clave, valor in nuevo.items():
        if clave in CAMPOS_METRICAS:
            if valor is not None:
                resultado[clave] = valor
            elif clave not in resultado:
                resultado[clave] = None
        elif valor not in (None, "", []):
            resultado[clave] = valor
        elif clave not in resultado:
            resultado[clave] = valor

    for campo in CAMPOS_METRICAS:
        resultado.setdefault(campo, None)

    resultado.setdefault("descripcion", "")
    resultado.setdefault("hashtags", [])
    return resultado


def main():
    if not USUARIO:
        raise SystemExit("Debes ingresar un nombre de usuario.")

    if not SESION.exists():
        raise SystemExit(
            "No existe tiktok_state.json. Ejecuta primero guardar_sesion.py."
        )

    url_perfil = f"https://www.tiktok.com/@{USUARIO}"

    perfil = {
        "usuario": USUARIO,
        "url": url_perfil,
        "nombre": "",
        "biografia": "",
        "seguidores": None,
        "seguidos": None,
        "me_gusta": None,
        "publicaciones": None,
        "videos": [],
    }

    datos_api = {}
    errores_respuesta = []

    def capturar(resp):
        """Guarda publicaciones recibidas en respuestas públicas del perfil."""
        if "/api/post/item_list" not in resp.url:
            return

        try:
            data = resp.json()
        except Exception:
            return

        items = data.get("itemList") or data.get("item_list") or []
        for item in items:
            if not isinstance(item, dict):
                continue

            video = item_a_video(item)
            identificador = video["id"]
            if not identificador:
                continue

            # Si TikTok indica el autor, descartar cualquier otra cuenta.
            if video["autor"] and video["autor"] != USUARIO.lower():
                continue

            anterior = datos_api.get(identificador, {})
            datos_api[identificador] = combinar_video(anterior, video)

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(storage_state=str(SESION))
        pagina = contexto.new_page()
        pagina.on("response", capturar)

        try:
            pagina.goto(
                url_perfil,
                wait_until="domcontentloaded",
                timeout=60000,
            )
            pagina.wait_for_timeout(5000)

            # Datos básicos del perfil.
            selectores_perfil = [
                ('[data-e2e="user-title"]', "usuario"),
                ('[data-e2e="user-subtitle"]', "nombre"),
                ('[data-e2e="user-bio"]', "biografia"),
                ('[data-e2e="followers-count"]', "seguidores"),
                ('[data-e2e="following-count"]', "seguidos"),
                ('[data-e2e="likes-count"]', "me_gusta"),
            ]

            for selector, clave in selectores_perfil:
                try:
                    loc = pagina.locator(selector).first
                    if loc.count():
                        valor = limpiar(loc.inner_text(timeout=2000))
                        if valor:
                            perfil[clave] = valor
                except Exception:
                    pass

            # Desplazarse para que TikTok cargue más publicaciones del perfil.
            for _ in range(15):
                cantidad = pagina.locator(
                    f'a[href*="/@{USUARIO.lower()}/video/"]'
                ).count()
                if cantidad >= MAX_VIDEOS:
                    break
                pagina.mouse.wheel(0, 1200)
                pagina.wait_for_timeout(1800)

            # Dejar que terminen las respuestas pendientes y leer JSON incrustado.
            pagina.wait_for_timeout(1500)
            captions_json = buscar_datos_json(pagina)

            # Recopilar únicamente enlaces del perfil consultado.
            videos = {}
            anchors = pagina.locator('a[href*="/video/"]')
            cantidad_anchors = min(anchors.count(), 200)

            for i in range(cantidad_anchors):
                enlace = anchors.nth(i)
                try:
                    href = enlace.get_attribute("href", timeout=1500) or ""
                    url_video = urljoin("https://www.tiktok.com", href)
                    identificador = id_video(url_video)

                    if not identificador or not url_del_perfil(url_video, USUARIO):
                        continue

                    info = combinar_video(
                        datos_api.get(identificador),
                        captions_json.get(identificador),
                    )

                    # Intentar leer el texto de la tarjeta si el JSON no lo tiene.
                    if not info.get("descripcion"):
                        for selector in SELECTORES_CAPTION:
                            try:
                                loc = enlace.locator(selector).first
                                if loc.count():
                                    candidato = limpiar(loc.inner_text(timeout=1000))
                                    if candidato:
                                        info["descripcion"] = candidato
                                        break
                            except Exception:
                                continue

                    # El texto alternativo puede ser descriptivo, pero no siempre es caption.
                    if not info.get("descripcion"):
                        try:
                            alt = enlace.locator("img").first.get_attribute(
                                "alt", timeout=1000
                            )
                            if texto_util(alt):
                                info["descripcion"] = limpiar(alt)
                        except Exception:
                            pass

                    info["id"] = identificador
                    info["url"] = url_video
                    info["hashtags"] = (
                        info.get("hashtags") or hashtags_de(info.get("descripcion", ""))
                    )
                    videos[identificador] = combinar_video(
                        videos.get(identificador), info
                    )
                except Exception as error:
                    errores_respuesta.append(str(error))

            # Añadir solo los elementos de la respuesta API cuyo autor coincida
            # o aquellos IDs que ya aparecieron en enlaces del perfil.
            for identificador, info in datos_api.items():
                autor = (info.get("autor") or "").lower()
                if autor and autor != USUARIO.lower():
                    continue
                if identificador not in videos and not autor:
                    # Sin autor ni enlace del perfil, no podemos asegurar
                    # que la publicación pertenezca a la cuenta buscada.
                    continue

                url_video = (
                    f"https://www.tiktok.com/@{USUARIO}/video/{identificador}"
                )
                info_final = combinar_video(videos.get(identificador), info)
                info_final["id"] = identificador
                info_final["url"] = url_video
                info_final["hashtags"] = (
                    info_final.get("hashtags")
                    or hashtags_de(info_final.get("descripcion", ""))
                )
                videos[identificador] = info_final

            # Orden estable y límite máximo.
            lista_videos = list(videos.values())[:MAX_VIDEOS]
            for video in lista_videos:
                video.setdefault("descripcion", "")
                video.setdefault("hashtags", [])
                for campo in CAMPOS_METRICAS:
                    video.setdefault(campo, None)
                video.pop("autor", None)

            perfil["videos"] = lista_videos
            perfil["publicaciones_recopiladas"] = len(lista_videos)
            perfil["videos_con_texto_util"] = sum(
                texto_util(video.get("descripcion", "")) for video in lista_videos
            )
            perfil["resumen_metricas"] = {
                campo: sum(video.get(campo) is not None for video in lista_videos)
                for campo in CAMPOS_METRICAS
            }

            SALIDA.write_text(
                json.dumps(perfil, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"\nResultado guardado en: {SALIDA}")
            print(f"Videos del perfil encontrados: {len(lista_videos)}")
            print(f"Videos con texto útil: {perfil['videos_con_texto_util']}")
            print("\nMétricas numéricas disponibles por publicación:")
            for campo, cantidad in perfil["resumen_metricas"].items():
                print(f"  {campo}: {cantidad}/{len(lista_videos)}")

            print(
                "\nNota: las métricas no proporcionadas por TikTok se guardan "
                "como null. No se inventan valores."
            )

            if not datos_api:
                print(
                    "\nAVISO: no se capturaron respuestas del endpoint esperado. "
                    "TikTok puede haber cambiado su estructura o limitar los datos."
                )

            if perfil["videos_con_texto_util"] < 10:
                print(
                    "\nADVERTENCIA: hay menos de 10 videos con texto útil. "
                    "Revisa las descripciones antes de ejecutar Big Five."
                )

            if errores_respuesta:
                print(
                    f"\nAviso: {len(errores_respuesta)} elementos no se pudieron "
                    "procesar por completo."
                )

        finally:
            contexto.close()
            navegador.close()


if __name__ == "__main__":
    main()
