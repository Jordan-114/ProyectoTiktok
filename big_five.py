"""Análisis exploratorio de TikTok: Big Five y Benford con Python local.

La decisión sobre si la persona quiere viajar se calcula ÚNICAMENTE a partir
de los porcentajes del Big Five (ya no se buscan palabras de viaje).
"""

import math
import re
import unicodedata
from collections import Counter


# ============================================================
# CONFIGURACIÓN
# ============================================================

RASGOS = [
    "apertura",
    "responsabilidad",
    "extraversion",
    "amabilidad",
    "neuroticismo",
]

# Cada rasgo tiene expresiones asociadas.
# El método cuenta evidencias textuales, no mide la personalidad real.
DICCIONARIO_RASGOS = {
    "apertura": [
        "aventura", "explorar", "descubrir", "viajar", "creatividad",
        "creativo", "arte", "musica", "aprender", "curiosidad",
        "experiencia nueva", "nuevo lugar", "naturaleza", "cultura",
        "innovacion", "imaginar", "fotografia", "conocer el mundo",
    ],
    "responsabilidad": [
        "objetivo", "meta", "disciplina", "organizacion", "organizado",
        "estudiar", "estudio", "trabajar", "esfuerzo", "constancia",
        "planificar", "planificacion", "puntualidad", "progreso",
        "ahorrar", "cumplir", "productividad", "emprender",
    ],
    "extraversion": [
        "amigos", "fiesta", "bailar", "celebrar", "diversion",
        "divertido", "social", "reunidos", "concierto", "compartir",
        "energia", "feliz", "salir", "conocer gente", "en vivo",
        "equipo", "familia", "reir",
    ],
    "amabilidad": [
        "ayudar", "apoyar", "gracias", "amistad", "amor",
        "familia", "respeto", "empatia", "solidaridad", "cuidar",
        "compartir", "bondad", "generosidad", "juntos", "te quiero",
        "agradecido", "amable", "perdon",
    ],
    "neuroticismo": [
        "estres", "ansiedad", "preocupacion", "preocupado",
        "triste", "tristeza", "miedo", "temor", "angustia",
        "inseguridad", "frustracion", "frustrado", "soledad",
        "agotado", "cansado", "llorar", "nervioso", "decepcion",
    ],
}

# Regla para decidir si la persona quiere viajar (solo con el Big Five).
# índice = PESO_APERTURA*apertura + PESO_EXTRAVERSION*extraversion
#          - PESO_NEUROTICISMO*neuroticismo
# Con un reparto neutro (20 % cada rasgo) el índice vale 20.
PESO_APERTURA = 1.0
PESO_EXTRAVERSION = 0.5
PESO_NEUROTICISMO = 0.5
UMBRAL_VIAJAR = 20.0

METRICAS_BENFORD = {
    "visualizaciones": [
        "visualizaciones", "views", "view_count", "play_count",
        "reproducciones", "vistas",
    ],
    "me_gusta": [
        "me_gusta", "likes", "like_count", "digg_count", "corazones",
    ],
    "comentarios": [
        "comentarios", "comments", "comment_count",
    ],
    "compartidos": [
        "compartidos", "shares", "share_count",
    ],
}


# ============================================================
# UTILIDADES PARA LEER LAS PUBLICACIONES
# ============================================================

def _normalizar_texto(texto):
    """Pasa a minúsculas y elimina tildes para comparar palabras."""
    texto = str(texto).lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return texto


def _buscar_videos(datos):
    """Encuentra las publicaciones en el JSON del scraper."""
    if isinstance(datos, list):
        return datos

    if not isinstance(datos, dict):
        return []

    for clave in (
        "videos", "publicaciones", "posts", "videos_extraidos",
        "publicaciones_extraidas", "items",
    ):
        valor = datos.get(clave)
        if isinstance(valor, list):
            return valor

    for clave in ("data", "resultado", "perfil"):
        valor = datos.get(clave)
        if isinstance(valor, dict):
            encontrados = _buscar_videos(valor)
            if encontrados:
                return encontrados

    return []


def _obtener_texto(video):
    """Extrae descripción y hashtags de una publicación."""
    if not isinstance(video, dict):
        return ""

    partes = []

    for clave in (
        "descripcion", "description", "texto",
        "caption", "desc", "title",
    ):
        valor = video.get(clave)
        if isinstance(valor, str) and valor.strip():
            partes.append(valor.strip())

    for clave in ("hashtags", "tags", "etiquetas"):
        valor = video.get(clave)

        if isinstance(valor, list):
            partes.extend(
                str(item).strip()
                for item in valor
                if str(item).strip()
            )
        elif isinstance(valor, str) and valor.strip():
            partes.append(valor.strip())

    return "\n".join(dict.fromkeys(partes))


