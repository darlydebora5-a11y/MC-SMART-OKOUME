import streamlit as st
import uuid
import subprocess
import os
import time
import pandas as pd
import base64
import fitz  # PyMuPDF
import win32api
import win32print
import qrcode
import socket # Pour détecter l'IP automatiquement
from io import BytesIO
from datetime import datetime
from PIL import Image

# --- 🛡️ CONFIGURATION MC SMART OKOUME ---
TEMP_DIR = "print_queue"
ADS_DIR = "ads"
LOG_FILE = "historique_impressions.csv"
ADMIN_PASSWORD = "admin123" 
PRIX_NB, PRIX_COULEUR = 100, 200

# --- 🔍 FONCTION POUR RÉCUPÉRER L'IP RÉSEAU AUTOMATIQUEMENT ---
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

current_ip = get_ip_address()
client_url = f"http://{current_ip}:8501"

# --- 🔍 DÉTECTION LOGICIELS ---
def trouver_logiciel(nom_exe, chemins):
    for c in chemins:
        if os.path.exists(c): return c
    return None

LIBREOFFICE_PATH = trouver_logiciel("soffice.exe", [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    r"C:\LibreOffice\program\soffice.exe"
])

SUMATRA_PATH = trouver_logiciel("SumatraPDF.exe", [
    r"C:\Users\\" + os.getlogin() + r"\AppData\Local\SumatraPDF\SumatraPDF.exe",
    r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
    r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe"
])

# --- 🛠️ FONCTIONS UTILES ---
def auto_reparation():
    for d in [TEMP_DIR, ADS_DIR]:
        if not os.path.exists(d): os.makedirs(d)
    if not os.path.exists(LOG_FILE): 
        pd.DataFrame(columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"]).to_csv(LOG_FILE, index=False)

def convertir_en_pdf(input_path):
    if input_path.lower().endswith(".pdf"): return input_path
    if not LIBREOFFICE_PATH: return None
    try:
        nom_base = os.path.splitext(os.path.basename(input_path))[0]
        subprocess.run([LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", "--outdir", TEMP_DIR, input_path], check=True)
        time.sleep(1)
        return os.path.join(TEMP_DIR, nom_base + ".pdf")
    except: return None

def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def generer_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- 🎨 INITIALISATION UI ---
st.set_page_config(page_title="MC SMART OKOUME", layout="wide", page_icon="logo.png")
auto_reparation()

# Récupération des médias
video_b64 = get_base64_file("video.mp4")
logo_b64 = f"data:image/png;base64,{get_base64_file('logo.png')}"

# --- 🖌️ STYLE CSS (SANS LA VIDEO DEDANS) ---
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
    div.stButton > button[key="btn_print_final"] {{
        border-radius: 20px !important; height: 150px !important; width: 100% !important; 
        background-color: #FF0000 !important; font-size: 40px !important;
        animation: blinker 0.6s linear infinite !important; border: 8px solid white !important;
    }}
    @keyframes blinker {{ 50% {{ opacity: 0.5; background-color: #990000; }} }}
    </style>
""", unsafe_allow_html=True)

# --- 📽️ INJECTION DE LA VIDEO SEULE (POUR ÉVITER LES BUGS) ---
if video_b64:
    st.markdown(f"""
        <video autoplay muted loop playsinline id="bgVideo">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

st.markdown('<div class="marquee-container"><div class="marquee-text">🚀 MC SMART OKOUME : Système autonome d\'impression. Propriété exclusive de M. MPIGA OKOUMBA MC FRINCK.</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="white-bar"><img src="{logo_b64}" style="height:85px;"></div>', unsafe_allow_html=True)
st.markdown('<div style="margin-top:165px;"></div><h1 style="text-align:center; color:#FFCC00; font-size:55px; text-shadow: 2px 2px 4px #000000;">MC SMART OKOUME</h1>', unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = "upload"

tab_client, tab_admin = st.tabs(["📲 CLIENT", "🔐 ADMIN"])

with tab_client:
    with st.expander("📲 INSTALLER L'APPLICATION SUR VOTRE ÉCRAN"):
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.6); padding: 15px; border-radius: 10px; color: white; border: 2px solid #39B54A; text-align: center;">
                <p>Pour revenir plus vite la prochaine fois, ajoutez cette page à votre écran d'accueil :</p>
                <div style="display: flex; justify-content: space-around; font-size: 14px;">
                    <div style="width: 45%;"><b>ANDROID :</b> Menu ⋮ > <b>Ajouter à l'écran d'accueil</b></div>
                    <div style="width: 45%;"><b>IPHONE :</b> Partager ⎋ > <b>Sur l'écran d'accueil</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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
        st.markdown(f'<div style="background:rgba(0,0,0,0.6); padding:20px; text-align:center; font-size:24px; border-radius:15px; border:2px solid white; color: white;">📄 {tot} Page(s) ({st.session_state.nb_g} N/B, {st.session_state.nb_c} Couleur)</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div style="text-align:center; font-size:30px; margin-bottom:20px; color: white; font-weight: bold; background:rgba(0,0,0,0.6); border-radius:10px; padding:10px;">TOTAL : {st.session_state.final_m} FCFA</div>', unsafe_allow_html=True)
        if st.button("CLIC ICI POUR IMPRIMER", key="btn_print_final"):
            try:
                f_path = os.path.abspath(st.session_state.pdf_path)
                p_name = win32print.GetDefaultPrinter()
                args = [SUMATRA_PATH, "-print-to", p_name, "-silent"]
                if st.session_state.type_p == "NB": 
                    args.extend(["-print-settings", "monochrome"])
                args.append(f_path)
                
                if SUMATRA_PATH: subprocess.run(args, check=True)
                else: win32api.ShellExecute(0, "print", f_path, None, ".", 0)
                
                new_log = pd.DataFrame([[str(uuid.uuid4())[:8], datetime.now().strftime("%Y-%m-%d %H:%M"), os.path.basename(f_path), st.session_state.nb_c + st.session_state.nb_g, st.session_state.type_p, st.session_state.final_m, "Succès"]], columns=["ID", "Heure", "Fichier", "Pages", "Type", "Montant", "Statut"])
                new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)
                
                st.success("Impression lancée !")
                st.session_state.step = "upload"
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

with tab_admin:
    pwd_val = st.text_input("Mot de passe administrateur", type="password")
    if pwd_val == ADMIN_PASSWORD:
        st.markdown("<h2 style='text-align: center; color: white;'>⚙️ PANNEAU DE CONTRÔLE</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #39B54A;'>IP Active : {current_ip}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h3 style='text-align: center; color: white;'>📲 ACCÈS CLIENT (QR CODE)</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            qr_data = generer_qr_code(client_url)
            st.image(qr_data, use_container_width=True)
            st.download_button("Code QR Télécharger", data=qr_data, file_name="qr.png", mime="image/png", use_container_width=True)
        st.divider()
        if os.path.exists(LOG_FILE):
            st.dataframe(pd.read_csv(LOG_FILE).tail(15), use_container_width=True)
