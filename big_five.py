"""Análisis exploratorio de descripciones y hashtags con Gemini."""
import json
import os
import math
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


def normalizar_porcentajes(rasgos):
    """Convierte cinco puntuaciones relativas en porcentajes que suman 100."""
    puntuaciones = [r["puntuacion"] for r in rasgos]
    total = sum(puntuaciones)

    # Si no hay indicadores puntuados, asigna una distribución uniforme.
    if total == 0:
        for rasgo in rasgos:
            rasgo["puntuacion"] = 20
        return rasgos

    # Calcula los porcentajes exactos antes de redondearlos.
    exactos = [p * 100 / total for p in puntuaciones]

    # Toma primero la parte entera de cada porcentaje.
    porcentajes = [math.floor(p) for p in exactos]

    # Reparte los puntos que faltan según las mayores partes decimales.
    restantes = 100 - sum(porcentajes)
    orden = sorted(
        range(len(rasgos)),
        key=lambda i: exactos[i] - porcentajes[i],
        reverse=True
    )

    for i in orden[:restantes]:
        porcentajes[i] += 1

    # Guarda el porcentaje final en cada rasgo.
    for rasgo, porcentaje in zip(rasgos, porcentajes):
        rasgo["puntuacion"] = porcentaje

    return rasgos


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
dominios Big Five.

IMPORTANTE SOBRE LAS PUNTUACIONES:
- Asigna a cada rasgo un valor entero de 0 a 100 que represente su peso RELATIVO
  de indicadores textuales dentro de esta muestra.
- Estos valores son pesos iniciales; el programa los convertirá después en
  porcentajes cuya suma será exactamente 100.
- No es necesario que tus cinco valores iniciales sumen 100.
- No interpretes estos porcentajes como probabilidades ni como mediciones
  psicológicas reales.
- Si no hay evidencia suficiente para un rasgo, indícalo en confianza y
  explicación. No inventes evidencia ni confundas ausencia de datos con
  evidencia de ausencia.

Devuelve exactamente los cinco rasgos: apertura, responsabilidad, extraversion,
amabilidad y neuroticismo. Usa español para resumen, explicaciones, evidencias y
limitaciones. La confianza permitida es baja, muy baja o insuficiente.
Incluye referencias breves a los textos proporcionados, sin inventar citas.
Considera que la muestra es limitada y sesgada.

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

    # Validar que estén presentes exactamente los cinco rasgos.
    rasgos = resultado.get("rasgos", [])
    encontrados = [r.get("rasgo") for r in rasgos]

    if len(rasgos) != 5 or set(encontrados) != set(RASGOS):
        raise ValueError(
            "La respuesta de Gemini no contiene exactamente los cinco rasgos."
        )

    # Validar las puntuaciones iniciales antes de normalizarlas.
    for rasgo in rasgos:
        puntuacion = rasgo.get("puntuacion")
        if (
            not isinstance(puntuacion, int)
            or isinstance(puntuacion, bool)
            or not 0 <= puntuacion <= 100
        ):
            raise ValueError(
                "Gemini devolvió una puntuación fuera del rango 0-100."
            )

    # Convertir los pesos iniciales a porcentajes que suman exactamente 100.
    resultado["rasgos"] = normalizar_porcentajes(rasgos)

    # Comprobación adicional de la suma final.
    total_porcentajes = sum(
        r["puntuacion"] for r in resultado["rasgos"]
    )
    if total_porcentajes != 100:
        raise ValueError("Los porcentajes normalizados no suman 100.")

    return {
        "perfil": {
            "usuario": datos.get("usuario", ""),
            "url": datos.get("url", ""),
            "videos_analizados": len(material),
        },
        "metodologia": {
            "modelo": modelo,
            "tipo": "análisis exploratorio de descripciones y hashtags",
            "escala": "porcentajes relativos normalizados; suma total = 100%",
            "nota": (
                "Los porcentajes representan una distribución relativa de "
                "indicadores textuales y no una medición de personalidad."
            )
        },
        "big_five": resultado,
        "aviso": (
            "Este informe no determina la personalidad real de una persona ni "
            "constituye una evaluación o diagnóstico psicológico. Los "
            "porcentajes representan únicamente una distribución relativa de "
            "indicadores textuales limitados y pueden contener errores."
        )
    }