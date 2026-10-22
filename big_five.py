"""Análisis exploratorio de descripciones y hashtags con Gemini."""
import json
import os
from google import genai

RASGOS = [
    "apertura",
    "responsabilidad",
    "extraversion",
    "amabilidad",
    "neuroticismo",
]

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "resumen": {"type": "STRING"},
        "rasgos": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "rasgo": {
                        "type": "STRING",
                        "enum": RASGOS
                    },
                    "puntuacion": {"type": "INTEGER"},
                    "confianza": {
                        "type": "STRING",
                        "enum": ["baja", "muy baja", "insuficiente"]
                    },
                    "evidencias": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "explicacion": {"type": "STRING"}
                },
                "required": [
                    "rasgo", "puntuacion", "confianza",
                    "evidencias", "explicacion"
                ]
            }
        },
        "limitaciones": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        }
    },
    "required": ["resumen", "rasgos", "limitaciones"]
}

def analizar_con_gemini(datos):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY. Configúrala en PowerShell antes de ejecutar."
        )

    videos = datos.get("videos", [])
    if len(videos) < 10:
        raise ValueError(
            f"Se necesitan al menos 10 videos con datos recopilados; solo hay {len(videos)}."
        )

    material = []
    for i, video in enumerate(videos[:30], start=1):
        material.append({
            "video": i,
            "descripcion": str(video.get("descripcion", ""))[:1500],
            "hashtags": video.get("hashtags", []),
            "url": video.get("url", "")
        })

    prompt = f"""
Eres un asistente de investigación académica que analiza textos públicos.
Evalúa únicamente indicadores lingüísticos observables en las descripciones y
hashtags suministrados. No afirmes conocer la personalidad real de la persona.
No hagas diagnósticos ni infieras salud mental, identidad, religión, política,
orientación sexual u otros atributos sensibles. Los contenidos pueden ser
actuación, humor, marketing o estar escritos por otra persona.

Tarea: producir una interpretación EXPLORATORIA y no validada de los cinco
dominios Big Five. Una puntuación de 0 a 100 solo representa la presencia
relativa de indicadores textuales en esta muestra, no una medición psicológica.
No interpretes ausencia de evidencia como evidencia de un rasgo. Si la evidencia
es insuficiente, usa confianza "insuficiente", explica por qué y evita conclusiones
firmes. Incluye en evidencias referencias breves a los textos proporcionados;
no inventes citas. Considera la muestra limitada y sesgada.

Devuelve exactamente los cinco rasgos: apertura, responsabilidad, extraversion,
amabilidad y neuroticismo. Usa español para resumen, explicaciones, evidencias y
limitaciones. No atribuyas puntuaciones altas o bajas sin evidencia textual
concreta. La confianza permitida es baja, muy baja o insuficiente.

Datos del perfil (solo para contexto; no uses métricas sociales como prueba de
personalidad):
{json.dumps({"usuario": datos.get("usuario"), "videos": material}, ensure_ascii=False)}
"""

    client = genai.Client(api_key=api_key)
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    respuesta = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SCHEMA,
            "temperature": 0.2,
        },
    )

    if not respuesta.text:
        raise RuntimeError("Gemini no devolvió contenido.")
    resultado = json.loads(respuesta.text)

    # Validaciones básicas para evitar informes incompletos o fuera de rango.
    encontrados = {r.get("rasgo") for r in resultado.get("rasgos", [])}
    if set(RASGOS) != encontrados:
        raise ValueError("La respuesta de Gemini no contiene exactamente los cinco rasgos.")
    for rasgo in resultado["rasgos"]:
        puntuacion = rasgo.get("puntuacion")
        if not isinstance(puntuacion, int) or not 0 <= puntuacion <= 100:
            raise ValueError("Gemini devolvió una puntuación fuera del rango 0-100.")

    return {
        "perfil": {
            "usuario": datos.get("usuario", ""),
            "url": datos.get("url", ""),
            "videos_analizados": len(material),
        },
        "metodologia": {
            "modelo": modelo,
            "tipo": "análisis exploratorio de descripciones y hashtags",
            "escala": "0-100; no es una prueba psicométrica validada"
        },
        "big_five": resultado,
        "aviso": (
            "Este informe no determina la personalidad real de una persona ni "
            "constituye una evaluación o diagnóstico psicológico. Solo resume "
            "indicadores textuales limitados y puede contener errores."
        )
    }
