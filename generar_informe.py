"""Genera un informe HTML local de Big Five, decisión de viaje y ley de Benford."""

import html
import math
from pathlib import Path

NOMBRES = {
    "apertura": "Apertura a la experiencia",
    "responsabilidad": "Responsabilidad",
    "extraversion": "Extraversión",
    "amabilidad": "Amabilidad",
    "neuroticismo": "Neuroticismo",
}


def seguro_texto(valor, predeterminado="No disponible"):
    """Convierte cualquier valor en texto HTML seguro."""
    if valor is None:
        valor = predeterminado
    return html.escape(str(valor))


def generar_seccion_benford(benford):
    if not isinstance(benford, dict):
        return "<section><h2>Ley de Benford</h2><p>Sin resultados disponibles.</p></section>"

    secciones = []

    for metrica, resultado in benford.items():
        # La estructura incluye textos de metodología o avisos.
        if not isinstance(resultado, dict):
            continue

        nombre = seguro_texto(metrica.replace("_", " ").capitalize())
        total = resultado.get(
            "cantidad_datos",
            resultado.get("cantidad_datos_validos", 0),
        )
        mad = resultado.get("mad", resultado.get("desviacion_mad"))
        interpretacion = seguro_texto(
            resultado.get("interpretacion", "Sin interpretación.")
        )

        frecuencias = resultado.get("frecuencias", [])
        filas = []
        barras = []

        if isinstance(frecuencias, list):
            for dato in frecuencias:
                if not isinstance(dato, dict):
                    continue

                digito = dato.get("digito", "")
                observada = dato.get(
                    "frecuencia_observada",
                    dato.get("observada", 0),
                )
                esperada = dato.get(
                    "frecuencia_esperada",
                    dato.get("esperada", 0),
                )
                cantidad = dato.get(
                    "cantidad_observada",
                    dato.get("cantidad", 0),
                )

                try:
                    observada = float(observada)
                    esperada = float(esperada)
                except (ValueError, TypeError):
                    continue

                if not math.isfinite(observada):
                    observada = 0.0
                if not math.isfinite(esperada):
                    esperada = 0.0

                # big_five.py guarda fracciones (0 a 1); se convierten a %.
                # El formato antiguo (benford.py) ya venía en porcentaje.
                if "cantidad_observada" in dato:
                    observada *= 100
                    esperada *= 100

                obs_css = max(0, min(100, observada))
                esp_css = max(0, min(100, esperada))

                filas.append(
                    f"<tr><td>{seguro_texto(digito)}</td>"
                    f"<td>{observada:.2f}%</td>"
                    f"<td>{esperada:.2f}%</td>"
                    f"<td>{seguro_texto(cantidad)}</td></tr>"
                )

                barras.append(f"""
                    <div class="benford-row">
                        <strong>Dígito {seguro_texto(digito)}</strong>
                        <div>
                            <p>Observada: {observada:.2f}%</p>
                            <div class="track"><div class="fill"
                                style="width:{obs_css:.2f}%"></div></div>
                            <p>Esperada: {esperada:.2f}%</p>
                            <div class="track"><div class="expected-fill"
                                style="width:{esp_css:.2f}%"></div></div>
                        </div>
                    </div>
                """)

        try:
            mad_texto = f"{float(mad):.5f}" if mad is not None else "No disponible"
        except (ValueError, TypeError, OverflowError):
            mad_texto = "No disponible"

        tabla = "".join(filas) or (
            '<tr><td colspan="4">No hay frecuencias disponibles.</td></tr>'
        )

        secciones.append(f"""
            <section>
                <h2>Benford: {nombre}</h2>
                <div class="stats">
                    <div class="stat-card">
                        <span>Datos analizados</span>
                        <strong>{seguro_texto(total)}</strong>
                    </div>
                    <div class="stat-card">
                        <span>Desviación MAD</span>
                        <strong>{seguro_texto(mad_texto)}</strong>
                    </div>
                </div>
                <h3>Distribución del primer dígito</h3>
                {"".join(barras) or "<p>No hay datos suficientes para el gráfico.</p>"}
                <h3>Tabla de frecuencias</h3>
                <div class="tablewrap">
                    <table>
                        <thead><tr><th>Dígito</th><th>Observada</th>
                        <th>Esperada</th><th>Cantidad</th></tr></thead>
                        <tbody>{tabla}</tbody>
                    </table>
                </div>
                <h3>Interpretación</h3>
                <p>{interpretacion}</p>
            </section>
        """)

    aviso = benford.get("advertencia")
    if aviso:
        secciones.append(
            f'<section><h2>Advertencia sobre Benford</h2><p>{seguro_texto(aviso)}</p></section>'
        )

    return "".join(secciones) or """
        <section>
            <h2>Ley de Benford</h2>
            <p>No hay métricas disponibles para mostrar.</p>
        </section>
    """


