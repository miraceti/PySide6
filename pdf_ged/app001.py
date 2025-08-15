import PySide6
import os
import shutil
import pandas as pd
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# =====================
# 1️⃣ Création structure de test
# =====================
def creer_structure_test():
    # Nettoyage ancien test
    if os.path.exists("pdf_ged/Lots"):
        shutil.rmtree("pdf_ged/Lots")
    if os.path.exists("pdf_gedPDF_Resultats"):
        shutil.rmtree("pdf_ged/PDF_Resultats")

    os.makedirs("pdf_ged/Lots", exist_ok=True)
    os.makedirs("pdf_ged/PDF_Resultats", exist_ok=True)

    plis = ["201546", "201547"]
    for pli in plis:
        dossier = os.path.join("pdf_ged/Lots", pli)
        os.makedirs(dossier, exist_ok=True)

        # Images + XML
        # Image_001 : infos dossier
        creer_image(os.path.join(dossier, "Image_001.jpg"), "Image_001")
        creer_xml_infos_dossier(os.path.join(dossier, "Image_001.xml"), numaxa=f"{pli}_INFO")

        # Image_002 : début pli 1
        creer_image(os.path.join(dossier, "Image_002.jpg"), "Image_002")
        creer_xml_donnees(os.path.join(dossier, "Image_002.xml"), numaxa=f"{pli}_PLI1")

        # Pages du pli 1 (003 à 005) -> XML vide
        for i in range(3, 6):
            creer_image(os.path.join(dossier, f"Image_{i:03}.jpg"), f"Image_{i:03}")
            creer_xml_vide(os.path.join(dossier, f"Image_{i:03}.xml"))

        # Image_006 : début pli 2
        creer_image(os.path.join(dossier, "Image_006.jpg"), "Image_006")
        creer_xml_donnees(os.path.join(dossier, "Image_006.xml"), numaxa=f"{pli}_PLI2")

        # Pages pli 2 (007 à 008)
        for i in range(7, 9):
            creer_image(os.path.join(dossier, f"Image_{i:03}.jpg"), f"Image_{i:03}")
            creer_xml_vide(os.path.join(dossier, f"Image_{i:03}.xml"))

def creer_image(path, text):
    img = Image.new("RGB", (400, 300), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((50, 140), text, fill="black", font=font)
    img.save(path)

def creer_xml_infos_dossier(path, numaxa):
    contenu = f"""<?xml version="1.0" encoding="utf-8"?>
<XMLDoc>
  <rotation>0</rotation>
  <etat>0</etat>
  <type>1</type>
  <crop>
    <left>0</left><top>0</top><width>0</width><height>0</height>
  </crop>
  <meta>
    <numaxa>{numaxa}</numaxa>
    <service>INFO_DOSSIER</service>
    <pole></pole><complexe></complexe><gestionnaire></gestionnaire>
  </meta>
</XMLDoc>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)

def creer_xml_donnees(path, numaxa):
    contenu = f"""<?xml version="1.0" encoding="utf-8"?>
<XMLDoc>
  <rotation>0</rotation>
  <etat>1</etat>
  <type>1</type>
  <crop>
    <left>10</left><top>20</top><width>100</width><height>200</height>
  </crop>
  <meta>
    <numaxa>{numaxa}</numaxa>
    <service>PLI_DATA</service>
    <pole>PoleX</pole><complexe>CompY</complexe><gestionnaire>GestZ</gestionnaire>
  </meta>
</XMLDoc>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)

def creer_xml_vide(path):
    contenu = """<?xml version="1.0" encoding="utf-8"?>
<XMLDoc>
  <rotation></rotation>
  <etat></etat>
  <type></type>
  <crop>
    <left></left><top></top><width></width><height></height>
  </crop>
  <meta>
    <numaxa></numaxa>
    <service></service>
    <pole></pole><complexe></complexe><gestionnaire></gestionnaire>
  </meta>
</XMLDoc>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenu)

# =====================
# 2️⃣ Analyse + regroupement
# =====================
def analyser_lots():
    data = []
    for dossier_pli in sorted(os.listdir("pdf_ged/Lots")):
        path_pli = os.path.join("pdf_ged/Lots", dossier_pli)
        if not os.path.isdir(path_pli):
            continue

        fichiers = sorted(os.listdir(path_pli))
        pdf_index = 0
        pdf_pages = []
        current_pdf = []

        for fichier in fichiers:
            chemin_fic = os.path.join(path_pli, fichier)
            nom, ext = os.path.splitext(fichier)
            index_num = int(nom.split("_")[1])

            if ext.lower() == ".xml":
                xml_data = lire_xml(chemin_fic)
                est_donnees = any(v.strip() for v in xml_data.values())
                if index_num == 1:
                    # infos dossier
                    pass
                elif est_donnees:
                    # Sauvegarder l'ancien PDF si pages
                    if current_pdf:
                        pdf_index += 1
                        generer_pdf(dossier_pli, pdf_index, current_pdf)
                        current_pdf = []
                    # Démarrer nouveau PDF
                    current_pdf.append(nom.replace(".xml", ".jpg"))
                else:
                    current_pdf.append(nom.replace(".xml", ".jpg"))

                data.append({
                    "dossier": dossier_pli,
                    "fichier": fichier,
                    "type": "xml",
                    "index": index_num,
                    **xml_data,
                    "pdf_num": pdf_index + 1 if est_donnees else pdf_index
                })

        # Dernier PDF du dossier
        if current_pdf:
            pdf_index += 1
            generer_pdf(dossier_pli, pdf_index, current_pdf)

    df = pd.DataFrame(data)
    df = df.sort_values(by=["dossier", "index"]).reset_index(drop=True)
    return df

def lire_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return {
        "rotation": root.findtext("rotation", ""),
        "etat": root.findtext("etat", ""),
        "type": root.findtext("type", ""),
        "left": root.findtext("crop/left", ""),
        "top": root.findtext("crop/top", ""),
        "width": root.findtext("crop/width", ""),
        "height": root.findtext("crop/height", ""),
        "numaxa": root.findtext("meta/numaxa", ""),
        "service": root.findtext("meta/service", ""),
        "pole": root.findtext("meta/pole", ""),
        "complexe": root.findtext("meta/complexe", ""),
        "gestionnaire": root.findtext("meta/gestionnaire", "")
    }

# =====================
# 3️⃣ Génération PDF
# =====================
def generer_pdf(dossier_pli, pdf_num, liste_images):
    pdf = FPDF()
    path_pli = os.path.join("pdf_ged/Lots", dossier_pli)
    for img_name in liste_images:
        img_path = os.path.join(path_pli, img_name)
        if os.path.exists(img_path):
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=180)
    pdf_path = os.path.join("pdf_ged/PDF_Resultats", f"{dossier_pli}_PLI{pdf_num}.pdf")
    pdf.output(pdf_path)
    print(f"PDF généré: {pdf_path}")

# =====================
# 4️⃣ Main
# =====================
if __name__ == "__main__":
    creer_structure_test()
    df_resultat = analyser_lots()
    print("\n=== DataFrame final ===")
    print(df_resultat)
