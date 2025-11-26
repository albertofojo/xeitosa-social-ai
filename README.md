# Xeitosa Social AI 🎵

**Xeitosa Social AI** es una herramienta interna diseñada para **Xeitosa Producións** que utiliza Inteligencia Artificial (Google Gemini 2.0 Flash) para generar textos (copy) para redes sociales.

La aplicación permite crear contenido personalizado adaptado al tono, idioma y audiencia de cada artista de la productora, analizando tanto las instrucciones del usuario como archivos multimedia (imágenes y vídeos).

## ✨ Características

*   **Perfiles de Artista Personalizados**: Generación de texto adaptada a la "persona" de cada artista (ej. Xeitosa Corporativo, Sheila Patricia, Os Carecos).
*   **Multimodalidad**: Capacidad para "ver" y analizar imágenes y vídeos para crear textos contextualizados.
*   **Gestión de Idiomas**: Respeta el idioma preferente del artista (Gallego, Castellano, etc.).
*   **Interfaz Moderna**: Diseño limpio y centrado para una experiencia de usuario fluida.

## 🚀 Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/albertofojo/xeitosa-social-ai.git
    cd xeitosa-social-ai
    ```

2.  **Crear un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuración

1.  Crea un archivo `.env` en la raíz del proyecto.
2.  Añade tu clave de API de Google Gemini:
    ```env
    GOOGLE_API_KEY=tu_clave_api_aqui
    ```

### Configuración de Artistas
Los perfiles de los artistas se definen en `artist-config.json`. Puedes añadir o modificar artistas editando este archivo. Cada perfil incluye:
*   `name`: Nombre visible.
*   `base_prompt`: La "personalidad" del sistema.
*   `keywords`: Palabras clave obligatorias.
*   `few_shot_examples`: Ejemplos de estilo para el aprendizaje en contexto.

## ▶️ Uso

Ejecuta la aplicación con Streamlit:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador (normalmente en `http://localhost:8501`).

## 🛠️ Tecnologías

*   **Python 3.10+**
*   **Streamlit**: Framework para la interfaz de usuario.
*   **Google Generative AI (Gemini)**: Motor de IA (Modelo `gemini-2.0-flash`).
*   **Python-dotenv**: Gestión de variables de entorno.
