import os
import time
import subprocess

# CHEMIN DE TON DOSSIER GOOGLE DRIVE SUR TON PC
# Exemple : "C:/Users/TonNom/Google Drive/Mon Drive/Impressions_MC_Smart"
WATCH_DIR = r"METS_ICI_LE_CHEMIN_DE_TON_DOSSIER_DRIVE"

print("🤖 ROBOT MC SMART (DRIVE SYNC) ACTIF...")

while True:
    # Liste les fichiers dans le dossier
    files = [f for f in os.listdir(WATCH_DIR) if os.path.isfile(os.path.join(WATCH_DIR, f))]
    
    for file_name in files:
        file_path = os.path.join(WATCH_DIR, file_name)
        
        print(f"🖨️ Impression automatique de : {file_name}")
        
        # Commande Windows pour imprimer
        os.startfile(file_path, "print")
        
        # Attendre 10 secondes pour laisser l'imprimante travailler
        time.sleep(10)
        
        # Déplacer ou supprimer le fichier pour ne pas le réimprimer
        # Ici on le supprime (il restera dans la corbeille de Google Drive au cas où)
        try:
            os.remove(file_path)
            print(f"✅ Nettoyage terminé.")
        except:
            pass

    time.sleep(5) # Vérifie toutes les 5 secondes
