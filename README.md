# 📊 TikTok Psychographic Engine
### Scraping, análisis Big Five e indicadores de interés turístico

## 📌 Descripción del proyecto

TikTok Psychographic Engine es una herramienta desarrollada en Python para recopilar información pública de perfiles de TikTok, analizar el contenido textual mediante reglas y palabras clave, y presentar los resultados en un informe HTML.

El proyecto integra las siguientes etapas:

1. Autenticación manual en Chromium y almacenamiento local de cookies.
2. Extracción de información pública del perfil seleccionado.
3. Análisis textual mediante indicadores asociados al modelo de personalidad Big Five (OCEAN).
4. Cálculo de indicadores heurísticos de interés turístico y análisis estadístico de métricas.
5. Generación y visualización de un informe HTML.

El sistema tiene un enfoque exploratorio de inteligencia de audiencias aplicada al turismo (TravelTech). Los resultados son indicadores experimentales y no constituyen evaluaciones psicológicas validadas ni confirmaciones de las preferencias reales de una persona.

## 🎯 Objetivos

- Recopilar información pública de perfiles de TikTok mediante automatización del navegador.
- Analizar el contenido textual utilizando reglas y palabras clave.
- Calcular indicadores relativos asociados a las cinco dimensiones del modelo Big Five.
- Explorar señales textuales relacionadas con posibles intereses turísticos.
- Analizar la distribución de primeros dígitos de determinadas métricas mediante la ley de Benford.
- Almacenar los resultados en archivos JSON.
- Generar un reporte visual HTML con los resultados del procesamiento.

## 🧰 Tecnologías utilizadas

- **Python:** lenguaje principal.
- **Playwright:** automatización del navegador Chromium.
- **JSON:** almacenamiento de cookies, datos recopilados y resultados.
- **HTML / CSS:** presentación visual del informe.
- **PowerShell:** ejecución de los scripts en Windows.
- **Git y GitHub:** control de versiones.

## 📋 Requisitos previos

- Windows con PowerShell.
- Python instalado y disponible desde la terminal.
- Git, si deseas clonar el repositorio.
- Dependencias indicadas en `requirements.txt`.
- Conexión a Internet.
- Una cuenta de TikTok para iniciar sesión manualmente cuando sea necesario.

## 🚀 Instalación y configuración

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Jordan-114/ProyectoTiktok.git
cd ProyectoTiktok
```

Si ya tienes el proyecto descargado, abre PowerShell en la carpeta del proyecto y continúa con el siguiente paso.

### 2. Crear un entorno virtual

```powershell
python -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Instala Chromium mediante Playwright:

```powershell
python -m playwright install chromium
```

### 4. Configurar las variables de entorno

Si el proyecto utiliza variables de entorno, revisa el archivo `.env.example` y crea tu archivo local `.env`:

```powershell
Copy-Item .env.example .env
```

Edita `.env` y configura las variables que realmente utiliza el código. Los nombres y valores deben coincidir con los definidos en el proyecto.

**Importante:**
- No inventes variables que el código no utilice.
- No publiques el archivo `.env` si contiene información sensible.
- No subas cookies, credenciales ni archivos de sesión a GitHub.
- Verifica que `.env` y el archivo JSON de sesión estén incluidos en `.gitignore`.

Si alguna variable no es necesaria para la versión actual, no es obligatorio crearla.

## 🔄 Flujo de ejecución

Ejecuta los scripts en el siguiente orden, desde la carpeta raíz del proyecto y con el entorno virtual activado.

### Paso 1. Iniciar sesión y guardar las cookies

Ejecuta:

```powershell
python guardar_sesion.py
```

El script abre Chromium para que puedas iniciar sesión manualmente en TikTok.

1. Espera a que se abra la ventana del navegador.
2. Inicia sesión en TikTok.
3. Si aparece una verificación de seguridad, complétala manualmente siguiendo las indicaciones de TikTok.
4. Regresa a la terminal de PowerShell.
5. Presiona **Enter** cuando el script lo solicite para guardar las cookies y el estado de la sesión en un archivo JSON.

El archivo generado permite reutilizar la sesión en las siguientes etapas, según la configuración del scraper.

**Nota:** las cookies son datos sensibles. Mantén el archivo de sesión en tu computadora y no lo compartas ni lo publiques en el repositorio.

### Paso 2. Ejecutar el scraper y seleccionar el perfil

Ejecuta:

```powershell
python scraper_tiktok.py
```

El programa solicita el nombre de usuario del perfil de TikTok que deseas analizar.

Introduce el usuario **sin el símbolo `@`**.

Por ejemplo, si el perfil es `@Pacho_Willian`, escribe:

```text
Pacho_Willian
```

El scraper utiliza el navegador y la sesión guardada para intentar recopilar la información disponible del perfil.

Si TikTok solicita un CAPTCHA o una verificación adicional, complétala manualmente en el navegador cuando sea posible. La extracción depende de la disponibilidad del perfil, la sesión y las restricciones de la plataforma; no se garantiza que todos los intentos finalicen correctamente.

Al terminar, el scraper genera los datos de entrada que utilizarán las siguientes etapas. En la estructura del proyecto, el archivo de datos recopilados se denomina `resultado.json`.

### Paso 3. Ejecutar el análisis Big Five

