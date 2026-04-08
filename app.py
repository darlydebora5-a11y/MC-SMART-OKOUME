import streamlit as st
import uuid
import subprocess
import os
import time
import pandas as pd
import base64
import fitz  # PyMuPDF
import qrcode
import socket
from io import BytesIO
from datetime import datetime
from PIL import Image

# --- 🛡️ CONFIGURATION MC SMART OKOUME ---
TEMP_DIR = "print_queue"
ADS_DIR = "ads"
LOG_FILE = "historique_impressions.csv"
ADMIN_PASSWORD = "admin123" 
PRIX_NB, PRIX_COULEUR = 100, 200

# --- 🔍 FONCTION POUR RÉCUPÉRER L'IP (Sert surtout en local) ---
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# --- 🔍 DÉTECTION LOGICIELS (ADAPTÉ LINUX/CLOUD) ---
# Sur Streamlit Cloud, si vous créez un fichier packages.txt avec "libreoffice", 
# la commande est simplement "soffice"
LIBREOFFICE_PATH = "soffice" 

# --- 🛠️ FONCTIONS UTILES ---
def auto_reparation():
    if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
    if not os.path.exists(ADS_DIR): os.makedirs(ADS_DIR)
    if not os.path.exists(LOG_FILE): 
        pd.DataFrame(columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"]).to_csv(LOG_FILE, index=False)

def convertir_en_pdf(input_path):
    if input_path.lower().endswith(".pdf"): return input_path
    try:
        # Commande Linux pour LibreOffice (installé via packages.txt)
        subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", TEMP_DIR, input_path], check=True)
        nom_base = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(TEMP_DIR, nom_base + ".pdf")
    except Exception as e:
        st.error(f"Erreur de conversion : {e}")
        return None

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- 🎨 INITIALISATION UI ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide")
auto_reparation()

# Tentative de récupération des médias (ne pas planter si absents)
video_b64 = get_base64_file("video.mp4")
logo_raw = get_base64_file("logo.png")
logo_b64 = f"data:image/png;base64,{logo_raw}" if logo_raw else ""

# --- 🖌️ STYLE CSS ---
st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: transparent !important; }}
    #bgVideo {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; object-fit: cover; filter: brightness(0.4) blur(4px); }}
    .marquee-container {{ background: #FF0000; color: white; padding: 8px 0; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }}
    .marquee-text {{ display: inline-block; white-space: nowrap; animation: marquee 25s linear infinite; font-weight: bold; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .white-bar {{ background: white; height: 100px; width: 100%; position: fixed; top: 35px; left: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; }}
    
    div.stButton > button {{ 
        border-radius: 50% !important; height: 150px !important; width: 150px !important; 
        font-weight: 900 !important; border: 3px solid white !important; 
        background: linear-gradient(145deg, #39B54A, #2E8B3D) !important; color: white !important; 
    }}
    </style>
""", unsafe_allow_html=True)

if video_b64:
    st.markdown(f'<video autoplay muted loop playsinline id="bgVideo"><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>', unsafe_allow_html=True)

st.markdown('<div class="marquee-container"><div class="marquee-text">🚀 MC SMART OKOUME : Système autonome d\'impression. Propriété exclusive de M. MPIGA OKOUMBA MC FRINCK.</div></div>', unsafe_allow_html=True)
if logo_b64:
    st.markdown(f'<div class="white-bar"><img src="{logo_b64}" style="height:85px;"></div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:165px;"></div><h1 style="text-align:center; color:#FFCC00; font-size:55px; text-shadow: 2px 2px 4px #000000;">MC SMART OKOUME</h1>', unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = "upload"

tab_client, tab_admin = st.tabs(["📲 CLIENT", "🔐 ADMIN"])

with tab_client:
    if st.session_state.step == "upload":
        f = st.file_uploader("DÉPOSER FICHIER", type=["pdf", "png", "jpg", "docx", "xlsx"], label_visibility="collapsed")
        if f:
            p_init = os.path.join(TEMP_DIR, f.name)
            with open(p_init, "wb") as t: t.write(f.getbuffer())
            p_pdf = convertir_en_pdf(p_init)
            if p_pdf:
                doc = fitz.open(p_pdf)
                nb_c, mat = 0, fitz.Matrix(0.1, 0.1)
                for pg in doc:
                    pix = pg.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    if any(abs(r-g)>18 or abs(r-b)>18 for r,g,b in img.getdata()): nb_c += 1
                st.session_state.nb_c, st.session_state.nb_g, st.session_state.pdf_path, st.session_state.step = nb_c, len(doc)-nb_c, p_pdf, "choix"
                st.rerun()

    elif st.session_state.step == "choix":
        tot = st.session_state.nb_c + st.session_state.nb_g
        st.write(f"📄 {tot} Page(s) détectée(s)")
        if st.button("Recommencer"):
            st.session_state.step = "upload"
            st.rerun()

with tab_admin:
    pwd = st.text_input("Mot de passe", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Accès autorisé")
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
            st.dataframe(df)
