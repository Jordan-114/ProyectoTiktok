"""Genera un informe HTML autónomo con tabla y barras Big Five."""
import html
from pathlib import Path

NOMBRES = {
    "apertura": "Apertura a la experiencia",
    "responsabilidad": "Responsabilidad",
    "extraversion": "Extraversión",
    "amabilidad": "Amabilidad",
    "neuroticismo": "Neuroticismo",
}

def generar_informe(datos, destino):
    big = datos.get("big_five", {})
    rasgos = big.get("rasgos", [])
    filas = []
    barras = []

    for r in rasgos:
        nombre = NOMBRES.get(r.get("rasgo"), r.get("rasgo", "Rasgo"))
        puntuacion = int(r.get("puntuacion", 0))
        confianza = html.escape(str(r.get("confianza", "insuficiente")))
        explicacion = html.escape(str(r.get("explicacion", "")))
        evidencias = "".join(
            f"<li>{html.escape(str(e))}</li>" for e in r.get("evidencias", [])
        ) or "<li>No se aportaron evidencias concretas.</li>"
        filas.append(
            f"<tr><td>{html.escape(nombre)}</td><td>{puntuacion}/100</td>"
            f"<td>{confianza}</td><td>{explicacion}<ul>{evidencias}</ul></td></tr>"
        )
        barras.append(
            f'<div class="barrow"><span>{html.escape(nombre)}</span>'
            f'<div class="track"><div class="fill" style="width:{puntuacion}%"></div></div>'
            f'<strong>{puntuacion}</strong></div>'
        )

    limitaciones = "".join(
        f"<li>{html.escape(str(x))}</li>" for x in big.get("limitaciones", [])
    )
    usuario = html.escape(str(datos.get("perfil", {}).get("usuario", "No indicado")))
    url = html.escape(str(datos.get("perfil", {}).get("url", "")), quote=True)
    modelo = html.escape(str(datos.get("metodologia", {}).get("modelo", "")))
    resumen = html.escape(str(big.get("resumen", "")))
    aviso = html.escape(str(datos.get("aviso", "")))
    if url:
        perfil_html = f'<a href="{url}" rel="noopener noreferrer">{url}</a>'
    else:
        perfil_html = "No disponible"

    documento = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Informe exploratorio Big Five</title>
<style>
:root {{ color-scheme: light; }}
body {{ font-family: Arial, sans-serif; margin: 0; background: #f3f5f8; color: #202938; line-height: 1.55; }}
main {{ max-width: 1050px; margin: 32px auto; padding: 0 18px; }}
header, section {{ background: white; padding: 24px; border-radius: 14px; margin-bottom: 18px; box-shadow: 0 3px 16px #1720330c; }}
h1 {{ margin-top: 0; }} h2 {{ margin-top: 0; font-size: 1.25rem; }}
.meta {{ color: #526174; }}
.warning {{ border-left: 5px solid #d97706; background: #fff7e6; padding: 14px; border-radius: 6px; }}
.barrow {{ display: grid; grid-template-columns: 220px 1fr 45px; gap: 12px; align-items: center; margin: 16px 0; }}
.track {{ height: 15px; border-radius: 20px; background: #e4e9f0; overflow: hidden; }}
.fill {{ height: 100%; background: #4776d0; border-radius: 20px; }}
.tablewrap {{ overflow-x: auto; }} table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #e3e7ed; text-align: left; padding: 12px; vertical-align: top; }}
th {{ background: #f7f8fa; }} li {{ margin-bottom: 5px; }}
footer {{ color: #637083; font-size: .9rem; padding: 10px 2px 28px; }}
@media(max-width:650px) {{ .barrow {{ grid-template-columns: 1fr 45px; }} .barrow span {{ grid-column: 1 / -1; }} }}
</style>
</head>
<body><main>
<header>
<h1>Informe exploratorio de personalidad — Big Five</h1>
<p class="meta">Perfil: <strong>{usuario}</strong> · Videos analizados: {datos.get("perfil", {}).get("videos_analizados", 0)} · Modelo: {modelo}</p>
<p>Perfil público consultado: {perfil_html}</p>
<div class="warning"><strong>Importante:</strong> {aviso}</div>
</header>
<section><h2>Resumen generado por IA</h2><p>{resumen}</p></section>
<section><h2>Visualización de puntuaciones exploratorias</h2>
<p class="meta">La escala 0–100 es una representación del análisis textual generado por IA; no es una medida psicológica validada.</p>
{"".join(barras)}
</section>
<section><h2>Resultados y evidencias</h2><div class="tablewrap"><table>
<thead><tr><th>Rasgo</th><th>Puntuación</th><th>Confianza</th><th>Interpretación y evidencias textuales</th></tr></thead>
<tbody>{"".join(filas)}</tbody></table></div></section>
<section><h2>Limitaciones del análisis</h2><ul>{limitaciones}
<li>Solo se analizan descripciones y hashtags; no se analiza el video ni el audio.</li>
<li>Los captions pueden ser humorísticos, promocionales, estar escritos por terceros o no representar opiniones personales.</li>
<li>El resultado no debe usarse para tomar decisiones sobre una persona ni presentarse como diagnóstico psicológico.</li>
</ul></section>
<footer>Generado localmente por ProyectoTiktok. Revisa las evidencias y limitaciones antes de presentar el informe.</footer>
</main></body></html>"""
    Path(destino).write_text(documento, encoding="utf-8")
