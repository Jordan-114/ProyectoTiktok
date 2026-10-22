"""Lee resultado.json, analiza con Gemini y genera JSON e informe HTML."""
import json
from pathlib import Path
from big_five import analizar_con_gemini
from generar_informe import generar_informe

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "resultado.json"
SALIDA_JSON = BASE / "resultado_big_five.json"
SALIDA_HTML = BASE / "informe_big_five.html"

def main():
    if not ENTRADA.exists():
        raise FileNotFoundError(
            "No existe resultado.json. Ejecuta primero: python scrapear.py"
        )

    datos = json.loads(ENTRADA.read_text(encoding="utf-8"))
    videos = datos.get("videos", [])
    # Contar solo videos con descripción o hashtags utilizables.
    utilizables = [
        v for v in videos
        if str(v.get("descripcion", "")).strip()
        or v.get("hashtags")
    ]
    if len(utilizables) < 10:
        raise SystemExit(
            f"Solo hay {len(utilizables)} videos con descripción/hashtags. "
            "Se necesitan al menos 10. Revisa resultado.json o vuelve a ejecutar "
            "el scraper; no se generará un análisis incompleto."
        )
    datos["videos"] = utilizables

    print(f"Analizando {min(len(utilizables), 30)} videos con Gemini...")
    resultado = analizar_con_gemini(datos)
    SALIDA_JSON.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    generar_informe(resultado, SALIDA_HTML)
    print(f"JSON generado: {SALIDA_JSON}")
    print(f"Informe HTML generado: {SALIDA_HTML}")
    print("Abre el HTML en tu navegador para ver el informe.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Error: {exc}")
