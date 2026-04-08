import time
import os
import win32api
from supabase import create_client

# --- 🛡️ CONFIGURATION AGENT MC ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_secret_9wMSGX3Mb0Q4uuFmunBopQ_y1QFnlCc" # TA CLÉ SECRÈTE
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🚀 AGENT MC SMART OKOUME - SURVEILLANCE ACTIVE...")

while True:
    try:
        # On vérifie ton dossier IMPRESSIONS
        files = supabase.storage.from_('IMPRESSIONS').list()
        
        for f in files:
            nom_fichier = f['name']
            if nom_fichier == ".emptyFolderPlaceholder": continue
            
            print(f"📥 Nouveau document trouvé : {nom_fichier}")
            
            # 1. Télécharger
            with open(nom_fichier, 'wb') as local_file:
                res = supabase.storage.from_('IMPRESSIONS').download(nom_fichier)
                local_file.write(res)
            
            # 2. Imprimer (Ton module win32api original)
            win32api.ShellExecute(0, "print", nom_fichier, None, ".", 0)
            
            # 3. Nettoyer
            time.sleep(5)
            supabase.storage.from_('IMPRESSIONS').remove([nom_fichier])
            os.remove(nom_fichier)
            print("✅ Impression lancée et Cloud nettoyé.")

    except Exception as e:
        pass
    
    time.sleep(10)
