import streamlit as st
import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import datetime
from email.utils import make_msgid

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Xestión de Artistas", page_icon="📝", layout="wide")

CONFIG_PATH = Path("artist-config.json")

def load_config():
    if not CONFIG_PATH.exists():
        return {"artists": []}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao cargar a configuración: {e}")
        return {"artists": []}

def send_backup_email(config):
    """Sends the config JSON via email."""
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    recipient = os.getenv("BACKUP_EMAIL_RECIPIENT")

    if not all([smtp_server, smtp_port, smtp_email, smtp_password, recipient]):
        print(f"DEBUG: Missing SMTP config. Server={smtp_server}, Port={smtp_port}, Email={smtp_email}, Recipient={recipient}")
        st.warning("⚠️ Configuración SMTP incompleta. Non se enviou backup por email.")
        return

    try:
        print(f"DEBUG: Attempting to send email to {recipient} via {smtp_server}:{smtp_port}")
        
        # Prepare JSON string
        json_str = json.dumps(config, indent=4, ensure_ascii=False)
        
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = recipient
        msg['Subject'] = f"Backup Xeitosa Social AI - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg['Message-ID'] = make_msgid() # Fix for Gmail 550-5.7.1
        
        body = f"""Adxunto atoparás a última versión de artist-config.json:

{json_str}
"""
        msg.attach(MIMEText(body, 'plain'))

        # Removed attachment logic as per user request to put it in body
        
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.set_debuglevel(1) # Enable verbose SMTP logging
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        print("DEBUG: Email sent successfully")
        st.toast("Backup enviado por email! 📧", icon="✅")
    except smtplib.SMTPAuthenticationError:
        st.error("Erro de Autenticación SMTP (535). Se usas Gmail, asegúrate de usar un 'Contrasinal de Aplicación' e non o teu contrasinal normal. Activa a verificación en 2 pasos e xera un en: https://myaccount.google.com/apppasswords")
    except Exception as e:
        print(f"DEBUG: Email error: {e}")
        st.error(f"Erro ao enviar email de backup: {e}")

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        st.toast("Configuración gardada correctamente!", icon="✅")
        
        # Trigger Email Backup
        send_backup_email(config)
        
        # Force reload of config in session state or cache if used, 
        # but since we reload on every run, st.rerun() should handle it.
        # However, we need to ensure the file write is flushed.
        return True
    except Exception as e:
        st.error(f"Erro ao gardar a configuración: {e}")
        return False

