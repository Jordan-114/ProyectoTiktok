# 📊 Proyecto TikTok: Scraping y análisis exploratorio Big Five con Python

## 📌 Descripción del proyecto

Este proyecto utiliza Python para recopilar información pública de perfiles de TikTok, obtener descripciones de sus publicaciones y utilizar inteligencia artificial para realizar un análisis exploratorio basado en el modelo de personalidad **Big Five**.

Los resultados se almacenan en archivos JSON y se presentan mediante un informe HTML que facilita la visualización de los rasgos analizados.

## 🎯 Objetivos

- Recopilar información disponible públicamente de un perfil de TikTok.
- Obtener las publicaciones y sus descripciones textuales cuando estén disponibles.
- Identificar hashtags y otros datos relevantes de las publicaciones recopiladas.
- Utilizar la API de Google Gemini para generar un análisis exploratorio de los cinco rasgos Big Five.
- Guardar los resultados en archivos JSON.
- Generar un informe visual en HTML.
- Practicar Python, automatización de navegadores, procesamiento de datos e inteligencia artificial.

## 🧰 Tecnologías utilizadas

- **Python:** lenguaje principal del proyecto.
- **Playwright:** automatización del navegador para acceder a páginas públicas de TikTok.
- **Google Gemini API:** análisis exploratorio del contenido textual recopilado.
- **JSON:** almacenamiento e intercambio de datos.
- **HTML:** presentación visual de los resultados.
- **Git y GitHub:** control de versiones y publicación del código fuente.

## 📂 Estructura del proyecto

```text
ProyectoTiktok/
├── scraper_tiktok.py          # Recopilación de datos públicos de TikTok
├── guardar_sesion.py           # Preparación de la sesión local del navegador
├── analizar_big_five.py       # Análisis con Google Gemini
├── big_five.py                # Funciones auxiliares del análisis
├── generar_informe.py         # Generación del informe HTML
├── requirements.txt           # Dependencias de Python
├── .env.example               # Plantilla de variables de entorno
├── .env                       # Clave privada; no se publica
├── .gitignore                 # Archivos excluidos de Git
├── tiktok_state.json          # Estado local de sesión; no se publica
├── resultado.json             # Datos recopilados
├── resultado_big_five.json    # Resultados del análisis
└── informe_big_five.html      # Informe visual generado
```

*Nota: los archivos JSON y el informe HTML se generan durante la ejecución. Los archivos privados y los resultados con datos personales deben mantenerse fuera del repositorio público cuando corresponda.*

## ⚙️ Requisitos previos

Antes de ejecutar el proyecto, instala:

1. Python 3.13 o una versión compatible con las dependencias.
2. Git para administrar el repositorio.
3. Una clave de API de Google Gemini.
4. Las dependencias de Python especificadas en `requirements.txt`.

Puedes obtener una clave de Gemini desde Google AI Studio:

https://aistudio.google.com/apikey