def generar_seccion_viajes(viajes):
    """Sección '¿Quiere viajar?' deducida únicamente del Big Five."""
    if not isinstance(viajes, dict):
        viajes = {}

    resultado = str(viajes.get("interesado_en_viajar", "indeterminado"))
    resultado_texto = seguro_texto(resultado.upper())
    confianza = seguro_texto(viajes.get("confianza", "No disponible"))
    explicacion = seguro_texto(
        viajes.get("explicacion", "No hay una explicación disponible.")
    )
    formula = seguro_texto(viajes.get("formula", "No disponible"))
    metodo = seguro_texto(viajes.get("metodo", "Regla heurística sobre el Big Five"))

    try:
        indice = f"{float(viajes.get('indice')):.1f}"
    except (ValueError, TypeError):
        indice = "No disponible"

    try:
        umbral = f"{float(viajes.get('umbral')):.0f}"
    except (ValueError, TypeError):
        umbral = "No disponible"

    usados = viajes.get("porcentajes_usados", {})
    if not isinstance(usados, dict):
        usados = {}

    lista_usados = "".join(
        f"<li>{seguro_texto(NOMBRES.get(k, k))}: {seguro_texto(v)}%</li>"
        for k, v in usados.items()
    ) or "<li>No disponible.</li>"

    return f"""
<section>
<h2>¿La persona quiere viajar? (según el Big Five)</h2>
<div class="stats">
<div class="stat-card"><span>Resultado</span><strong>{resultado_texto}</strong></div>
<div class="stat-card"><span>Índice de viaje</span><strong>{seguro_texto(indice)}</strong></div>
<div class="stat-card"><span>Umbral</span><strong>{seguro_texto(umbral)}</strong></div>
<div class="stat-card"><span>Confianza</span><strong>{confianza}</strong></div>
</div>
<p>{explicacion}</p>
<h3>Porcentajes del Big Five utilizados</h3>
<ul>{lista_usados}</ul>
<p class="meta">Fórmula: {formula}</p>
<p class="meta">Método: {metodo}. Este resultado es una heurística sobre los porcentajes del Big Five; no confirma los intereses reales de la persona.</p>
</section>
"""