def _obtener_perfil(datos):
    """Busca los datos del perfil, incluso si están anidados."""
    if not isinstance(datos, dict):
        return {}

    perfil = datos.get("perfil", {})
    return perfil if isinstance(perfil, dict) else {}


# ============================================================
# BIG FIVE: CÁLCULO LOCAL
# ============================================================

def _contar_evidencias(texto, palabras):
    """Cuenta las expresiones encontradas en un texto normalizado."""
    texto = _normalizar_texto(texto)
    evidencias = []

    for palabra in palabras:
        termino = _normalizar_texto(palabra)
        patron = r"(?<!\w)" + re.escape(termino) + r"(?!\w)"

        if re.search(patron, texto):
            evidencias.append(palabra)

    return evidencias


def _calcular_big_five(videos):
    """
    Calcula puntuaciones relativas a partir de evidencias textuales.

    Los porcentajes resultantes se normalizan para sumar exactamente 100.
    No son probabilidades ni puntuaciones psicométricas validadas.
    """
    textos = [
        _obtener_texto(video)
        for video in videos
        if _obtener_texto(video).strip()
    ]

    evidencias_por_rasgo = {rasgo: [] for rasgo in RASGOS}
    conteos = {rasgo: 0 for rasgo in RASGOS}

    for texto in textos:
        for rasgo, palabras in DICCIONARIO_RASGOS.items():
            encontradas = _contar_evidencias(texto, palabras)

            if encontradas:
                conteos[rasgo] += len(encontradas)
                evidencias_por_rasgo[rasgo].extend(encontradas)

    # Suavizado inicial: evita divisiones por cero cuando no hay señales.
    puntuaciones_base = {
        rasgo: 1 + conteos[rasgo]
        for rasgo in RASGOS
    }

    total = sum(puntuaciones_base.values())
    porcentajes_exactos = {
        rasgo: puntuaciones_base[rasgo] * 100 / total
        for rasgo in RASGOS
    }

    # Método de restos mayores: garantiza enteros cuya suma es 100.
    porcentajes = {
        rasgo: math.floor(porcentajes_exactos[rasgo])
        for rasgo in RASGOS
    }

    restantes = 100 - sum(porcentajes.values())
    orden = sorted(
        RASGOS,
        key=lambda rasgo: (
            porcentajes_exactos[rasgo] - porcentajes[rasgo]
        ),
        reverse=True,
    )

    for rasgo in orden[:restantes]:
        porcentajes[rasgo] += 1

    resultado_rasgos = []

    for rasgo in RASGOS:
        evidencias = list(dict.fromkeys(evidencias_por_rasgo[rasgo]))

        if evidencias:
            explicacion = (
                f"Se encontraron {conteos[rasgo]} coincidencias "
                "con el diccionario textual de este rasgo."
            )
        else:
            explicacion = (
                "No se encontraron coincidencias en el diccionario. "
                "Esto no significa que el rasgo esté ausente."
            )

        resultado_rasgos.append({
            "rasgo": rasgo,
            "puntuacion": porcentajes[rasgo],
            "evidencias": evidencias[:10],
            "coincidencias": conteos[rasgo],
            "explicacion": explicacion,
        })

    assert sum(
        rasgo["puntuacion"] for rasgo in resultado_rasgos
    ) == 100

    return {
        "resumen": (
            "Análisis exploratorio basado en reglas y palabras clave. "
            "Los porcentajes representan la distribución relativa de "
            "las señales detectadas entre los cinco rasgos."
        ),
        "rasgos": resultado_rasgos,
        "limitaciones": [
            "El método utiliza un diccionario de palabras y no comprende "
            "el contexto como lo haría un modelo de lenguaje.",
            "Una palabra puede aparecer en una broma, una cita o una "
            "negación y no representar al autor.",
            "La ausencia de palabras asociadas a un rasgo no demuestra "
            "que ese rasgo esté ausente.",
            "Los porcentajes suman 100 por normalización matemática; "
            "no son probabilidades ni una evaluación psicológica validada.",
        ],
        "metodo": "Diccionario de palabras clave y normalización relativa",
        "publicaciones_con_texto": len(textos),
    }


