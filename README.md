# ProyectoTiktok — Scraper de perfiles públicos

**Aplicación desarrollada en Python para consultar información pública de perfiles de TikTok mediante automatización del navegador con Playwright.**

## Descripción

Proyecto académico que busca aplicar conceptos de programación en Python y automatización web para acceder a un perfil público de TikTok, obtener los datos que estén disponibles en la página y almacenarlos en un archivo JSON.

El proyecto utiliza una sesión del navegador guardada localmente para facilitar el acceso a la página cuando sea necesario.

## Objetivos

- Desarrollar una aplicación de extracción de datos web utilizando Python.
- Automatizar la navegación hacia perfiles públicos de TikTok.
- Identificar y procesar datos del perfil disponibles en la página.
- Guardar los resultados en formato JSON para facilitar su lectura y reutilización.
- Practicar el manejo de archivos, excepciones y automatización con Playwright.

## Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **Playwright:** automatización del navegador.
- **Chromium:** navegador utilizado por Playwright.
- **JSON:** formato de almacenamiento de los resultados.

## Funcionalidades

- Apertura de TikTok mediante un navegador automatizado.
- Uso de una sesión local guardada en el equipo.
- Navegación a un perfil mediante su nombre de usuario.
- Extracción de los datos del perfil que estén disponibles en la página.
- Generación del archivo `resultado.json`.

Los datos que pueden obtenerse incluyen el nombre de usuario, nombre visible, biografía, estado de verificación, seguidores, seguidos, cantidad de me gusta y número de publicaciones. La disponibilidad depende de la información que TikTok entregue en cada página.

## Estructura del proyecto

```text
ProyectoTiktok/
├── guardar_sesion.py
├── scrapear.py
├── README.md
├── .gitignore
├── tiktok_state.json   # Local, no publicar
└── resultado.json      # Archivo generado localmente
```

Los dos últimos archivos son de uso local y están excluidos del repositorio mediante `.gitignore`.

## Requisitos previos

- Python instalado.
- Git instalado.
- Conexión a Internet.
- Una cuenta de TikTok, si la página requiere iniciar sesión para acceder al contenido.

## Instalación

### 1. Clonar el repositorio

```bash
git clone URL_DE_TU_REPOSITORIO
cd ProyectoTiktok
```

Sustituye `URL_DE_TU_REPOSITORIO` por la dirección real de tu repositorio de GitHub.

### 2. Crear un entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar Playwright

```powershell
python -m pip install playwright
python -m playwright install chromium
```

## Configuración y uso

### 1. Guardar la sesión local

Ejecuta:

```powershell
python guardar_sesion.py
```

Completa el proceso en el navegador y guarda el estado de la sesión localmente.

### 2. Configurar el perfil

Abre `scrapear.py` y establece el nombre de usuario del perfil que deseas consultar, sin el símbolo `@`.

### 3. Ejecutar el scraper

```powershell
python scrapear.py
```

Si la extracción se realiza correctamente, el programa mostrará los datos en la terminal y generará el archivo `resultado.json` en la carpeta del proyecto.

## Ejemplo del resultado

El archivo JSON puede tener una estructura similar a la siguiente:

```json
{
  "usuario": "usuario_ejemplo",
  "nombre": "Nombre de ejemplo",
  "biografia": "Biografía de ejemplo",
  "verificado": false,
  "seguidores": 12500,
  "seguidos": 350,
  "me_gusta": 45000,
  "publicaciones": 120,
  "url": "https://www.tiktok.com/@usuario_ejemplo"
}
```

*Los valores anteriores son ilustrativos y no corresponden a una cuenta real.*

## Consideraciones y limitaciones

- La estructura interna de TikTok puede cambiar y afectar la extracción.
- Algunos datos pueden no estar disponibles o requerir iniciar sesión.
- La aplicación no garantiza que todos los perfiles o campos puedan consultarse.
- Se recomienda respetar las condiciones de uso de TikTok y la privacidad de los usuarios.
- Este proyecto tiene fines educativos y no pretende eludir mecanismos de seguridad o restricciones de acceso.

## Seguridad

**No publiques archivos de sesión, cookies, contraseñas ni tokens de autenticación.** El archivo `tiktok_state.json` debe permanecer únicamente en el equipo local. Tampoco publiques datos personales o resultados que no tengas autorización para divulgar.

## Autor

Proyecto desarrollado como parte de una actividad académica universitaria.

**Nombre del proyecto:** ProyectoTiktok  
**Lenguaje principal:** Python  
**Área:** Automatización web y extracción de datos