def generar_informe(datos, destino):
    """Construye el informe HTML a partir del análisis local."""

    big = datos.get("big_five", {})
    if not isinstance(big, dict):
        big = {}

    rasgos = big.get("rasgos", [])
    if not isinstance(rasgos, list):
        rasgos = []

    filas = []
    barras = []

    for rasgo in rasgos:
        if not isinstance(rasgo, dict):
            continue

        clave = str(rasgo.get("rasgo", ""))
        nombre = NOMBRES.get(clave, clave.capitalize() or "Rasgo")

        try:
            puntuacion = int(rasgo.get("puntuacion", 0))
        except (ValueError, TypeError, OverflowError):
            puntuacion = 0

        puntuacion_visual = max(0, min(100, puntuacion))
        explicacion = seguro_texto(rasgo.get("explicacion", ""))
        coincidencias = seguro_texto(rasgo.get("coincidencias", 0))
        evidencias = rasgo.get("evidencias", [])

        if not isinstance(evidencias, list):
            evidencias = []

        lista_evidencias = "".join(
            f"<li>{seguro_texto(evidencia)}</li>"
            for evidencia in evidencias
        ) or "<li>No se encontraron evidencias textuales concretas.</li>"

        filas.append(f"""
            <tr>
                <td>{seguro_texto(nombre)}</td>
                <td><strong>{puntuacion}%</strong></td>
                <td>{explicacion}<br>
                    <span class="meta">Coincidencias: {coincidencias}</span>
                    <ul>{lista_evidencias}</ul>
                </td>
            </tr>
        """)

        barras.append(f"""
            <div class="barrow">
                <span>{seguro_texto(nombre)}</span>
                <div class="track">
                    <div class="fill" style="width:{puntuacion_visual}%"></div>
                </div>
                <strong>{puntuacion}%</strong>
            </div>
        """)

    suma = sum(
        int(r.get("puntuacion", 0))
        for r in rasgos
        if isinstance(r, dict)
        and str(r.get("puntuacion", "")).lstrip("-").isdigit()
    )

    limitaciones = big.get("limitaciones", [])
    if isinstance(limitaciones, str):
        limitaciones = [limitaciones]
    if not isinstance(limitaciones, list):
        limitaciones = []

    lista_limitaciones = "".join(
        f"<li>{seguro_texto(item)}</li>" for item in limitaciones
    )

    perfil = datos.get("perfil", {})
    if not isinstance(perfil, dict):
        perfil = {}

    metodologia = datos.get("metodologia", {})
    if isinstance(metodologia, dict):
        modelo = metodologia.get("modelo", "Python local")
    elif isinstance(metodologia, str):
        modelo = metodologia
    else:
        modelo = "Python local"

    modelo = seguro_texto(modelo)
    usuario = seguro_texto(
        perfil.get("usuario", perfil.get("nombre", "No indicado"))
    )
    url_original = str(perfil.get("url") or "")
    url = html.escape(url_original, quote=True)
    videos = seguro_texto(
        perfil.get("videos_analizados", datos.get("videos_analizados", 0))
    )
    aviso = seguro_texto(datos.get(
        "aviso",
        "Este informe es exploratorio y no constituye una evaluación psicológica.",
    ))
    resumen = seguro_texto(big.get("resumen", "Análisis realizado localmente mediante reglas y palabras clave."))

    if url_original.startswith(("https://", "http://")):
        perfil_html = (
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        )
    else:
        perfil_html = "No disponible"

    viajes_html = generar_seccion_viajes(datos.get("interes_viajar", {}))
    benford_html = generar_seccion_benford(datos.get("benford", {}))

    documento = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Informe Big Five y ley de Benford</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: Arial, sans-serif; margin: 0; background: #f3f5f8;
       color: #202938; line-height: 1.6; }}