def analyze_style_with_ai(artist_name, sample_texts, language="Galego"):
    """Uses Gemini to analyze sample texts and generate a profile."""
    if not GOOGLE_API_KEY:
        st.error("Necesitas configurar a API Key de Google para usar esta función.")
        return None

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are an expert social media strategist and copywriter.
    Your task is to analyze the following sample posts from an artist named "{artist_name}" and extract their "Persona" to create a style guide for an AI generator.

    SAMPLE POSTS:
    {sample_texts}

    OUTPUT FORMAT (JSON ONLY):
    {{
        "base_prompt": "A detailed description of the persona, tone, and style (2-3 sentences). Write this in {language}.",
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8"],
        "target_audience": "A short description of the target audience. Write this in {language}.",
        "few_shot_examples": [
            "Select the 5 (if possible) best and most representative sentences or short paragraphs from the sample posts to use as few-shot examples. Keep them exactly as they are in the source text."
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Erro na análise da IA: {e}")
        return None

st.title("Xestión de Artistas 📝")

config = load_config()
artists = config.get("artists", [])

# Sidebar Actions
st.sidebar.header("Accións")
json_str = json.dumps(config, indent=4, ensure_ascii=False)
st.sidebar.download_button(
    label="📥 Descargar Configuración (JSON)",
    data=json_str,
    file_name="artist-config.json",
    mime="application/json",
    help="Descarga este ficheiro antes de redesplegar a aplicación para non perder os cambios."
)

tab1, tab2, tab3 = st.tabs(["✏️ Editar Existentes", "➕ Crear Novo (Manual)", "✨ Asistente IA"])

# --- TAB 1: EDIT EXISTING ---
with tab1:
    # Reload config to ensure we have the latest data
    config = load_config()
    artists = config.get("artists", [])
    
    if not artists:
        st.info("Non hai artistas configurados.")
    else:
        artist_names = [a["name"] for a in artists]
        selected_name = st.selectbox("Selecciona un Artista para editar", artist_names)
        
        # Find selected artist index
        selected_index = next((i for i, a in enumerate(artists) if a["name"] == selected_name), None)
        
        if selected_index is not None:
            artist = artists[selected_index]
            
            with st.form(key="edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Nome", artist["name"])
                    new_id = st.text_input("ID (único)", artist["id"])
                    new_lang = st.selectbox("Idioma", ["Galego", "Español", "English"], index=["Galego", "Español", "English"].index(artist.get("language", "Galego")))
                with col2:
                    new_audience = st.text_area("Audiencia Obxectivo", artist["target_audience"])
                
                new_prompt = st.text_area("Base Prompt (Persona)", artist["base_prompt"], height=100)
                new_keywords = st.text_area("Keywords (separadas por comas)", ", ".join(artist["keywords"]))
                new_examples = st.text_area("Exemplos (un por liña)", "\n".join(artist["few_shot_examples"]), height=150)
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    submit_button = st.form_submit_button("💾 Gardar Cambios", type="primary", use_container_width=True)
                with c2:
                    delete_button = st.form_submit_button("🗑️ Eliminar Artista", type="secondary", use_container_width=True)

                if submit_button:
                    artists[selected_index] = {
                        "id": new_id,
                        "name": new_name,
                        "language": new_lang,
                        "target_audience": new_audience,
                        "base_prompt": new_prompt,
                        "keywords": [k.strip() for k in new_keywords.split(",") if k.strip()],
                        "few_shot_examples": [e.strip() for e in new_examples.split("\n") if e.strip()]
                    }
                    config["artists"] = artists
                    save_config(config)
                    st.rerun()
                
                if delete_button:
                    artists.pop(selected_index)
                    config["artists"] = artists
                    save_config(config)
                    st.rerun()

# --- TAB 2: CREATE MANUAL ---
with tab2:
    with st.form(key="create_form"):
        c_name = st.text_input("Nome")
        c_id = st.text_input("ID (único, sen espazos)")
        c_lang = st.selectbox("Idioma", ["Galego", "Español", "English"])
        c_audience = st.text_area("Audiencia Obxectivo")
        c_prompt = st.text_area("Base Prompt (Persona)")
        c_keywords = st.text_area("Keywords (separadas por comas)")
        c_examples = st.text_area("Exemplos (un por liña)")
        
        create_btn = st.form_submit_button("➕ Crear Artista")
        
        if create_btn:
            if not c_name or not c_id:
                st.error("O nome e o ID son obrigatorios.")
            else:
                new_artist = {
                    "id": c_id,
                    "name": c_name,
                    "language": c_lang,
                    "target_audience": c_audience,
                    "base_prompt": c_prompt,
                    "keywords": [k.strip() for k in c_keywords.split(",") if k.strip()],
                    "few_shot_examples": [e.strip() for e in c_examples.split("\n") if e.strip()]
                }
                artists.append(new_artist)
                config["artists"] = artists
                save_config(config)
                st.success(f"Artista {c_name} creado correctamente!")
                st.rerun()

# --- TAB 3: AI ASSISTANT ---
with tab3:
    st.markdown("### 🤖 Xerador de Perfiles con IA")
    st.info("Pega aquí varios textos (captions de Instagram, posts, etc.) do artista e a IA extraerá o seu estilo automaticamente.")
    
    # Initialize session state for AI analysis
    if "ai_analysis_result" not in st.session_state:
        st.session_state.ai_analysis_result = None
    
    ai_name = st.text_input("Nome do Artista")
    ai_lang = st.selectbox("Idioma do Artista", ["Galego", "Español", "English"], key="ai_lang")
    sample_texts = st.text_area("Textos de Exemplo (Pega aquí 5-10 posts recentes)", height=300)
    
    analyze_btn = st.button("✨ Analizar e Xerar Perfil")
    
    if analyze_btn and sample_texts and ai_name:
        with st.spinner("Analizando estilo..."):
            result = analyze_style_with_ai(ai_name, sample_texts, ai_lang)
            if result:
                st.session_state.ai_analysis_result = result
                st.success("Análise completada! Revisa os datos abaixo e garda o perfil.")
            else:
                st.error("Non se puido realizar a análise.")

    # Show form if result exists in session state
    if st.session_state.ai_analysis_result:
        result = st.session_state.ai_analysis_result
        
        st.markdown("---")
        st.markdown("#### 📝 Revisar e Gardar")
        
        with st.form(key="ai_save_form"):
            f_name = st.text_input("Nome", ai_name if ai_name else "Novo Artista")
            # Generate a default ID if not present
            default_id = f_name.lower().replace(" ", "_") if f_name else "novo_id"
            f_id = st.text_input("ID", default_id)
            
            f_lang = st.selectbox("Idioma", ["Galego", "Español", "English"], index=["Galego", "Español", "English"].index(ai_lang))
            f_audience = st.text_area("Audiencia", result.get("target_audience", ""))
            f_prompt = st.text_area("Base Prompt", result.get("base_prompt", ""))
            f_keywords = st.text_area("Keywords", ", ".join(result.get("keywords", [])))
            f_examples = st.text_area("Exemplos", "\n".join(result.get("few_shot_examples", [])))
            
            save_ai_btn = st.form_submit_button("💾 Gardar Novo Perfil")
            
            if save_ai_btn:
                new_artist = {
                    "id": f_id,
                    "name": f_name,
                    "language": f_lang,
                    "target_audience": f_audience,
                    "base_prompt": f_prompt,
                    "keywords": [k.strip() for k in f_keywords.split(",") if k.strip()],
                    "few_shot_examples": [e.strip() for e in f_examples.split("\n") if e.strip()]
                }
                artists.append(new_artist)
                config["artists"] = artists
                if save_config(config):
                    st.success(f"Perfil de {f_name} gardado!")
                    # Clear session state after save
                    st.session_state.ai_analysis_result = None
                    st.switch_page("app.py")
