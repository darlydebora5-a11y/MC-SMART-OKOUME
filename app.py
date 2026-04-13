import streamlit as st
import uuid
import os
import time
from datetime import datetime
from supabase import create_client

# --- CONFIGURATION ---
URL = "https://supabase.co"
KEY = "sb_secret_9wMSGX3Mb0Q4uuFmunBopQ_y1QFnlCc"
supabase = create_client(URL, KEY)

# Fonction pour envoyer le fichier au "Cloud" pour que ton PC le récupère
def envoyer_a_l_imprimante_distance(file_path):
    try:
        nom_unique = f"{uuid.uuid4()}.pdf"
        
        # 1. On envoie le fichier dans le dossier 'impressions' de Supabase
        with open(file_path, "rb") as f:
            supabase.storage.from_("impressions").upload(nom_unique, f.read())
        
        # 2. On crée une alerte dans la table pour dire au robot local d'imprimer
        data = {"nom_fichier": nom_unique, "statut": "en_attente"}
        supabase.table("commandes_impression").insert(data).execute()
        
        return True
    except Exception as e:
        st.error(f"Erreur d'envoi : {e}")
        return False

# --- DANS TON INTERFACE (Exemple d'utilisation) ---
st.title("MC SMART - Impression")
uploaded_file = st.file_uploader("Choisissez votre document")

if uploaded_file:
    # Sauvegarde temporaire pour l'envoi
    temp_path = os.path.join("print_queue", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Lancer l'impression automatique"):
        with st.spinner("Envoi en cours..."):
            succes = envoyer_a_l_imprimante_distance(temp_path)
            if succes:
                st.success("✅ Document reçu ! L'imprimante va démarrer toute seule.")
