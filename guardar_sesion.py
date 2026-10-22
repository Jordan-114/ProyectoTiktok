"""Guarda el estado local de sesión de Chromium para uso personal."""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
SALIDA = BASE / "tiktok_state.json"

def main():
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        contexto = navegador.new_context()
        pagina = contexto.new_page()
        pagina.goto("https://www.tiktok.com/login", wait_until="domcontentloaded")
        print("Inicia sesión manualmente si es necesario.")
        print("No automatices ni intentes eludir controles de seguridad.")
        input("Cuando termines y veas TikTok, vuelve aquí y presiona ENTER...")
        contexto.storage_state(path=str(SALIDA))
        contexto.close()
        navegador.close()
    print(f"Sesión guardada localmente en: {SALIDA}")
    print("No compartas este archivo ni lo subas a GitHub.")

if __name__ == "__main__":
    main()
