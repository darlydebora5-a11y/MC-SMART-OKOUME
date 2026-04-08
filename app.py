import streamlit as st
import uuid
import subprocess
import os
import time
import pandas as pd
import base64
import fitz  # PyMuPDF
import qrcode
from datetime import datetime
from PIL import Image
from supabase import create_client

# --- 🛡️ CONFIGURATION MC SMART OKOUME ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_8c3T0LRymg5L7hG8uv1UtA_p1wm3l7_"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TEMP_DIR = "print_queue"
ADS_DIR = "ads"
LOG_FILE = "historique_impressions.csv"
ADMIN_PASSWORD = "admin123" 
PRIX_NB, PRIX_COULEUR = 100, 200

# --- 🔍 FONCTIONS RÉCUPÉRÉES ---
def auto_reparation():
    for d in [TEMP_DIR, ADS_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    if not os.path.exists(LOG_FILE): 
        pd.DataFrame(columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"]).to_csv(LOG_FILE, index=False)

def convertir_en_pdf(input_path):
    if input_path.lower().endswith(".pdf"): return input_path
    try:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", TEMP_DIR, input_path], check=True)
        time.sleep(1)
        return os.path.join(TEMP_DIR, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    except: return None

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- 🎨 INITIALISATION UI (DESIGN ORIGINAL) ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide", page_icon="logo.png")
auto_reparation()

video_b64 = get_base64_file("video.mp4")
logo_b64 = f"data:image/png;base64,{get_base64_file('logo.png')}"

st.markdown(f"""
    <style>
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background-color: #002366 !important; }}
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
    div.stButton > button[key="btn_print_final"] {{
        border-radius: 20px !important; height: 120px !important; width: 100% !important; 
        background-color: #FF0000 !important; font-size: 35px !important;
        animation: blinker 0.8s linear infinite !important; border: 8px solid white !important;
    }}
    @keyframes blinker {{ 50% {{ opacity: 0.5; background-color: #990000; }} }}
    </style>
""", unsafe_allow_html=True)

if video_b64:
    st.markdown(f'<video autoplay muted loop playsinline id="bgVideo"><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>', unsafe_allow_html=True)

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
                nb_c = 0
                mat = fitz.Matrix(0.1, 0.1)
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
        st.markdown(f'<h1 style="text-align:center; color:white; font-size:60px;">{st.session_state.final_m} FCFA</h1>', unsafe_allow_html=True)
        if st.button("LANCER L'IMPRESSION", key="btn_print_final"):
            try:
                unique_name = f"{uuid.uuid4().hex[:8]}.pdf"
                with open(st.session_state.pdf_path, 'rb') as f:
                    # TESTER LE NOM DU BUCKET EN MINUSCULES SI LES MAJUSCULES ÉCHOUENT
                    try:
                        supabase.storage.from_('IMPRESSIONS').upload(path=unique_name, file=f)
                    except:
                        f.seek(0)
                        supabase.storage.from_('impressions').upload(path=unique_name, file=f)
                
                st.success("✅ Envoyé au Cloud !")
                time.sleep(2)
                st.session_state.step = "upload"
                st.rerun()
            except Exception as e:
                st.error(f"Détail technique de l'erreur : {e}")

with tab_admin:
    pwd = st.text_input("Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        if os.path.exists(LOG_FILE): st.dataframe(pd.read_csv(LOG_FILE))
