"""Lee resultado.json, calcula Big Five y Benford localmente y genera el informe."""

import json
from pathlib import Path

from big_five import (
    analizar_big_five,
    _buscar_videos,
    _obtener_texto,
)
from generar_informe import generar_informe


BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "resultado.json"
SALIDA_JSON = BASE / "resultado_big_five.json"
SALIDA_HTML = BASE / "informe_big_five.html"


def main():
    # 1. Comprobar que existe el archivo del scraper.
    if not ENTRADA.exists():
        raise FileNotFoundError(
            "No existe resultado.json. "
            "Ejecuta primero: python scraper_tiktok.py"
        )

    # 2. Leer el JSON.
    datos = json.loads(ENTRADA.read_text(encoding="utf-8"))

    if not isinstance(datos, (dict, list)):
        raise ValueError(
            "resultado.json debe contener un objeto JSON o una lista."
        )

    # 3. Localizar publicaciones y conservar las que tienen texto.
    videos = _buscar_videos(datos)

    utilizables = [
        video
        for video in videos
        if isinstance(video, dict) and _obtener_texto(video).strip()
    ]

    if len(utilizables) < 10:
        raise SystemExit(
            f"Solo hay {len(utilizables)} videos con texto útil. "
            "Se necesitan al menos 10. Revisa resultado.json."
        )

    # 4. Preparar los datos para el análisis local.
    # El scraper guarda los datos del perfil en el nivel superior del JSON
    # (usuario, url, nombre...). Si existe una clave "perfil", se usa esa.
    perfil = {}

    if isinstance(datos, dict):
        if isinstance(datos.get("perfil"), dict):
            perfil = datos["perfil"]
        else:
            perfil = {
                clave: datos[clave]
                for clave in (
                    "usuario", "url", "nombre", "biografia",
                    "seguidores", "seguidos", "me_gusta",
                )
                if clave in datos
            }

    datos_analisis = {
        "perfil": perfil,
        "videos": utilizables,
    }

    print(f"Videos con texto útil: {len(utilizables)}")
    print("Motor de análisis: Python local (sin Gemini)")
    print("No se necesita API key ni conexión a un modelo de IA.")

    # 5. Calcular Big Five, decisión de viaje y Benford.
    resultado = analizar_big_five(datos_analisis)

    # 6. Verificar que los cinco porcentajes sumen 100.
    rasgos = resultado["big_five"]["rasgos"]
    total_porcentajes = sum(
        rasgo["puntuacion"] for rasgo in rasgos
    )

    if len(rasgos) != 5 or total_porcentajes != 100:
        raise ValueError(
            "Los cinco rasgos deben sumar exactamente 100 %."
        )

    # 7. Guardar el resultado JSON.
    SALIDA_JSON.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nJSON generado: {SALIDA_JSON}")

    # 8. Generar el informe HTML.
    generar_informe(resultado, SALIDA_HTML)

    print(f"Informe HTML generado: {SALIDA_HTML}")

    # 9. Mostrar los porcentajes Big Five.
    print("\n=== BIG FIVE: PORCENTAJES RELATIVOS ===")

    for rasgo in rasgos:
        nombre = rasgo["rasgo"].replace("_", " ").capitalize()
        porcentaje = rasgo["puntuacion"]
        print(f"{nombre}: {porcentaje} %")

    print(f"TOTAL: {total_porcentajes} %")

    # 10. Mostrar si la persona quiere viajar (deducido del Big Five).
    viajes = resultado.get("interes_viajar", {})

    print("\n=== ¿QUIERE VIAJAR? (según el Big Five) ===")
    print(
        "Resultado:",
        str(viajes.get("interesado_en_viajar", "No disponible")).upper(),
    )
    print(
        "Índice:", viajes.get("indice", "N/D"),
        "| Umbral:", viajes.get("umbral", "N/D"),
    )
    print("Confianza:", viajes.get("confianza", "N/D"))
    print("Fórmula:", viajes.get("formula", "N/D"))
    print(viajes.get("explicacion", ""))

    # 11. Mostrar las métricas de Benford.
    print("\n=== LEY DE BENFORD ===")

    benford = resultado.get("benford", {})

    for metrica, analisis in benford.items():
        # metodologia y advertencia son textos, no objetos de métricas.
        if not isinstance(analisis, dict):
            continue

        cantidad = analisis.get("cantidad_datos", 0)
        mad = analisis.get("mad")

        print(
            f"{metrica}: {cantidad} datos válidos; MAD = {mad}"
        )

    print("\nProceso completado correctamente.")
    print("Abre informe_big_five.html en tu navegador.")
    print(
        "Aviso: el Big Five es una estimación basada en palabras clave, "
        "no una evaluación psicológica validada; la decisión de viaje es "
        "una heurística sobre esos porcentajes."
    )


if __name__ == "__main__":
    import traceback

    try:
        main()
    except Exception:
        traceback.print_exc()
        raise SystemExit("Error al ejecutar el análisis.")