# ============================================================
# INTERÉS EN VIAJAR: DEDUCIDO ÚNICAMENTE DEL BIG FIVE
# ============================================================

def _interes_viajar_desde_big_five(big_five):
    """
    Decide si la persona querría viajar (sí / no) usando solo los
    porcentajes del Big Five.

    Regla: apertura y extraversión favorecen viajar; neuroticismo lo
    desfavorece. Es una heurística exploratoria, no una predicción real.
    """
    rasgos = big_five.get("rasgos", [])

    porcentajes = {
        r["rasgo"]: r["puntuacion"]
        for r in rasgos
        if isinstance(r, dict) and "rasgo" in r
    }
    coincidencias_totales = sum(
        r.get("coincidencias", 0)
        for r in rasgos
        if isinstance(r, dict)
    )

    apertura = porcentajes.get("apertura", 20)
    extraversion = porcentajes.get("extraversion", 20)
    neuroticismo = porcentajes.get("neuroticismo", 20)

    indice = (
        PESO_APERTURA * apertura
        + PESO_EXTRAVERSION * extraversion
        - PESO_NEUROTICISMO * neuroticismo
    )
    distancia = indice - UMBRAL_VIAJAR

    quiere_viajar = "sí" if distancia > 0 else "no"

    # Confianza: depende de lo lejos que está del umbral y de cuántas
    # señales de texto respaldan los porcentajes.
    if coincidencias_totales < 5:
        confianza = "baja"
    elif abs(distancia) >= 15:
        confianza = "alta"
    elif abs(distancia) >= 5:
        confianza = "media"
    else:
        confianza = "baja"

    if quiere_viajar == "sí":
        explicacion = (
            f"El índice de viaje ({indice:.1f}) supera el umbral "
            f"({UMBRAL_VIAJAR:.0f}). Pesan a favor la apertura "
            f"({apertura} %) y la extraversión ({extraversion} %), "
            f"frente al neuroticismo ({neuroticismo} %)."
        )
    else:
        explicacion = (
            f"El índice de viaje ({indice:.1f}) no supera el umbral "
            f"({UMBRAL_VIAJAR:.0f}). La apertura ({apertura} %) y la "
            f"extraversión ({extraversion} %) no compensan el "
            f"neuroticismo ({neuroticismo} %)."
        )

    if confianza == "baja":
        explicacion += (
            " La confianza es baja: hay pocas coincidencias de texto "
            "o el resultado está muy cerca del umbral."
        )

    return {
        "interesado_en_viajar": quiere_viajar,
        "indice": round(indice, 2),
        "umbral": UMBRAL_VIAJAR,
        "confianza": confianza,
        "porcentajes_usados": {
            "apertura": apertura,
            "extraversion": extraversion,
            "neuroticismo": neuroticismo,
        },
        "formula": (
            f"{PESO_APERTURA}×apertura + {PESO_EXTRAVERSION}×extraversión "
            f"- {PESO_NEUROTICISMO}×neuroticismo"
        ),
        "explicacion": explicacion,
        "metodo": "Regla heurística aplicada solo a los porcentajes Big Five",
    }


# ============================================================
# LEY DE BENFORD: CÁLCULO LOCAL
# ============================================================

def _a_numero(valor):
    if isinstance(valor, bool) or valor is None:
        return None

    if isinstance(valor, (int, float)):
        numero = float(valor)
    elif isinstance(valor, str):
        try:
            numero = float(valor.strip().replace(",", ""))
        except ValueError:
            return None
    else:
        return None

    if not math.isfinite(numero) or numero <= 0:
        return None

    return numero


def _primer_digito(numero):
    for caracter in format(numero, ".15g"):
        if caracter in "123456789":
            return int(caracter)
    return None


def _obtener_valor(video, claves):
    if not isinstance(video, dict):
        return None

    contenedores = [video]

    for clave in ("stats", "statistics", "metricas", "metrics"):
        subdatos = video.get(clave)
        if isinstance(subdatos, dict):
            contenedores.append(subdatos)

    for contenedor in contenedores:
        for clave in claves:
            if clave in contenedor:
                numero = _a_numero(contenedor[clave])
                if numero is not None:
                    return numero

    return None


