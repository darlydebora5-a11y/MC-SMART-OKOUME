import streamlit as st
import os
import base64
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- CONFIGURATION (TON ID EST INSÉRÉ ICI) ---
ID_DOSSIER = '1WN7i7bMR4XgYuS-oeHNLUGFI1bWYyntG' 

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide")
logo_b64 = get_base64_file('logo.png')

# --- DESIGN MC SMART (CSS) ---
st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background-color: #002366 !important; color: white; }}
    
    /* BANDE DÉROULANTE ROUGE */
    .marquee-container {{
        background: #FF0000;
        color: white;
        padding: 10px 0;
        font-weight: bold;
        overflow: hidden;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    marquee {{ font-size: 1.2em; }}

    /* LOGO CIRCULAIRE ET CENTRÉ */
    .logo-container {{
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }}
    .circular-logo {{
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #FF0000;
        background: white;
    }}

    /* CARTE BLANCHE CENTRALE */
    .card {{ 
        background: white; 
        padding: 30px; 
        border-radius: 15px; 
        color: #002366; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }}
    
    /* BOUTON ROUGE */
    div.stButton > button {{ 
        width: 100%; 
        background-color: #FF0000 !important; 
        color: white !important; 
        font-weight: bold; 
        border-radius: 8px; 
        height: 3.5em; 
        border: none; 
        font-size: 1.1em;
    }}
    </style>

    <div class="marquee-container">
        <marquee scrollamount="10">🚀 BIENVENUE CHEZ MC SMART OKOUME - IMPRESSION AUTOMATIQUE 24/7 - SERVICE RAPIDE 🚀</marquee>
    </div>
""", unsafe_allow_html=True)

# Affichage du Logo
if logo_b64:
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" class="circular-logo"></div>', unsafe_allow_html=True)

# --- CONNEXION AUTOMATIQUE À GOOGLE DRIVE ---
@st.cache_resource
def connexion_drive():
    gauth = GoogleAuth()
    # Charge les identifiants sauvegardés s'ils existent
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Première connexion : ouvre une fenêtre navigateur
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Rafraîchit le jeton si expiré
        gauth.Refresh()
    else:
        # Autorise la session
        gauth.Authorize()
    # Sauvegarde pour la prochaine fois
    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)

# --- INTERFACE DE DÉPÔT ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Déposez votre document à imprimer")
    doc = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"])
    
    if doc:
        if st.button("LANCER L'IMPRESSION MAINTENANT"):
            with st.spinner("Envoi vers l'imprimante..."):
                try:
                    drive = connexion_drive()
                    # Création du fichier directement dans ton dossier Drive
                    file_drive = drive.CreateFile({
                        'title': doc.name,
                        'parents': [{'id': ID_DOSSIER}]
                    })
                    # On place le contenu du fichier uploadé
                    file_drive.content = doc
                    file_drive.Upload()
                    
                    st.balloons()
                    st.success("✅ C'est fait ! Votre document arrive sur l'imprimante au comptoir.")
                except Exception as e:
                    st.error(f"Détail de l'erreur : {e}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center><small>MC SMART SYSTEM v3.0 - Cloud Print Ready</small></center>", unsafe_allow_html=True)
