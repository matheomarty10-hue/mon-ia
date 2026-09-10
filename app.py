import streamlit as st
from google import genai
from PIL import Image
import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="Nexus AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("⚡ Nexus AI")

# --- Configuration de l'API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("⚠️ Clé API Gemini introuvable. Veuillez l'ajouter dans les secrets de l'application Streamlit.")
    st.stop()

# Configuration du modèle
model_id = "gemini-2.5-flash"

system_instruction = "Tu es une intelligence artificielle generale d'excellence, polyvalente, extremement cultivee et dotee d'une capacite d'analyse exceptionnelle. Tu reponds a n'importe quelle question avec une precision chirurgicale."

# --- Barre Laterale ---
with st.sidebar:
    st.header("⚙️ Configuration du Chat")
    
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.chat_history = []
        st.session_state.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()

# --- Initialisation de l'historique ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Creation de la session de chat Google GenAI
chat = client.chats.create(
    model=model_id,
    config={
        "system_instruction": system_instruction,
    }
)

# --- Affichage du chat ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Saisie utilisateur ---
prompt = st.chat_input("Pose ta question a l'IA...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Reponse de l'assistant
    with st.chat_message("assistant"):
        with st.spinner("Reflexion en cours..."):
            try:
                response = chat.send_message(prompt)
                bot_reply = response.text
                
                st.markdown(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API : {e}")
