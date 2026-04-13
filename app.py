import streamlit as st
import os
import base64
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- DESIGN MC SMART ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide")

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64_file('logo.png')

# Style CSS Original
st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background-color: #002366 !important; color: white; }}
    .marquee-container {{ background: #FF0000; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; overflow: hidden; }}
    .logo-container {{ display: flex; justify-content: center; margin: 20px 0; }}
    .circular-logo {{ width: 150px; height: 150px; border-radius: 50%; border: 4px solid #FF0000; background: white; object-fit: cover; }}
    .card {{ background: white; padding: 30px; border-radius: 15px; color: #002366; }}
    div.stButton > button {{ width: 100%; background-color: #FF0000 !important; color: white !important; font-weight: bold; border-radius: 8px; height: 3.5em; border: none; }}
    </style>
    <div class="marquee-container"><marquee>🚀 MC SMART OKOUME - IMPRESSION AUTOMATIQUE 24/7 🚀</marquee></div>
""", unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" class="circular-logo"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Déposez votre document")
    uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg"])

    if uploaded_file:
        if st.button("LANCER L'IMPRESSION"):
            try:
                # Authentification Google Drive
                gauth = GoogleAuth()
                # Charge les credentials ou ouvre une fenêtre de connexion au premier lancement
                gauth.LocalWebserverAuth() 
                drive = GoogleDrive(gauth)

                # Sauvegarde temporaire
                temp_name = uploaded_file.name
                with open(temp_name, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Envoi dans le dossier spécifique (ID du dossier 'Impressions_MC_Smart')
                # Remplace 'TON_ID_DE_DOSSIER' par l'ID visible dans l'URL de ton dossier sur ton navigateur
                file_drive = drive.CreateFile({
                    'title': temp_name,
                    'parents': [{'id': 'TON_ID_DE_DOSSIER_ICI'}] 
                })
                file_drive.SetContentFile(temp_name)
                file_drive.Upload()

                st.success("✅ Document envoyé ! L'imprimante va démarrer.")
                os.remove(temp_name)
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
    st.markdown('</div>', unsafe_allow_html=True)
