import os
import json

DOSSIER = r"/media/rico/SATURNE/DL/stock_RNE_formalites_20250523_0000"   # 👉 mets ici ton dossier
TEXTE = "381658822"                # 👉 le texte à rechercher

matches = []

for root, dirs, files in os.walk(DOSSIER):
    for file in files:
        if file.lower().endswith(".json"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    contenu = f.read()

                if TEXTE in contenu:
                    matches.append(path)

            except Exception as e:
                print(f"Erreur lecture {path}: {e}")

print("\n📌 Fichiers contenant le texte recherché:\n")
for m in matches:
    print(m)

print(f"\n🔎 Total : {len(matches)} fichiers trouvés.")