main {{ max-width: 1050px; margin: 32px auto; padding: 0 18px; }}
header, section {{ background: white; padding: 24px; border-radius: 14px;
                  margin-bottom: 18px; box-shadow: 0 3px 16px #1720330c; }}
h1 {{ margin-top: 0; line-height: 1.3; }}
h2 {{ margin-top: 0; font-size: 1.3rem; }}
.meta {{ color: #526174; overflow-wrap: anywhere; }}
.warning {{ border-left: 5px solid #d97706; background: #fff7e6;
            padding: 14px; border-radius: 6px; }}
.barrow {{ display: grid; grid-template-columns: 220px 1fr 45px; gap: 12px;
           align-items: center; margin: 16px 0; }}
.track {{ height: 15px; border-radius: 20px; background: #e4e9f0; overflow: hidden; }}
.fill {{ height: 100%; background: #4776d0; border-radius: 20px; }}
.expected-fill {{ height: 100%; background: #e3a343; border-radius: 20px; }}
.tablewrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; min-width: 520px; }}
th, td {{ border-bottom: 1px solid #e3e7ed; text-align: left; padding: 12px; vertical-align: top; }}
th {{ background: #f7f8fa; }}
li {{ margin-bottom: 5px; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 14px; margin: 18px 0; }}
.stat-card {{ background: #f5f7fb; border: 1px solid #e3e7ed; border-radius: 10px;
              padding: 14px 18px; min-width: 160px; display: flex; flex-direction: column; gap: 5px; }}
.stat-card strong {{ font-size: 1.35rem; overflow-wrap: anywhere; }}
.benford-row {{ display: grid; grid-template-columns: 100px 1fr; gap: 12px; margin: 20px 0; }}
footer {{ color: #637083; font-size: .9rem; padding: 10px 2px 28px; }}
@media(max-width:650px) {{
 main {{ margin: 16px auto; padding: 0 10px; }}
 header, section {{ padding: 18px; }}
 .barrow {{ grid-template-columns: 1fr 45px; }}
 .barrow span {{ grid-column: 1 / -1; }}
 .benford-row {{ grid-template-columns: 1fr; }}
}}
@media print {{
 body {{ background: white; }} main {{ max-width: none; margin: 0; }}
 header, section {{ box-shadow: none; border: 1px solid #ddd; break-inside: avoid; }}
}}
</style>
</head>
<body><main>
<header>
<h1>Informe exploratorio: Big Five y ley de Benford</h1>
<p class="meta">Perfil: <strong>{usuario}</strong> · Videos analizados: {videos} · Motor: {modelo}</p>
<p>Perfil público consultado: {perfil_html}</p>
<div class="warning"><strong>Importante:</strong> {aviso}</div>
</header>

<section>
<h2>Resumen del análisis local</h2>
<p>{resumen}</p>
<p class="meta">Se procesaron textos mediante reglas y un diccionario de palabras clave. No se usó Gemini ni una API externa.</p>
</section>

<section>
<h2>Big Five: distribución relativa</h2>
<p class="meta">Los cinco porcentajes suman {suma}%. Son proporciones de indicadores textuales detectados, no puntuaciones psicológicas validadas.</p>
{"".join(barras) or "<p>No hay rasgos disponibles.</p>"}
</section>

{viajes_html}

<section>
<h2>Resultados y evidencias textuales</h2>
<div class="tablewrap"><table>
<thead><tr><th>Rasgo</th><th>Porcentaje</th><th>Interpretación y evidencias</th></tr></thead>
<tbody>{"".join(filas) or '<tr><td colspan="3">No hay resultados.</td></tr>'}</tbody>
</table></div>
</section>

{benford_html}

<section>
<h2>Limitaciones del análisis</h2>
<ul>
{lista_limitaciones}
<li>El Big Five se estima mediante palabras clave y reglas locales; no es una prueba psicométrica validada.</li>
<li>La decisión de viajar es una regla heurística sobre esos porcentajes; no predice el comportamiento real.</li>
<li>Los textos pueden ser humorísticos, promocionales o estar escritos por terceros.</li>
<li>Los resultados dependen de las descripciones y hashtags disponibles.</li>
<li>La ley de Benford solo es apropiada para ciertos conjuntos de datos numéricos; las métricas de TikTok podrían no cumplir sus condiciones.</li>
<li>Una desviación de Benford no demuestra fraude ni manipulación.</li>
<li>No se debe utilizar este informe para diagnosticar ni etiquetar a una persona.</li>
</ul>
</section>

<footer>Generado localmente por ProyectoTiktok. Informe exploratorio para fines académicos.</footer>
</main></body></html>
"""

    Path(destino).write_text(documento, encoding="utf-8")