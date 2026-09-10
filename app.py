
import streamlit as st
import google.generativeai as genai
from google.colab import userdata
import PIL.Image
import io
import datetime # Importation de datetime

st.set_page_config(
    page_title="Gemini Multimédia Chat",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("💬 Gemini Multimédia Chat")

# --- Configuration de l'API Gemini ---
# Assurez-vous d'avoir enregistré votre clé API Gemini sous le nom 'GEMINI_API_KEY' dans les secrets Colab.
api_key = userdata.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

system_instruction = "Tu es une intelligence artificielle générale d’excellence, polyvalente, extrêmement cultivée et douée d’une capacité d’analyse exceptionnelle. Tu réponds à absolument n’importe quelle question avec une précision chirurgicale, une logique implacable et une clarté cristalline."

# Initialiser le modèle avec l'instruction système et le modèle recommandé
# (gemini-3.6-flash est utilisé car gemini-2.5-flash est déprécié)
model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=system_instruction
)

# --- Barre latérale ---
with st.sidebar:
    st.header("Configuration du Chat") # Titre de la barre latérale
    st.markdown("--- # ---")
    st.write("Gérez votre session de chat et exportez l'historique.") # Description
    st.markdown("--- # ---")

    if st.button("Effacer la conversation / Nouvelle session"): # Ajout du bouton
        st.session_state.chat_history = []  # Réinitialise l'historique du chat
        # Crée une nouvelle session de chat pour Gemini
        st.session_state.gemini_chat = model.start_chat(history=[])
        # Réinitialise la date de début pour la nouvelle session
        st.session_state.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.experimental_rerun() # Force la mise à jour de l'application

    st.markdown("--- # ---") # Séparateur visuel

    # --- Bouton 'Exporter la conversation' dans la barre latérale ---
    if "chat_history" in st.session_state and st.session_state.chat_history: # Afficher le bouton seulement s'il y a de l'historique
        # Fonction pour formater l'historique en texte
        def format_chat_history_for_export(history):
            formatted_text = []
            formatted_text.append("--- Historique de la conversation Gemini ---")
            formatted_text.append(f"Date d'exportation : {st.session_state.get('start_time', 'N/A')}")
            formatted_text.append("------------------------------------------")

            for i, message in enumerate(history):
                # S'assurer que 'role' et 'parts' existent, sinon utiliser des valeurs par défaut
                role = message.get('role', 'user')
                parts = message.get('parts', [])

                display_content = []
                for part in parts:
                    if isinstance(part, str):
                        display_content.append(part)
                    elif isinstance(part, PIL.Image.Image):
                        display_content.append("[IMAGE: Contenu visuel non exportable en texte pur]")
                    elif isinstance(part, dict) and 'text' in part:
                        display_content.append(part['text'])
                    elif isinstance(part, dict) and 'inline_data' in part:
                        display_content.append("[IMAGE_DATA: Contenu visuel non exportable en texte pur]")

                speaker = "Utilisateur" if role == "user" else "Gemini"
                formatted_text.append(f"\n{speaker}: {' '.join(display_content)}")

            formatted_text.append("\n--- Fin de l'historique ---")
            return "\n".join(formatted_text)

        export_data = format_chat_history_for_export(st.session_state.chat_history)
        st.download_button(
            label="Exporter la conversation (TXT)",
            data=export_data,
            file_name="gemini_chat_history.txt",
            mime="text/plain"
        )

# --- Gestion de l'historique du chat avec st.session_state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Démarrer une nouvelle session de chat si l'historique est vide
    st.session_state.gemini_chat = model.start_chat(history=[])
    st.session_state.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
elif "gemini_chat" not in st.session_state:
    # Recréer la session de chat avec l'historique existant si nécessaire
    st.session_state.gemini_chat = model.start_chat(history=st.session_state.chat_history)
# Initialiser start_time si ce n'est pas déjà fait (pour les sessions existantes qui n'ont pas encore de start_time)
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Affichage de l'historique du chat ---
for message in st.session_state.chat_history:
    role = message.get('role', 'user') # Supposons 'user' par défaut si le rôle n'est pas spécifié
    parts = message.get('parts', [])

    # Convertir les parties en un format affichable
    display_content = []
    with st.chat_message(role):
        for part in parts:
            if isinstance(part, str):
                display_content.append(part)
            elif isinstance(part, PIL.Image.Image):
                st.image(part, caption="Image envoyée", width=200)
            elif isinstance(part, dict) and 'text' in part:
                display_content.append(part['text'])
            elif isinstance(part, dict) and 'inline_data' in part:
                # Gérer les images encodées en base64 si elles proviennent de l'historique du modèle
                pass # Streamlit ne gère pas directement l'affichage de inline_data
        if display_content:
            st.write(" ".join(display_content))


# --- Entrée utilisateur et soumission ---
user_input = st.chat_input("Écrivez votre message ici...")
uploaded_file = st.file_uploader("Ou téléchargez une image", type=["jpg", "jpeg", "png", "gif"])

# Gérer l'envoi du message
if user_input or uploaded_file is not None:
    # Construire le contenu à envoyer au modèle
    content_to_send = []
    if uploaded_file is not None:
        image_data = uploaded_file.read()
        image = PIL.Image.open(io.BytesIO(image_data))
        content_to_send.append(image)
        with st.chat_message("user"):
            st.image(image, caption=uploaded_file.name, width=200)

    if user_input:
        content_to_send.append(user_input)
        with st.chat_message("user"):
            st.write(user_input)

    if content_to_send:
        # Ajouter le message utilisateur à l'historique
        st.session_state.chat_history.append({"role": "user", "parts": content_to_send})

        with st.spinner("Gemini réfléchit..."):
            response = st.session_state.gemini_chat.send_message(content_to_send)

        # Ajouter la réponse de Gemini à l'historique
        st.session_state.chat_history.append({"role": "model", "parts": [response.text]})

        with st.chat_message("model"):
            st.write(response.text)

        # Pour forcer le re-rendu et afficher le nouvel historique
        st.experimental_rerun()
