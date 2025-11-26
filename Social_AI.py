import streamlit as st
import google.generativeai as genai
import os
import json
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Xeitosa Social AI",
    page_icon="🎵",
    layout="centered"
)

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("⚠️ Non se atopou a GOOGLE_API_KEY nas variables de entorno. Por favor, revisa o teu ficheiro .env.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Load Artist Configuration
def load_config():
    config_path = Path("artist-config.json")
    if not config_path.exists():
        st.error("❌ Non se atopou artist-config.json!")
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Erro ao cargar a configuración: {e}")
        return None

config = load_config()

if not config:
    st.stop()

# Helper function to upload to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    # print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active.

    Some files uploaded to the Gemini API need to be processed before they can
    be used as prompt inputs. The status can be seen by querying the file's
    "state" field.

    This implementation relies on the file's "name" field to perform this check.
    """
    # print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(2) # Sleep for 2 seconds
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    # print("...all files ready")

# --- UI Layout ---

# Logo and Title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Social AI</h3>", unsafe_allow_html=True)

with col3:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("⚙️", help="Xestionar Artistas"):
        st.switch_page("pages/1_Xestión_Artistas.py")

artists = config.get("artists", [])
artist_names = [artist["name"] for artist in artists]

# Artist Selection (Top)
selected_artist_name = st.selectbox("Selecciona un Perfil de Artista", artist_names)

# Get selected artist data
selected_artist = next((a for a in artists if a["name"] == selected_artist_name), None)

if selected_artist:
    with st.expander("ℹ️ Información do Perfil (Audiencia e Ton)", expanded=False):
        st.markdown(f"**Audiencia:** {selected_artist['target_audience']}")
        st.markdown(f"**Idioma:** {selected_artist['language']}")
        st.markdown(f"**Ton:** {selected_artist['base_prompt']}")

st.markdown("---")

# Inputs (Stacked)
user_instructions = st.text_area(
    "Instrucións para o Copy",
    placeholder="Ex: Describe o novo episodio do podcast con Sheila Patricia...",
    height=150
)

uploaded_file = st.file_uploader(
    "Subir Multimedia (Vídeo/Imaxe)", 
    type=['mp4', 'mov', 'jpg', 'png']
)

generate_btn = st.button("✨ Xerar Copy", type="primary", use_container_width=True)

if generate_btn:
    if not user_instructions and not uploaded_file:
        st.warning("Por favor, escribe instrucións ou sube un ficheiro.")
    else:
            with st.spinner("Xerando contido... Isto pode levar un momento."):
                try:
                    # 1. Handle File Upload
                    gemini_file = None
                    temp_file_path = None
                    
                    if uploaded_file:
                        # Create a temporary file
                        suffix = Path(uploaded_file.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_file_path = tmp_file.name
                        
                        # Determine mime_type
                        mime_type = uploaded_file.type
                        
                        # Upload to Gemini
                        gemini_file = upload_to_gemini(temp_file_path, mime_type=mime_type)
                        
                        # Wait for processing if video
                        if "video" in mime_type:
                            wait_for_files_active([gemini_file])
                            
                    # 2. Construct Prompt
                    
                    # Base Prompt (Persona)
                    prompt_parts = [
                        f"SYSTEM PERSONA:\n{selected_artist['base_prompt']}\n",
                        f"MANDATORY KEYWORDS (Include some of these naturally):\n{', '.join(selected_artist['keywords'])}\n",
                        "STYLE EXAMPLES (Few-shot learning):\n"
                    ]
                    
                    for example in selected_artist['few_shot_examples']:
                        prompt_parts.append(f"- {example}")
                        
                    prompt_parts.append(f"\nUSER TASK:\n{user_instructions}")
                    
                    if gemini_file:
                        prompt_parts.append(gemini_file)
                        prompt_parts.append("\n(Analyze the attached media and incorporate it into the copy)")

                    # 3. Generate Content
                    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
                    
                    response = model.generate_content(prompt_parts)
                    
                    # Display Output
                    st.success("Copy Xerado:")
                    st.markdown(response.text)
                    
                    # 4. Cleanup
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
                    # We don't delete from Gemini in this MVP to keep it simple, 
                    # but in production we might want to clean up cloud resources too.
                    
                except Exception as e:
                    st.error(f"Ocorreu un erro: {e}")
                    # Cleanup on error
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

