import os
import json
import concurrent.futures

DOSSIER = r"/media/rico/SATURNE/DL/stock_RNE_formalites_20250523_0000"   # 👉 mets ici ton dossier
SIREN_RECHERCHE = "381658822"

resultats = []

def analyser_fichier(path):
    trouves = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for num_ligne, ligne in enumerate(f, start=1):
                try:
                    data = json.loads(ligne)
                except:
                    continue

                # Recherche exacte du SIREN dans les champs JSON
                if isinstance(data, dict):
                    for key, value in data.items():
                        if str(value) == SIREN_RECHERCHE:
                            trouves.append((num_ligne, ligne.strip()))
                            break

    except Exception as e:
        print(f"Erreur pour {path} : {e}")

    return path, trouves


def lister_fichiers_json(dossier):
    for root, dirs, files in os.walk(dossier):
        for file in files:
            if file.lower().endswith(".json"):
                yield os.path.join(root, file)


fichiers = list(lister_fichiers_json(DOSSIER))

# Multi-thread ultra rapide (lecture disque + parsing simple)
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    for path, matches in executor.map(analyser_fichier, fichiers):
        for ligne, contenu in matches:
            resultats.append({
                "fichier": path,
                "ligne": ligne,
                "json": contenu
            })


print("\n📌 RÉSULTATS :\n")
for r in resultats:
    print(f"Fichier : {r['fichier']}")
    print(f"Ligne   : {r['ligne']}")
    print(f"JSON    : {r['json']}\n")

print(f"🔎 Total occurrences exactes : {len(resultats)}")
