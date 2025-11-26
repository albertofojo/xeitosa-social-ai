# 🚀 Guía de Desenvolvemento: Apps de IA con Antigravity & Streamlit

Este documento detalla o proceso técnico e o fluxo de traballo utilizado para crear a ferramenta **"Xeitosa Social AI"**. Serve como manual de referencia para replicar aplicacións de IA Xenerativa ("Vibe Coding") de xeito rápido e eficiente.

## 1. Stack Tecnolóxico

* **IDE (Contorno de Desenvolvemento):** Google Antigravity.
* **Linguaxe:** Python 3.10+.
* **Frontend (Interface):** Streamlit.
* **Motor de IA:** Google Gemini 1.5 Pro (SDK `google-generativeai`).
* **Control de Versións:** Git & GitHub.
* **Despregamento (Hosting):** Streamlit Community Cloud.

---

## 2. Configuración do Entorno e do Axente

O primeiro paso é configurar o "cerebro" do Axente en Antigravity para que actúe como un enxeñeiro experto e siga as nosas normas.

**Acción:** Ir ao panel **Customizations** > **Rules** > **+ Workspace** e engadir a seguinte regra (recomendase en inglés para maior precisión do modelo):

* **Nome da Regra:** `Project_Stack_Rules`
* **Contido:**
    * **Rol:** Senior Python Developer.
    * **Stack obrigatorio:** Streamlit e google-generativeai.
    * **Normas:**
        1. Manter o código simple (MVP).
        2. Usar ficheiros JSON locais para datos (non SQL).
        3. Nunca escribir claves API no código (usar variables de entorno `os.getenv`).
        4. Asegurar que a app acepte subida de vídeo e imaxe.

---

## 3. Arquitectura de Datos (Contexto)

Para non mesturar código e datos, e facilitar o mantemento, definimos a personalidade da IA nun ficheiro externo.

**Ficheiro:** `artist_config.json` (creado na raíz do proxecto).

**Estrutura do JSON:**
Contén unha lista de artistas. Para cada un defínese:
* `id` e `name`: Identificadores internos e visibles no selector.
* `language`: Idioma base (Galego/Castelán).
* `base_prompt`: Instrución de sistema que define a personalidade (ex: "Eres poeta e rural").
* `keywords`: Palabras chave obrigatorias que debe usar.
* `few_shot_examples`: Lista de posts reais anteriores para que a IA imite o estilo (*Few-Shot Prompting*).

---

## 4. Proceso de Construción (Prompts)

O desenvolvemento divídese en dúas fases de prompts executados no chat do Axente ("Mission Control"):

### Fase 1: Inxección de Datos
Pídese ao axente que cree o ficheiro `artist_config.json` cos datos reais extraídos das redes sociais.

### Fase 2: Xeración da App (`app.py`)
Pídese ao axente que actúe como Senior Dev e constrúa a lóxica completa:
1.  Crear `requirements.txt` coas dependencias (`streamlit`, `google-generativeai`, `python-dotenv`).
2.  Cargar o JSON de configuración ao inicio.
3.  **Deseñar a Interface:** Barra lateral para seleccionar artista e área principal para instrucións e subida de ficheiros multimedia.
4.  **Programar a Lóxica:** Ao premer o botón, subir o vídeo temporalmente á API de Gemini e xerar o texto combinando o prompt do sistema (do JSON) coas instrucións do usuario.

---

## 5. Seguridade e Probas Locais

Antes de subir nada a Internet, é crucial xestionar as claves de seguridade para non expoñelas.

1.  **Ficheiro `.env`:** Créase localmente para gardar a variable `GOOGLE_API_KEY`.
2.  **Ficheiro `.gitignore`:** Créase para indicarlle a Git que ignore o ficheiro `.env` e os cartafoles virtuais (`venv/`, `__pycache__/`), evitando filtrar claves privadas ao repositorio público.

---

## 6. Despregamento (Deploy)

O paso a produción realízase sen servidores complexos usando a nube de Streamlit.

1.  **GitHub:** Créase un repositorio (privado ou público) e súbese o código final.
2.  **Streamlit Community Cloud:**
    * Créase unha nova app conectada ao repositorio de GitHub.
    * Na configuración avanzada (**Advanced Settings > Secrets**), engádese a clave API de xeito seguro:
      ```toml
      GOOGLE_API_KEY = "a_tua_clave_api_aqui"
      ```
3.  **Instalación en Móbil:**
    * Ábrese a URL da web no navegador do móbil.
    * Úsase a opción do navegador "Engadir á pantalla de inicio" (iOS/Android) para que funcione como unha App nativa.

---

## 7. Mantemento Futuro

O sistema está deseñado para ser mantido sen tocar código.

Para engadir novos artistas ou modificar o estilo de redacción:
1.  Editar unicamente o ficheiro `artist_config.json`.
2.  Facer "Commit" e "Push" a GitHub.
3.  A aplicación actualízase automaticamente en poucos minutos cos novos datos.