
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

USUARIO = "jordanguaicha9"  # Cambia esto por el usuario público, sin @

BASE = Path(__file__).resolve().parent
SESION = BASE / "tiktok_state.json"
SALIDA = BASE / "resultado.json"


def extraer_datos():
    if not SESION.exists():
        print("Error: no se encontró tiktok_state.json.")
        return

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context(
            storage_state=str(SESION)
        )
        pagina = contexto.new_page()

        url = f"https://www.tiktok.com/@{USUARIO}"
        print(f"Abriendo: {url}")

        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        pagina.wait_for_timeout(5000)

        # Busca los datos públicos que TikTok pueda incluir
        # en el HTML inicial de la página.
        html = pagina.content()
        coincidencia = re.search(
            r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"'
            r'[^>]*>(.*?)</script>',
            html,
            re.DOTALL
        )

        if not coincidencia:
            print("No se encontraron los datos estructurados.")
            print("Comprueba si el perfil se muestra completo.")
            navegador.close()
            return

        try:
            datos = json.loads(coincidencia.group(1))
            alcance = datos.get("__DEFAULT_SCOPE__", {})
            detalle = alcance.get("webapp.user-detail", {})
            usuario = detalle.get("userInfo", {})

            perfil = usuario.get("user", {})
            estadisticas = usuario.get("stats", {})

            if not perfil:
                print("TikTok no proporcionó los datos del perfil.")
                navegador.close()
                return

            resultado = {
                "usuario": perfil.get("uniqueId"),
                "nombre": perfil.get("nickname"),
                "biografia": perfil.get("signature"),
                "verificado": perfil.get("verified"),
                "seguidores": estadisticas.get("followerCount"),
                "seguidos": estadisticas.get("followingCount"),
                "me_gusta": estadisticas.get("heartCount"),
                "publicaciones": estadisticas.get("videoCount"),
                "url": url
            }

            SALIDA.write_text(
                json.dumps(resultado, ensure_ascii=False, indent=4),
                encoding="utf-8"
            )

            print("\nDatos extraídos:")
            print(json.dumps(resultado, ensure_ascii=False, indent=4))
            print(f"\nArchivo guardado en: {SALIDA}")

        except (json.JSONDecodeError, AttributeError, TypeError) as error:
            print(f"No se pudieron interpretar los datos: {error}")

        finally:
            navegador.close()


if __name__ == "__main__":
    extraer_datos()
