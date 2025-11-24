import os

DOSSIER = r"/media/rico/SATURNE/DL/stock_RNE_formalites_20250523_0000"   # 👉 mets ici ton dossier
TEXTE = "381658822"                # 👉 texte / SIREN à rechercher

resultats = []

for root, dirs, files in os.walk(DOSSIER):
    for file in files:
        if file.lower().endswith(".json"):
            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    for num_ligne, ligne in enumerate(f, start=1):
                        if TEXTE in ligne:
                            resultats.append({
                                "fichier": path,
                                "ligne": num_ligne,
                                "contenu_json": ligne.strip()
                            })

            except Exception as e:
                print(f"Erreur lecture {path}: {e}")

# Affichage
print("\n📌 Résultats :\n")
for r in resultats:
    print(f"Fichier : {r['fichier']}")
    print(f"Ligne   : {r['ligne']}")
    print(f"JSON    : {r['contenu_json']}\n")

print(f"🔎 Total occurrences trouvées : {len(resultats)}")
