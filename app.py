import streamlit as st
from google import genai

st.set_page_config(
    page_title="Nexus AI",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Nexus AI")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Cle API introuvable dans les secrets.")
    st.stop()

model_id = "gemini-2.5-flash"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Reflexion..."):
            try:
                # Utilisation d'un appel direct sans historique complexe pour eviter tout bug d'encodage
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                )
                bot_reply = response.text
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Erreur API : {e}")
