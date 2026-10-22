"""Scraper didáctico de metadatos y captions públicos de TikTok."""
import json
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
SESION = BASE / "tiktok_state.json"
SALIDA = BASE / "resultado.json"

USUARIO = input("Usuario público de TikTok (sin @): ").strip().lstrip("@")

SELECTORES_CAPTION = [
    '[data-e2e="user-post-item-desc"]',
    '[data-e2e="video-desc"]',
    '[data-e2e="browse-video-desc"]',
]

MAX_VIDEOS = 30


def limpiar(texto):
    return re.sub(r"\s+", " ", texto or "").strip()


def hashtags_de(texto):
    return list(dict.fromkeys(
        re.findall(r"(?<!\w)#([\wáéíóúñÁÉÍÓÚÑ]+)", texto)
    ))


def texto_util(texto):
    """Evita considerar números aislados como texto lingüístico útil."""
    texto = limpiar(texto)
    if not texto:
        return False
    if re.fullmatch(r"[\d\s.,:;+\-]+", texto):
        return False
    return bool(re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", texto))


def id_video(url):
    coincidencia = re.search(r"/video/(\d+)", url)
    return coincidencia.group(1) if coincidencia else None


def buscar_descripciones_en_json(pagina):
    """Intenta leer captions de datos JSON ya presentes en la página."""
    encontrados = {}

    selectores = [
        "script#__UNIVERSAL_DATA_FOR_REHYDRATION__",
        "script#SIGI_STATE",
    ]

    def recorrer(obj):
        if isinstance(obj, dict):
            identificador = obj.get("id")
            descripcion = obj.get("desc")

            if (
                identificador is not None
                and isinstance(descripcion, str)
                and descripcion.strip()
            ):
                encontrados[str(identificador)] = limpiar(descripcion)

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


def main():
    if not USUARIO:
        raise SystemExit("Debes ingresar un nombre de usuario.")

    if not SESION.exists():
        raise SystemExit(
            "No existe tiktok_state.json. Revisa tu configuración local de sesión."
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

    # Aquí se guardan las descripciones y hashtags que llegan por la API.
    datos_api = {}

    def capturar(resp):
        if "/api/post/item_list" not in resp.url:
            return
        try:
            data = resp.json()
        except Exception:
            return
        for it in data.get("itemList") or []:
            datos_api[str(it.get("id"))] = {
                "descripcion": limpiar(it.get("desc", "")),
                "hashtags": [
                    t["hashtagName"]
                    for t in (it.get("textExtra") or [])
                    if t.get("hashtagName")
                ],
            }

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(storage_state=str(SESION))
        pagina = contexto.new_page()

        # Escucha las respuestas ANTES de abrir el perfil.
        pagina.on("response", capturar)

        try:
            pagina.goto(
                url_perfil,
                wait_until="domcontentloaded",
                timeout=60000,
            )
            pagina.wait_for_timeout(5000)

            for selector, clave in [
                ('[data-e2e="user-title"]', "usuario"),
                ('[data-e2e="user-subtitle"]', "nombre"),
                ('[data-e2e="user-bio"]', "biografia"),
                ('[data-e2e="followers-count"]', "seguidores"),
                ('[data-e2e="following-count"]', "seguidos"),
                ('[data-e2e="likes-count"]', "me_gusta"),
            ]:
                try:
                    loc = pagina.locator(selector).first
                    if loc.count():
                        valor = limpiar(loc.inner_text(timeout=2000))
                        if valor:
                            perfil[clave] = valor
                except Exception:
                    pass

            # Desplaza la página para cargar más publicaciones.
            for _ in range(15):
                if pagina.locator('a[href*="/video/"]').count() >= MAX_VIDEOS:
                    break
                pagina.mouse.wheel(0, 1200)
                pagina.wait_for_timeout(1800)

            print(f"Respuestas de la API capturadas: {len(datos_api)} videos")

            # Respaldo: captions desde el JSON incrustado en la página.
            captions_json = buscar_descripciones_en_json(pagina)

            videos = []
            vistos = set()
            anchors = pagina.locator('a[href*="/video/"]')

            for i in range(min(anchors.count(), 100)):
                enlace = anchors.nth(i)

                try:
                    href = enlace.get_attribute("href", timeout=1500) or ""
                    url_video = urljoin("https://www.tiktok.com", href)
                    identificador = id_video(url_video)

                    if not identificador or identificador in vistos:
                        continue

                    vistos.add(identificador)

                    # 1) Primero la API, 2) luego el JSON incrustado.
                    info = datos_api.get(identificador, {})
                    descripcion = (
                        info.get("descripcion", "")
                        or captions_json.get(identificador, "")
                    )

                    # 3) El alt de la miniatura suele contener la descripción.
                    if not descripcion:
                        try:
                            alt = enlace.locator("img").first.get_attribute(
                                "alt", timeout=1000
                            )
                            if texto_util(alt):
                                descripcion = limpiar(alt)
                        except Exception:
                            pass

                    # 4) Selectores de caption dentro del enlace.
                    if not descripcion:
                        for selector in SELECTORES_CAPTION:
                            try:
                                loc = enlace.locator(selector).first
                                if loc.count():
                                    candidato = limpiar(
                                        loc.inner_text(timeout=1000)
                                    )
                                    if texto_util(candidato):
                                        descripcion = candidato
                                        break
                            except Exception:
                                continue

                    # 5) Último intento: texto del enlace (solo si hay palabras).
                    if not descripcion:
                        try:
                            candidato = limpiar(
                                enlace.inner_text(timeout=1000)
                            )
                            if texto_util(candidato):
                                descripcion = candidato
                        except Exception:
                            pass

                    videos.append({
                        "url": url_video,
                        "descripcion": descripcion,
                        "hashtags": info.get("hashtags") or hashtags_de(descripcion),
                    })

                except Exception:
                    continue

            # Videos que llegaron por la API pero no aparecieron como enlaces.
            for identificador, info in datos_api.items():
                if identificador in vistos:
                    continue
                vistos.add(identificador)
                videos.append({
                    "url": f"https://www.tiktok.com/@{USUARIO}/video/{identificador}",
                    "descripcion": info["descripcion"],
                    "hashtags": info["hashtags"] or hashtags_de(info["descripcion"]),
                })

            perfil["videos"] = videos[:MAX_VIDEOS]
            perfil["publicaciones_recopiladas"] = len(perfil["videos"])
            perfil["videos_con_texto_util"] = sum(
                texto_util(v["descripcion"]) for v in perfil["videos"]
            )

            SALIDA.write_text(
                json.dumps(perfil, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(f"\nResultado guardado en: {SALIDA}")
            print(f"Videos encontrados: {len(perfil['videos'])}")
            print(f"Videos con texto útil: {perfil['videos_con_texto_util']}")
            print(
                "Nota: los selectores y datos disponibles pueden variar "
                "según el diseño de TikTok."
            )

            if len(datos_api) == 0:
                print(
                    "\nAVISO: la API no devolvió datos. Puede haber captcha, "
                    "sesión caducada o un endpoint con otro nombre. "
                    "Revisa DevTools -> Network."
                )

            if perfil["videos_con_texto_util"] < 10:
                print(
                    "\nADVERTENCIA: hay menos de 10 videos con texto útil. "
                    "No ejecutes todavía el análisis Big Five."
                )
                print(
                    "Comprueba manualmente si las publicaciones tienen "
                    "descripciones o si TikTok las expone en la página."
                )

        finally:
            contexto.close()
            navegador.close()


if __name__ == "__main__":
    main()