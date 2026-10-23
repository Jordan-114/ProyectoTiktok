# 📊 TikTok Psychographic Engine: Scraping, Análisis Big Five y Segmentación Turística (B2B)

## 📌 Descripción del proyecto

Este proyecto utiliza Python y la API de Google Gemini para realizar **scraping y profiling psicográfico** de perfiles públicos de TikTok mediante el modelo de personalidad **Big Five (OCEAN)**. 

El sistema está orientado a un caso de uso B2B de **Inteligencia de Audiencias para Turismo (TravelTech)**: clasifica la personalidad de los usuarios a partir de sus publicaciones en TikTok para alimentar campañas de publicidad hiper-segmentadas (en TikTok Ads y Meta Ads) destinadas a agencias de viajes, hoteles y empresas del sector.

Los resultados se estructuran en archivos JSON y se consolidan en un informe visual en HTML.

## 💡 Idea de Negocio (Caso de Uso B2B)

**Agencia de Ads Psicológicos para Turismo**
Las agencias de viajes tradicionales pierden presupuesto al segmentar únicamente por variables demográficas (edad o ubicación). Este motor permite segmentar por **motivaciones emocionales y tipo de viajero**:

* **Alta Apertura (Openness):** Target ideal para turismo de aventura, mochileros y experiencias culturales exóticas.
* **Alta Extraversión (Extraversion):** Target ideal para festivales, viajes grupales, cruceros y vida nocturna.
* **Alta Neuroticismo / Sensibilidad:** Target ideal para paquetes *All-Inclusive*, viajes organizados y turismo de bienestar/relax.
* **Alta Escrupulosidad (Conscientiousness):** Target ideal para itinerarios detallados, pases multipack (*City Pass*) y viajes corporativos.
* **Alta Amabilidad (Agreeableness):** Target ideal para ecoturismo, voluntariados y viajes familiares.

---

## 🎯 Objetivos

- Recopilar información pública de perfiles de TikTok (descripciones, hashtags y engagement) mediante automatización.
- Procesar el contenido textual con Google Gemini para extraer métricas del modelo de personalidad Big Five.
- Mapear el perfil psicográfico obtenido hacia categorías comerciales de intención de viaje.
- Generar datos estructurados (JSON) e informes visuales (HTML) utilizables por agencias de marketing o turismo.
- Automatizar el flujo completo desde la extracción de datos hasta el reporte final.

## 🧰 Tecnologías utilizadas

- **Python 3.13:** Lenguaje principal del motor.
- **Playwright:** Automatización de navegador para scraping público en TikTok.
- **Google Gemini API:** Motor de Inteligencia Artificial para procesamiento de lenguaje natural (NLP) y scoring psicológico.
- **JSON:** Almacenamiento y estructuración de los segmentos de audiencia.
- **HTML / CSS:** Presentación visual del informe psicográfico.
- **Git & GitHub:** Control de versiones.

## 📂 Estructura del proyecto

```text
ProyectoTiktok/
├── scraper_tiktok.py        # Recopilación de datos públicos de TikTok
├── guardar_sesion.py        # Gestión e inicio de sesión local del navegador
├── analizar_big_five.py     # Procesamiento NLP y profiling Big Five con Gemini
├── big_five.py              # Lógica y funciones auxiliares del modelo OCEAN
├── generar_informe.py       # Generador del reporte visual HTML
├── requirements.txt         # Dependencias del proyecto
├── .env.example             # Plantilla de variables de entorno
├── .env                     # Claves privadas (no se publica en Git)
├── .gitignore               # Exclusiones de Git
├── tiktok_state.json        # Cookies y sesión local (no se publica en Git)
├── resultado.json           # Datos crudos extraídos de TikTok
├── resultado_big_five.json  # Matriz psicográfica y scoring generado por Gemini
└── informe_big_five.html    # Dashboard visual HTML generado