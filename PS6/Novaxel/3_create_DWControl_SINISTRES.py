import os
import re
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pyodbc

# Connexion à la base de données et récupération du DataFrame
conn = pyodbc.connect('DSN=WINPASS_SATEC_RW_64;')
query = """

SELECT 
    IDI=CONVERT(VARCHAR(7), s1.IDI),
    NomFichier=idi.NomFichier,
    TYPE_ENREGISTREMENT='DOC',
    COMPLEXE=isnull(s1.[N° de sinistre / Suivi interne],'')+' - ' + isnull(sin_nomtiers,'')+' - '+ isnull(adr_nom,'')+' ' + isnull(cli_dossier_id,'')+' '+ isnull(cli_siret,'') +' - ' + isnull(sin_sinistresiege,'@SINSiege') +' - '+convert(varchar,sin_dtesurvenance,103) +' - NC - WP01',
    POLE='95',
    TYPE_DOCUMENT=case s1.[Type document]
					when  'SD01' then 'SD01 - Déclaration de sinistre'
					when  'SD02' then 'SD02 - Mise en cause adverse'
					when  'SE02' then 'SE02 - Mission/Prise en charge/Prise en charge entreprise service'
					when  'SE03' then 'SE03 - Convocation'
					when  'SE06' then 'SE06 - Rapport d''expertise'
					when  'SJ02' then 'SJ02 - Dépôt de plainte'
					when  'SJ03' then 'SJ03 - Justificatifs comptables - factures'
					when  'SJ06' then 'SJ06 - Réclamations adverses'
					when  'SO01' then 'SO01 - AR client'
					when  'SO02' then 'SO02 - AR compagnie'
					when  'SO04' then 'SO04 - Echanges - texte libre divers'
					else ''
					end,
    TYPE_COURRIER=case s1.[Type document]
					when  'SD01' then 'SD01 - Déclaration de sinistre'
					when  'SD02' then 'SD02 - Mise en cause adverse'
					when  'SE02' then 'SE02 - Mission/Prise en charge/Prise en charge entreprise service'
					when  'SE03' then 'SE03 - Convocation'
					when  'SE06' then 'SE06 - Rapport d''expertise'
					when  'SJ02' then 'SJ02 - Dépôt de plainte'
					when  'SJ03' then 'SJ03 - Justificatifs comptables - factures'
					when  'SJ06' then 'SJ06 - Réclamations adverses'
					when  'SO01' then 'SO01 - AR client'
					when  'SO02' then 'SO02 - AR compagnie'
					when  'SO04' then 'SO04 - Echanges - texte libre divers'
					else ''
					end,
    ARCHIVE_PAR =s1.[Archivé par],
    TITRE_OBJET=s1.[NomFichier / Titre objet],
    s1.[Date Document] AS DATE_DOCUMENT,
    s1.[Date d'acquisition] AS DATE_ACQUISITION,
    EXTRANET='Non',
	SOCIETE='SATEC',
	NOM_CLIENT=isnull(adr_nom,''),
	NO_CONTRAT = isnull(s1.[Numérodecontrat],''),
	ORDRE_CONTRAT=isnull(s1.[Ordre contrat],''),
	SOURCE_WINPASS='WP01',
	SINISTRE_SUIVI = s1.[N° de sinistre / Suivi interne],
	CELLULE='Satec Saint Pierre',
	NO_BOITE=isnull(s1.[N° de boîte],''),
	CLIENT_CONTRAT_ID=Cli_Client_id,
	RISQUE=isnull(s1.[Risque ass# / Locataire],''),
	COMMENTAIRE=isnull(s1.commentaire,''),
    NO_PLI='IDI'+isnull(s1.[IDI],''),

    
	SINISTRE_COMPAGNIE=isnull(Sin_SinistreSiege,''),
	REF_CLIENT = ISNULL(sin_refcourtier,''),
	DATE_SINISTRE = Sin_DteSurvenance,
	TIERS_RISQUE_ASS = ISNULL(sin_nomtiers,''),
	NOM_COMPAGNIE = ISNULL(pol_cie_id,'')+' - ' + isnull(Cie_SuperCie_id,''),
	PRODUIT_LONG = ISNULL(pol_famille_id,'')+'-'+ISNULL(pol_branche_id,'')+'-'+ISNULL(pol_produit_id,'')+'-'+ISNULL(prd_intitule,''),

    LIEU_SINISTRE = isnull(sin_lieusurvenance,''),
	OBSERVATION = ISNULL(sin_observations,''),
    REF_EXPERT = isnull(sin_refexpert,''),
	SINISTRE = ISNULL(natu_intitule,'')

from TMP_ELC_JCF_NOVAXEL_SIN s1
inner join TMP_ELC_JCF_NOVAXEL_SIN_IDI idi on convert(varchar(7),idi.IDI) = convert(varchar(7),s1.IDI)
inner join si_sinistres on s1.[ID Sinistre] = sin_sinistre_id
inner join pc_clients on s1.[client contrat id] = cli_client_id
inner join pg_adresses on adr_adresse_id =cli_adresse_id
inner join PP_Contrats on Sin_Contrat_id=pol_contrat_id
inner join PG_Compagnies on Cie_Compagnie_id=pol_cie_id
inner join PA_Produits on Pol_Produit_id = Prd_Produit_id
left join PG_Natures on Natu_Nature_id=sin_nature_id  and Sin_Convention_id=Natu_Convention_id

--s
--where (idi.NomFichier like '%_2_880.%' or idi.NomFichier like '%_2_881.%' or idi.NomFichier like '%_2_882.%' or idi.NomFichier like '%_2_883.%')

"""
df = pd.read_sql(query, conn)