Cuando el scraping haya finalizado correctamente, ejecuta:

```powershell
python analizar_big_five.py
```

Este script procesa los datos recopilados y genera indicadores asociados a las cinco dimensiones del modelo Big Five:

- **Apertura (Openness):** indicadores relacionados con la apertura a experiencias.
- **Responsabilidad (Conscientiousness):** indicadores relacionados con la disciplina y el cumplimiento de objetivos.
- **Extraversión (Extraversion):** indicadores relacionados con la interacción social.
- **Amabilidad (Agreeableness):** indicadores relacionados con la cooperación y las relaciones interpersonales.
- **Neuroticismo (Neuroticism):** indicadores textuales relacionados con la sensibilidad emocional.

El análisis se basa en las reglas y palabras clave implementadas en el código. Los porcentajes obtenidos son relativos al método utilizado y no equivalen a una prueba psicológica validada.

El archivo de resultados del análisis se denomina `resultado_big_five.json`.


### Paso 4. Abrir el informe en el navegador

Para visualizar el reporte desde PowerShell, ejecuta:

```powershell
Start-Process .\informe_big_five.html
```

Este comando abre el archivo HTML utilizando la aplicación predeterminada de Windows para ese tipo de archivo, normalmente el navegador web.

## ⚡ Ejecución resumida

Una vez instaladas las dependencias y configurado el entorno, el flujo completo es:

```powershell
python guardar_sesion.py
python scraper_tiktok.py
python analizar_big_five.py
Start-Process .\informe_big_five.html
```

Recuerda que debes completar las acciones interactivas de los dos primeros scripts cuando se soliciten:

- **`guardar_sesion.py`:** inicia sesión en Chromium y presiona Enter en PowerShell para guardar las cookies.
- **`scraper_tiktok.py`:** introduce el usuario sin `@` y completa manualmente las verificaciones que solicite TikTok.

Ejecuta cada comando por separado y comprueba que finalice correctamente antes de continuar.

## 📂 Estructura del proyecto

```text
ProyectoTiktok/
├── guardar_sesion.py        # Inicio de sesión y almacenamiento de cookies
├── scraper_tiktok.py        # Extracción de información pública de TikTok
├── analizar_big_five.py     # Análisis textual e indicadores Big Five
├── big_five.py              # Funciones auxiliares del modelo Big Five
├── generar_informe.py       # Generación del reporte HTML
├── requirements.txt         # Dependencias de Python
├── .env.example             # Plantilla de variables de entorno, si aplica
├── .env                     # Configuración local; no publicar
├── .gitignore               # Archivos excluidos de Git
├── tiktok_state.json        # Estado local de sesión, si este es el nombre configurado
├── resultado.json           # Datos recopilados
├── resultado_big_five.json  # Resultados del análisis
└── informe_big_five.html    # Reporte visual generado
```

Los archivos JSON y el informe HTML pueden generarse durante la ejecución. Sus nombres y ubicaciones deben coincidir con la configuración real de los scripts.

## 📊 Interpretación de los resultados

### Indicadores Big Five

Los valores representan los resultados del método de análisis textual implementado. No deben interpretarse como diagnósticos psicológicos ni como características personales confirmadas.

### Índice heurístico de interés turístico

El índice utiliza una fórmula definida en el proyecto para explorar posibles señales textuales de interés turístico. No representa una probabilidad estadística real ni confirma que una persona tenga intención de viajar.

### Análisis de la ley de Benford

El análisis compara la distribución de primeros dígitos de determinadas métricas con una distribución teórica. Las diferencias observadas no demuestran por sí solas fraude, manipulación o actividad irregular. La interpretación depende del tamaño, la naturaleza y las características de los datos.

## 🛠️ Solución de problemas

**Python no se reconoce en PowerShell**

Comprueba la instalación:

```powershell
python --version
```

Si ese comando no funciona, prueba:

```powershell
py --version
```

**Playwright no encuentra Chromium**

Ejecuta:

```powershell
python -m playwright install chromium
```

**No se guarda la sesión**

Verifica que hayas iniciado sesión, presionado Enter cuando el programa lo solicita y comprobado que el archivo JSON de sesión se haya generado en la ubicación esperada.

**El scraper no encuentra el perfil**

Comprueba el nombre de usuario, escríbelo sin `@` y verifica que el perfil sea accesible. Si aparece una verificación de seguridad, sigue las indicaciones mostradas por TikTok.

**El análisis Big Five no encuentra los datos**

Comprueba que el scraper haya finalizado correctamente y que el archivo JSON de entrada exista en la ubicación esperada.

**No se genera el informe HTML**

Verifica que `resultado_big_five.json` exista y que `generar_informe.py` pueda leerlo correctamente.

## 🔒 Seguridad y uso responsable

- Utiliza el proyecto con fines legítimos de investigación.
- Respeta los términos de servicio de TikTok y las normas aplicables de privacidad y protección de datos.
- No publiques cookies, archivos de sesión, contraseñas ni tokens.
- No utilices indicadores heurísticos para tomar decisiones importantes sobre personas.
- No presentes los resultados exploratorios como conclusiones psicológicas verificadas.

## 👨‍💻 Autor

**Jordan Guaicha**

Repositorio: https://github.com/Jordan-114/ProyectoTiktok
