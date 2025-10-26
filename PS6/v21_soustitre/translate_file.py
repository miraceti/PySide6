from deep_translator import GoogleTranslator
import re

# --- paramètres à adapter ---
fichier_source = "/media/rico/SATURNE/rico/Documents/python/PySide6/PS6/v21_soustitre/texte_anglais.srt"
fichier_sortie = "texte_francais.srt"

# --- initialisation du traducteur ---
traducteur = GoogleTranslator(source='en', target='fr')

# --- lecture et traitement ligne par ligne ---
with open(fichier_source, "r", encoding="utf-8") as f_in, \
     open(fichier_sortie, "w", encoding="utf-8") as f_out:

    for ligne in f_in:
        # Vérifie si la ligne commence par une lettre (majuscule ou minuscule)
        if re.match(r"^[A-Za-z]", ligne.strip()):
            texte_traduit = traducteur.translate(ligne.strip())
            f_out.write(texte_traduit + "\n")
        else:
            # On garde la ligne telle quelle
            f_out.write(ligne)