def _analizar_benford_valores(valores):
    digitos = []

    for valor in valores:
        numero = _a_numero(valor)
        if numero is not None:
            digito = _primer_digito(numero)
            if digito is not None:
                digitos.append(digito)

    cantidad = len(digitos)

    if cantidad == 0:
        return {
            "cantidad_datos": 0,
            "frecuencias": [],
            "mad": None,
            "interpretacion": "No hay valores positivos válidos.",
        }

    conteo = Counter(digitos)
    filas = []

    for digito in range(1, 10):
        observada = conteo.get(digito, 0) / cantidad
        esperada = math.log10(1 + 1 / digito)

        filas.append({
            "digito": digito,
            "cantidad_observada": conteo.get(digito, 0),
            "frecuencia_observada": round(observada, 6),
            "frecuencia_esperada": round(esperada, 6),
            "diferencia_absoluta": round(
                abs(observada - esperada), 6
            ),
        })

    mad = sum(
        fila["diferencia_absoluta"] for fila in filas
    ) / 9

    if cantidad < 100:
        interpretacion = (
            "Muestra pequeña: las frecuencias pueden variar mucho. "
            "No permite conclusiones sólidas."
        )
    else:
        interpretacion = (
            "Comparación descriptiva con la distribución teórica. "
            "Una desviación no demuestra fraude ni manipulación."
        )

    return {
        "cantidad_datos": cantidad,
        "frecuencias": filas,
        "mad": round(mad, 6),
        "interpretacion": interpretacion,
    }


def analizar_metricas_tiktok(videos):
    """Analiza métricas numéricas localmente con la ley de Benford."""
    resultados = {}

    for nombre, claves in METRICAS_BENFORD.items():
        valores = [
            valor
            for video in videos
            if (valor := _obtener_valor(video, claves)) is not None
        ]
        resultados[nombre] = _analizar_benford_valores(valores)

    resultados["metodologia"] = (
        "Se compara el primer dígito significativo de cada métrica "
        "positiva con la distribución teórica de Benford."
    )
    resultados["advertencia"] = (
        "Las métricas de TikTok no necesariamente siguen la ley "
        "de Benford. Los resultados son exploratorios."
    )

    return resultados


# ============================================================
# FUNCIÓN PRINCIPAL: TODO LOCAL, SIN GEMINI
# ============================================================

def analizar_big_five(datos):
    """Analiza Big Five, viajes (derivado) y Benford sin servicios externos."""
    print("[1/3] Leyendo publicaciones...", flush=True)

    videos = _buscar_videos(datos)
    perfil = _obtener_perfil(datos)

    if not videos:
        raise ValueError(
            "No se encontraron publicaciones en resultado.json."
        )

    videos_con_texto = [
        video for video in videos if _obtener_texto(video).strip()
    ]

    if not videos_con_texto:
        raise ValueError(
            "No hay descripciones ni hashtags útiles. "
            "Comprueba el contenido de resultado.json."
        )

    print(
        f"Publicaciones encontradas: {len(videos)}; "
        f"con texto: {len(videos_con_texto)}",
        flush=True,
    )

    print("[2/3] Calculando Big Five y decisión de viaje...", flush=True)
    big_five = _calcular_big_five(videos)
    viajes = _interes_viajar_desde_big_five(big_five)

    print("[3/3] Calculando métricas de Benford...", flush=True)
    benford = analizar_metricas_tiktok(videos)

    nombre = (
        perfil.get("nombre")
        or perfil.get("nickname")
        or perfil.get("nombre_usuario")
        or perfil.get("username")
        or perfil.get("usuario")
        or "Perfil público"
    )

    return {
        "perfil": {
            **perfil,
            "nombre": nombre,
            "videos_analizados": len(videos),
            "videos_con_texto_util": len(videos_con_texto),
            "modelo": "Python local (sin IA externa)",
        },
        "metodologia": (
            "Big Five: reglas y palabras clave ejecutadas localmente en "
            "Python (los cinco porcentajes suman exactamente 100 %). "
            "Interés en viajar: regla heurística aplicada únicamente a "
            "los porcentajes del Big Five. Benford: cálculo estadístico "
            "local."
        ),
        "big_five": big_five,
        "interes_viajar": viajes,
        "benford": benford,
        "aviso": (
            "Este informe es exploratorio y no determina la personalidad "
            "real ni las preferencias de una persona. Las palabras pueden "
            "depender del contexto y las métricas no demuestran fraude."
        ),
    }


# Compatibilidad temporal con nombres antiguos. Ya NO llama a Gemini.
def analizar_con_gemini(datos):
    return analizar_big_five(datos)