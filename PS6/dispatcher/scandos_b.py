import os
import pandas as pd
from xml.etree import ElementTree as ET
from fpdf import FPDF

# =====================
# Lecture XML
# =====================
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
# Génération PDF
# =====================
def generer_pdf(dossier_pli, pdf_num, liste_images, dossier_lots, dossier_resultat):
    pdf = FPDF()
    path_pli = os.path.join(dossier_lots, dossier_pli)
    for img_name in liste_images:
        img_path = os.path.join(path_pli, img_name)
        if os.path.exists(img_path):
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=180)
    os.makedirs(dossier_resultat, exist_ok=True)
    pdf_path = os.path.join(dossier_resultat, f"{dossier_pli}_PLI{pdf_num}.pdf")
    pdf.output(pdf_path)
    print(f"PDF généré: {pdf_path}")

# =====================
# Analyse dossier Lots
# =====================
def analyser_lots(dossier_lots, dossier_resultat="PDF_Resultats"):
    data = []

    for dossier_pli in sorted(os.listdir(dossier_lots)):
        path_pli = os.path.join(dossier_lots, dossier_pli)
        if not os.path.isdir(path_pli):
            continue

        fichiers = sorted(os.listdir(path_pli))
        pdf_index = 0
        current_pdf = []

        for fichier in fichiers:
            nom, ext = os.path.splitext(fichier)
            if ext.lower() != ".xml":
                continue

            index_num = int(nom.split("_")[1])
            xml_data = lire_xml(os.path.join(path_pli, fichier))
            est_donnees = any(v.strip() for v in xml_data.values())

            if index_num == 1:
                # Infos dossier, pas de PDF
                pass
            elif est_donnees:
                # Sauvegarder PDF précédent
                if current_pdf:
                    pdf_index += 1
                    generer_pdf(dossier_pli, pdf_index, current_pdf, dossier_lots, dossier_resultat)
                    current_pdf = []
                # Nouveau PDF, ajout de l'image correspondante
                current_pdf.append(f"{nom}.jpg")
            else:
                # Page supplémentaire du PDF en cours
                current_pdf.append(f"{nom}.jpg")

            # Ajout des données au DataFrame
            data.append({
                "dossier": dossier_pli,
                "fichier": fichier,
                "type": "xml",
                "index": index_num,
                **xml_data,
                "pdf_num": pdf_index + 1 if est_donnees else pdf_index
            })

        # Dernier PDF
        if current_pdf:
            pdf_index += 1
            generer_pdf(dossier_pli, pdf_index, current_pdf, dossier_lots, dossier_resultat)

    df = pd.DataFrame(data)
    df = df.sort_values(by=["dossier", "index"]).reset_index(drop=True)
    return df

# =====================
# Main
# =====================
if __name__ == "__main__":
    dossier_source = "Lots"  # <-- ton dossier réel
    dossier_pdfs = "PDF_Resultats"
    df_resultat = analyser_lots(dossier_source, dossier_pdfs)
    print("\n=== DataFrame final ===")
    print(df_resultat)
    # Sauvegarde éventuelle en CSV
    df_resultat.to_csv("resultat_lots.csv", index=False, encoding="utf-8-sig")
