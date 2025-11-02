import fdb
import os
import re
import zlib
import magic
import logging
import pandas as pd

# CONFIGURATION
DOSSIER_FDB = "E:/FICHIERS/Pascal/FDB_50/VOLS_50"
FIREBIRD_CLIENT_PATH = "E:/FICHIERS/Pascal/FDB_50/Firebird-2.5.9.27139-0_x64_embed/fbclient.dll"
resultats = []
echecs_details = []
erreurs_connexion = []
erreurs_tables = []
erreurs_requete = []

# Init logging
logging.basicConfig(
    filename='extraction_novaxel_global.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Init Firebird client
fdb.load_api(FIREBIRD_CLIENT_PATH)

def nettoyer_nom_fichier(nom):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', str(nom))

def lister_tables(connexion):
    try:
        cur = connexion.cursor()
        cur.execute("SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0")
        tables = [row[0].strip() for row in cur.fetchall()]
        cur.close()
        return tables
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des tables : {e}")
        return []

def traiter_fichier_fdb(fichiervol_path):
    base_name = os.path.basename(fichiervol_path)
    num_vol = base_name[5:8]

    try:
        con = fdb.connect(dsn=fichiervol_path, user="SYSDBA", password="masterkey", charset="NONE")
        tables_disponibles = lister_tables(con)
        logging.info(f"[{base_name}] Tables disponibles : {tables_disponibles}")
        print(f"📋 Tables dans {base_name} : {tables_disponibles}")
        with open("tables_fdb.txt", "a", encoding="utf-8") as f_txt:
            f_txt.write(f"{base_name} : {', '.join(tables_disponibles)}\n")
    except Exception as e:
        logging.error(f"[{base_name}] Erreur de connexion : {e}")
        erreurs_connexion.append(base_name)
        return

    nom_table_standard = "TPAGES" + num_vol
    nom_table_alt = "TPAGES" + str(int(num_vol))
    nom_table = None

    if nom_table_standard in tables_disponibles:
        nom_table = nom_table_standard
    elif nom_table_alt in tables_disponibles:
        nom_table = nom_table_alt
    else:
        logging.warning(f"[{base_name}] Aucune table TPAGES trouvée : ni {nom_table_standard} ni {nom_table_alt}")
        print(f"⚠️ Aucune table TPAGES trouvée dans {base_name}")
        con.close()
        erreurs_tables.append(base_name)
        return

    dossier_sortie = os.path.join("fichier_pdf_html_" + nom_table)
    os.makedirs(dossier_sortie, exist_ok=True)
    print("📂 Début traitement " + str(nom_table))

    try:
        cur = con.cursor()
        cur.execute(f"SELECT IDC, IDC_SEQ, IDI, CETATS, LIB, BLB, XBLB FROM {nom_table}")
        rows = cur.fetchall()
        print(f"🔎 {len(rows)} lignes récupérées depuis {nom_table}")
        if not rows:
            print(f"⚠️ La table {nom_table} est vide dans {base_name}")
            logging.warning(f"[{base_name}] Table {nom_table} vide, aucun fichier à extraire.")
            cur.close()
            con.close()
            return
    except Exception as e:
        logging.error(f"[{base_name}] Erreur de requête : {e}")
        erreurs_requete.append(base_name)
        return

    total, succes, echec = 0, 0, 0
    for idx, row in enumerate(rows, 1):
        try:
            print(f"Traitement ligne {idx}/{len(rows)}")
            idc, IDC_SEQ, IDI, CETATS, LIB, BLB, XBLB = row
            if hasattr(BLB, "read"):
                blob_data = BLB.read()
                BLB.close()
            else:
                blob_data = BLB

            mime = magic.Magic()
            try:
                file_type = mime.from_buffer(blob_data)
            except Exception as e:
                file_type = str(e)

            extension = ".pdf"
            if "bin" in file_type: extension = ".bin"
            elif "vnd.ms-outlook" in file_type: extension = ".html"
            elif "msword" in file_type or "officedocument" in file_type: extension = ".docx"
            elif "jpeg" in file_type.lower(): extension = ".jpg"
            elif "png" in file_type.lower(): extension = ".png"
            elif "tiff" in file_type.lower(): extension = ".tiff"

            lib_net = nettoyer_nom_fichier(LIB)
            if "_MSG" in lib_net: extension = ".html"
            if "_Excel" in lib_net: extension = ".emf"
            if "_Word" in lib_net: extension = ".emf"
            if "_RTF" in lib_net: extension = ".rtf"
            if "_PNG" in lib_net: extension = ".png"
            if "_TIFF" in lib_net: extension = ".tiff"
            if "_))Dos(Id_L)=((vide))" in lib_net:
                if b'ppt/' in blob_data or 'présentation' in lib_net.lower():
                    extension = ".pptx"
                else:
                    extension = ".zip"
            if "_Word.Document." in lib_net: extension = ".pdf"

            try:
                blob_decompresse = zlib.decompress(blob_data)
            except zlib.error:
                blob_decompresse = blob_data

            nom_fichier = os.path.join(
                dossier_sortie,
                f"{nettoyer_nom_fichier(idc)}_{lib_net}_{nettoyer_nom_fichier(IDI)}_{nettoyer_nom_fichier(CETATS)}_{nettoyer_nom_fichier(IDC_SEQ)}{extension}"
            )

            with open(nom_fichier, "wb") as f:
                f.write(blob_decompresse)

            logging.info(f"[{base_name}] ✅ {nom_fichier}")
            succes += 1
            total += 1

        except Exception as err:
            err_msg = str(err)
            if "GPS-Data name use count" in err_msg:
                logging.warning(f"[{base_name}] ⚠️ Avertissement mineur (TIFF GPS) ligne {idx} : {err_msg}")
                continue  # Ne pas enregistrer comme échec bloquant
            logging.error(f"[{base_name}] ❌ Erreur ligne {idx}: {err_msg}")
            echec += 1
            echecs_details.append({
                "IDC": row[0],
                "IDC_SEQ": row[1],
                "IDI": row[2],
                "LIB": row[4],
                "Erreur": err_msg
            })

    cur.close()
    con.close()
    logging.info(f"[{base_name}] Extraction terminée. Total={len(rows)}, Succès={succes}, Échecs={echec}")
    print(f"✔️ Total lignes : {len(rows)}, ✅ Succès : {succes}, ❌ Échecs : {echec}")
    print("📁 Fin traitement " + str(nom_table))
    if echecs_details:
        df_err = pd.DataFrame(echecs_details)
        df_err.to_excel(f"erreurs_extraction_{num_vol}.xlsx", index=False)
        print(f"❗ {len(echecs_details)} erreurs enregistrées dans erreurs_extraction_{num_vol}.xlsx")
    extract_IDI(dossier_sortie)

def extract_IDI(repertoire):
    pattern = re.compile(r'=\(\((\d{7})')
    for nom_fichier in os.listdir(repertoire):
        match = pattern.search(nom_fichier)
        if match:
            resultats.append(match.group(1))
    print(f"🔍 {len(resultats)} IDI extraits depuis {repertoire}")
    return resultats

# Traitement initial des fichiers FDB
for fichier in os.listdir(DOSSIER_FDB):
    if fichier.lower().endswith(".fdb"):
        chemin_fdb = os.path.join(DOSSIER_FDB, fichier)
        traiter_fichier_fdb(chemin_fdb)

# Enregistrement des erreurs par type
if erreurs_connexion or erreurs_tables or erreurs_requete:
    with open("fichiers_fdb_en_erreur.txt", "w", encoding="utf-8") as f:
        if erreurs_connexion:
            f.write("--- Erreurs de connexion ---\n")
            f.writelines(n + "\n" for n in erreurs_connexion)
            f.write("\n")
        if erreurs_tables:
            f.write("--- Tables TPAGES non trouvées ---\n")
            f.writelines(n + "\n" for n in erreurs_tables)
            f.write("\n")
        if erreurs_requete:
            f.write("--- Erreurs de requête SQL ---\n")
            f.writelines(n + "\n" for n in erreurs_requete)
            f.write("\n")
    print(f"❌ Rapport d'erreurs généré : fichiers_fdb_en_erreur.txt")

print("✅ Tous les fichiers traités. Voir extraction_novaxel_global.log pour le résumé.")