# Répertoires
racine_dossier = r"E:/FICHIERS/Pascal/FDB_50/TPAGES_50"
dossier_cible = r"E:/FICHIERS/Pascal/FDB_50/TPAGES_50/EXPORT_XML_SIN"
dossier_cibleGED = r"//172.16.10.10/Import/Winpass"
os.makedirs(dossier_cible, exist_ok=True)

# Ensemble des IDI pour une recherche rapide
df_idi_set = set(df['IDI'].astype(str))

# Fonction pour extraire l'IDI du nom de fichier
def extraire_idi(nom_fichier):
    match = re.search(r'900_Doc\(Id_L_T\)=\(\((\d{7})', nom_fichier)
    return match.group(1) if match else None

# Fonction pour générer le fichier .dwcontrol
def generer_dwcontrol(nom_base, fichiers_paths, infos, output_folder, ged_folder):
    ET.register_namespace('', "http://dev.docuware.com/Jobs/Control")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

    root = ET.Element("ControlStatements", {
        "xmlns": "http://dev.docuware.com/Jobs/Control",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })

    document = ET.SubElement(root, "Document")
    for path in fichiers_paths:
        ged_path = os.path.join(ged_folder, os.path.basename(path)).replace("\\", "/")
        ET.SubElement(document, "InsertFile", {"path": ged_path})

    page = ET.SubElement(root, "Page")
    for dbName, type_attr, value in infos:
        ET.SubElement(page, "Field", {
            "dbName": dbName,
            "type": type_attr,
            "value": str(value) if pd.notna(value) else ""
        })

    nom_dwcontrol = f"{nom_base}.dwcontrol"
    chemin_xml = os.path.join(output_folder, nom_dwcontrol)

    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    with open(chemin_xml, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    return nom_dwcontrol

# Parcours des fichiers et traitement
for root, _, files in os.walk(racine_dossier):
    for fichier in files:
        idi = extraire_idi(fichier)
        if idi and idi in df_idi_set:
            chemin_fichier = os.path.join(root, fichier)
            dest = os.path.join(dossier_cible, fichier)
            shutil.copy2(chemin_fichier, dest)

            row = df[df['IDI'] == idi].iloc[0]
            infos = [
                ("TYPE_ENREGISTREMENT", "string", row["TYPE_ENREGISTREMENT"]),
                ("COMPLEXE", "string", row["COMPLEXE"]),
                ("POLE", "string", row["POLE"]),
                ("TYPE_DOCUMENT", "string", row["TYPE_DOCUMENT"]),
                ("TYPE_COURRIER", "string", row["TYPE_COURRIER"]),
                ("ARCHIVE_PAR", "string", row["ARCHIVE_PAR"]),
                ("TITRE_OBJET", "string", row["TITRE_OBJET"]),
                ("DATE_DOCUMENT", "date", row["DATE_DOCUMENT"]),
                ("DATE_ACQUISITION", "date", row["DATE_ACQUISITION"]),
                ("EXTRANET", "string", row["EXTRANET"]),
                ("NO_PLI", "string", row["NO_PLI"]),
                ("SOCIETE", "string", row["SOCIETE"]),
                ("NO_CONTRAT", "string", row["NO_CONTRAT"]),
                ("ORDRE_CONTRAT", "string", row["ORDRE_CONTRAT"]),
                ("SOURCE_WINPASS", "string", row["SOURCE_WINPASS"]),
                ("SINISTRE_SUIVI", "string", row["SINISTRE_SUIVI"]),
                ("CELLULE", "string", row["CELLULE"]),
                ("NO_BOITE", "string", row["NO_BOITE"]),
                ("CLIENT_CONTRAT_ID", "string", row["CLIENT_CONTRAT_ID"]),
                ("RISQUE", "string", row["RISQUE"]),
                ("COMMENTAIRE", "string", row["COMMENTAIRE"]),
                ("SINISTRE_COMPAGNIE", "string", row["SINISTRE_COMPAGNIE"]),
                ("REF_CLIENT", "string", row["REF_CLIENT"]),
                ("DATE_SINISTRE", "date", row["DATE_SINISTRE"]),
                ("TIERS_RISQUE_ASS", "string", row["TIERS_RISQUE_ASS"]),
                ("NOM_COMPAGNIE", "string", row["NOM_COMPAGNIE"]),
                ("PRODUIT_LONG", "string", row["PRODUIT_LONG"]),
                ("LIEU_SINISTRE", "string", row["LIEU_SINISTRE"]),
                ("OBSERVATION", "string", row["OBSERVATION"]),
                ("REF_EXPERT", "string", row["REF_EXPERT"]),
                ("SINISTRE", "string", row["SINISTRE"])
            ]
            nom_base = os.path.splitext(fichier)[0]
            generer_dwcontrol(nom_base, [dest], infos, dossier_cible, dossier_cibleGED)
