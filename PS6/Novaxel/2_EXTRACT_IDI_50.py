import os
import re
import pandas as pd

# Chemin correct vers ton répertoire
repertoire_principal = r"E:/FICHIERS/Pascal/FDB_50/TPAGES_50"

# Regex assouplie pour extraire l'ID
pattern = re.compile(r'^900_Doc\(Id_L_T\)=\(\((\d+)[^)]*')

# Listes de stockage
liste_ids = []
liste_noms_fichiers = []

# Parcours des fichiers
for dossier_racine, sous_dossiers, fichiers in os.walk(repertoire_principal):
    for nom_fichier in fichiers:
        match = pattern.match(nom_fichier)
        if match:
            liste_ids.append(match.group(1))
            liste_noms_fichiers.append(nom_fichier)

# Création du fichier Excel si des résultats ont été trouvés
if liste_ids:
    df = pd.DataFrame({
        "IDI": liste_ids,
        "NomFichier": liste_noms_fichiers
    })
    df.to_excel("E:/FICHIERS/Pascal/FDB_50/resultats_50.xlsx", index=False)
    print("✅ Extraction terminée. Fichier Excel généré : resultats.xlsx")
else:
    print("⚠️ Aucun fichier correspondant trouvé dans :", repertoire_principal)