## 🚀 Instalación en Windows

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Jordan-114/ProyectoTiktok.git
cd ProyectoTiktok
```

### 2. Crear un entorno virtual

```powershell
python -m venv .venv
```

Activarlo en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si la creación del entorno virtual falla, revisa la instalación de Python y pip antes de continuar.

### 3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

### 4. Instalar Chromium para Playwright

```powershell
python -m playwright install chromium
```

### 5. Configurar las variables de entorno

Crea un archivo `.env` en la carpeta raíz del proyecto. Puedes utilizar `.env.example` como referencia.

El archivo `.env` debe contener tu clave privada:

```dotenv
GEMINI_API_KEY=TU_CLAVE_REAL_DE_GEMINI
```

Reemplaza el valor de ejemplo por tu propia clave. No publiques este archivo ni compartas la clave en capturas de pantalla.

## ▶️ Ejecución del proyecto

Ejecuta los scripts desde la carpeta raíz del proyecto y en el orden indicado.

### Paso 1. Preparar la sesión del navegador

```powershell
python guardar_sesion.py
```

Sigue las instrucciones del programa para preparar la sesión local, si TikTok solicita iniciar sesión.

La sesión se guarda localmente para su uso posterior. No compartas el archivo `tiktok_state.json`, ya que puede contener cookies y datos de autenticación.

### Paso 2. Recopilar información de TikTok

```powershell
python scraper_tiktok.py
```

Introduce el nombre de usuario cuando el programa lo solicite, de acuerdo con las instrucciones que muestre la terminal.

El scraper intenta recopilar datos del perfil y de sus publicaciones, incluidas las descripciones textuales y los hashtags disponibles.

Los datos se guardan en:

```text
resultado.json
```

La cantidad de publicaciones recopiladas y la disponibilidad de sus descripciones pueden variar según el perfil y las restricciones de TikTok.

### Paso 3. Analizar las publicaciones con Gemini

```powershell
python analizar_big_five.py
```

Este script utiliza la información recopilada para solicitar a Gemini un análisis exploratorio basado en los cinco rasgos del modelo Big Five.

El resultado se guarda en:

```text
resultado_big_five.json
```

La ejecución requiere una clave de Gemini válida y las variables de entorno configuradas correctamente.

### Paso 4. Generar el informe visual

```powershell
python generar_informe.py
```

El generador utiliza los resultados disponibles para crear el informe visual en HTML.

Si el archivo generado se llama `informe_big_five.html`, puedes abrirlo en Windows con:

```powershell
Start-Process .\informe_big_five.html
```

El informe puede consultarse desde el navegador y utilizarse como apoyo visual para la presentación académica.

## 🧠 ¿Qué es el modelo Big Five?

El modelo Big Five organiza la personalidad en cinco dimensiones generales:

1. **Apertura a la experiencia:** interés por ideas, experiencias y actividades nuevas.
2. **Responsabilidad:** organización, planificación y orientación al cumplimiento de objetivos.
3. **Extraversión:** sociabilidad y tendencia a buscar interacción o estimulación social.
4. **Amabilidad:** tendencias relacionadas con la cooperación y la consideración hacia los demás.
5. **Neuroticismo:** dimensión relacionada con la tendencia a experimentar emociones negativas.

El proyecto utiliza contenido textual de publicaciones como material para una exploración automatizada de estas dimensiones.

**Importante:** las puntuaciones generadas por inteligencia artificial no constituyen una evaluación psicológica validada, un diagnóstico ni una medición científica de la personalidad. Las descripciones de TikTok son información limitada y no permiten establecer conclusiones definitivas sobre una persona.

## 🔐 Seguridad y privacidad

Para mantener seguro el proyecto:

- No subir `.env` a GitHub.
- No subir `tiktok_state.json` ni compartir cookies de sesión.
- No publicar claves de API, contraseñas ni tokens.
- Revisar los JSON y el HTML antes de publicarlos, ya que pueden contener nombres de usuario, enlaces u otros datos personales.
- Utilizar los datos de forma responsable y respetar las condiciones de uso de TikTok y las restricciones de acceso de la plataforma.
- No intentar eludir mecanismos de seguridad, CAPTCHA o limitaciones de acceso.

El archivo `.gitignore` debe incluir, como mínimo:

```gitignore
.env
.env.*
tiktok_state.json
.venv/
__pycache__/
```

## 🛠️ Solución de problemas

**Error al importar un módulo**

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

**Error al iniciar Playwright**

Instala el navegador requerido:

```powershell
python -m playwright install chromium
```

**Error de autenticación de Gemini**

Comprueba que la clave esté correctamente configurada en `.env`, que sea válida y que el modelo utilizado esté disponible para tu API.

**El scraper no encuentra suficientes descripciones**

Comprueba la conexión, el perfil consultado y la disponibilidad de sus publicaciones. No todos los perfiles muestran el mismo contenido y TikTok puede limitar el acceso.

**No se genera el informe HTML**

Comprueba que los archivos de resultados necesarios existan y que la terminal no muestre errores al ejecutar `generar_informe.py`.

## 👨‍🎓 Contexto académico

Proyecto desarrollado con fines educativos para practicar técnicas de recopilación de información pública, procesamiento de datos, automatización con Python e integración de modelos de inteligencia artificial.

## 📄 Licencia

Proyecto académico personal. Antes de reutilizar o redistribuir el código, revisa las condiciones de las bibliotecas y servicios utilizados.
