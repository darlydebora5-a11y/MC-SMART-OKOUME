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

# --- 🛠️ FONCTIONS ---
def auto_reparation():
    for d in [TEMP_DIR, ADS_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    if not os.path.exists(LOG_FILE): 
        pd.DataFrame(columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"]).to_csv(LOG_FILE, index=False)

def convertir_en_pdf(input_path):
    if input_path.lower().endswith(".pdf"): return input_path
    try:
        # Sur Streamlit Cloud, on utilise LibreOffice installé via packages.txt
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", TEMP_DIR, input_path], check=True)
        time.sleep(1)
        nom_base = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(TEMP_DIR, nom_base + ".pdf")
    except: return None

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- 🎨 INITIALISATION UI ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide")
auto_reparation()

logo_raw = get_base64_file("logo.png")
logo_b64 = f"data:image/png;base64,{logo_raw}" if logo_raw else ""

# --- 🖌️ STYLE CSS (AVEC LOGO EN FOND) ---
st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{
        background-image: url("{logo_b64}");
        background-repeat: no-repeat; background-attachment: fixed;
        background-position: center; background-size: 30%; background-color: #1E1E1E !important;
    }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0, 0, 0, 0.7); z-index: -1;
    }}
    .marquee-container {{ background: #FF0000; color: white; padding: 8px 0; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }}
    .marquee-text {{ display: inline-block; white-space: nowrap; animation: marquee 25s linear infinite; font-weight: bold; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .white-bar {{ background: white; height: 100px; width: 100%; position: fixed; top: 35px; left: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; }}
    
    div.stButton > button {{ 
        border-radius: 50% !important; height: 150px !important; width: 150px !important; 
        font-weight: 900 !important; border: 3px solid white !important; 
        background: linear-gradient(145deg, #39B54A, #2E8B3D) !important; color: white !important; 
    }}
    div.stButton > button[key="btn_print_final"] {{
        border-radius: 20px !important; height: 100px !important; width: 100% !important; 
        background-color: #FF0000 !important; font-size: 30px !important; border: 5px solid white !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="marquee-container"><div class="marquee-text">🚀 MC SMART OKOUME : Système autonome d\'impression. Propriété exclusive de M. MPIGA OKOUMBA MC FRINCK.</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="white-bar"><img src="{logo_b64}" style="height:85px;"></div>', unsafe_allow_html=True)
st.markdown('<div style="margin-top:165px;"></div><h1 style="text-align:center; color:#FFCC00; font-size:55px;">MC SMART OKOUME</h1>', unsafe_allow_html=True)

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
        st.markdown(f'<div style="background:rgba(0,0,0,0.6); padding:20px; text-align:center; font-size:24px; border-radius:15px; color: white;">📄 {tot} Page(s) ({st.session_state.nb_g} N/B, {st.session_state.nb_c} Couleur)</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button(f"N/B\n{tot*PRIX_NB}F"): 
            st.session_state.final_m, st.session_state.type_p, st.session_state.step = tot*PRIX_NB, "NB", "impression"
            st.rerun()
        if c2.button(f"COULEUR\n{tot*PRIX_COULEUR}F"): 
            st.session_state.final_m, st.session_state.type_p, st.session_state.step = tot*PRIX_COULEUR, "COULEUR", "impression"
            st.rerun()
        mix = (st.session_state.nb_g*PRIX_NB)+(st.session_state.nb_c*PRIX_COULEUR)
        if c3.button(f"MIXTE\n{mix}F"): 
            st.session_state.final_m, st.session_state.type_p, st.session_state.step = mix, "MIXTE", "impression"
            st.rerun()

    elif st.session_state.step == "impression":
        st.markdown(f'<h2 style="text-align:center; color:white;">TOTAL À PAYER : {st.session_state.final_m} F</h2>', unsafe_allow_html=True)
        if st.button("LANCER L'IMPRESSION", key="btn_print_final"):
            st.success("Demande d'impression enregistrée ! (Simulation sur Cloud)")
            # Ici on enregistre dans le log au lieu de win32print
            new_log = pd.DataFrame([[str(uuid.uuid4())[:8], datetime.now().strftime("%H:%M"), os.path.basename(st.session_state.pdf_path), st.session_state.nb_c + st.session_state.nb_g, st.session_state.type_p, st.session_state.final_m, "En attente"]], columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"])
            df_logs = pd.read_csv(LOG_FILE)
            pd.concat([df_logs, new_log]).to_csv(LOG_FILE, index=False)
            time.sleep(3)
            st.session_state.step = "upload"
            st.rerun()

with tab_admin:
    pwd = st.text_input("Admin", type="password")
    if pwd == ADMIN_PASSWORD:
        st.dataframe(pd.read_csv(LOG_FILE))
