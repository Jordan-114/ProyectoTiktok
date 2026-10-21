
from pathlib import Path
from playwright.sync_api import sync_playwright

CARPETA = Path(__file__).resolve().parent
ARCHIVO_SESION = CARPETA / "tiktok_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto(
            "https://www.tiktok.com/login",
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("1. Inicia sesión manualmente en el navegador.")
        print("2. Comprueba que TikTok haya abierto tu cuenta.")
        input("3. Cuando termines, vuelve aquí y pulsa ENTER: ")

        context.storage_state(path=str(ARCHIVO_SESION))
        print(f"Estado de sesión guardado en: {ARCHIVO_SESION}")

    finally:
        browser.close()
