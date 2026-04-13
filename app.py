import streamlit as st
import uuid
import os
import time
import base64
from datetime import datetime
from supabase import create_client

# --- CONFIGURATION (Vérifie bien ces deux valeurs dans Project Settings > API) ---
URL = "https://supabase.co" 
KEY = "sb_secret_9wMSGX3Mb0Q4uuFmunBopQ_y1QFnlCc" # Utilise la 'service_role' key
supabase = create_client(URL, KEY)

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- FONCTION D'ENVOI AU ROBOT ---
def envoyer_au_robot(file_obj, original_name):
    try:
        # Création d'un nom unique pour éviter les doublons
        extension = os.path.splitext(original_name)[1]
        nom_unique = f"{int(time.time())}_{uuid.uuid4().hex[:5]}{extension}"
        
        # 1. Upload dans le Bucket 'impressions'
        supabase.storage.from_("impressions").upload(nom_unique, file_obj.getvalue())
        
        # 2. Enregistrement dans la table que tu viens de créer
        data = {"nom_fichier": nom_unique, "statut": "en_attente"}
        supabase.table("commandes_impression").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur technique : {e}")
        return False

# --- DESIGN MC SMART ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide")
logo_b64 = get_base64_file('logo.png')

st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background-color: #002366 !important; color: white; }}
    .marquee {{ background: #FF0000; color: white; padding: 10px; font-weight: bold; text-align: center; border-radius: 10px; }}
    .card {{ background: white; padding: 30px; border-radius: 15px; color: #002366; margin-top: 20px; }}
    div.stButton > button {{ width: 100%; background-color: #FF0000 !important; color: white !important; font-weight: bold; border-radius: 8px; border: none; height: 3.5em; }}
    </style>
    <div class="marquee">🚀 MC SMART OKOUME - IMPRESSION AUTOMATIQUE 🚀</div>
""", unsafe_allow_html=True)

if logo_b64:
    st.image(f"data:image/png;base64,{logo_b64}", width=120)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Déposez votre document")
    doc = st.file_uploader("", type=["pdf", "png", "jpg", "docx"])
    
    if doc:
        st.info(f"Fichier prêt : {doc.name}")
        if st.button("LANCER L'IMPRESSION"):
            with st.spinner("Envoi au comptoir..."):
                if envoyer_au_robot(doc, doc.name):
                    st.balloons()
                    st.success("✅ Reçu ! L'impression démarre toute seule.")
    st.markdown('</div>', unsafe_allow_html=True)
