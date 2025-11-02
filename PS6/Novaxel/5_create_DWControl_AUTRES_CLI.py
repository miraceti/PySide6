import pandas as pd
import pyodbc
import xml.etree.ElementTree as ET
import os
import shutil
import re
import xlsxwriter


def normaliser_nom(nom):
    nom_sans_ext = os.path.splitext(nom)[0]
    nom_normalise = re.sub(r'[^\w\-]', '_', nom_sans_ext)
    return nom_normalise.lower()

def formatter_date(valeur):
    if pd.isna(valeur):
        return ""
    return valeur.strftime("%Y-%m-%d")

def indenter_xml(elem, niveau=0):
    indent = "\n" + niveau * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        for e in elem:
            indenter_xml(e, niveau + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
    else:
        if niveau and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent

conn = pyodbc.connect('DSN=WINPASS_SATEC_RW_64;') 
query = """


SELECT 
    IDI=c1.IDI,
    NomFichier=idi.NomFichier,
    TYPE_ENREGISTREMENT='DOC',
    COMPLEXE='*',
    POLE='40',
    TYPE_DOCUMENT=case c1.[Type document]
					when	'PC02' then 'PC02 - Pièces d''identité dont : Extrait Kbis, Permis de conduire, Licence, Brevets - Client'
					when	'PC05' then 'PC05 - Mandat SEPA dont : RIB, Relevé de compte/échéance - Client'
					when	'PE01' then	'PE01 - Attestation'
					when    'PE03' then 'PE03 - Demande de résiliation'
					when	'PE04' then 'PE04 - Correspondances y/c Pièces Avec / Sans perception, Doc. technique, Relance impayé'
					when	'PM01' then 'PM01 - Quittance/Avis échéance dont Quittance de renégociation, Quittance ristourne, Note honoraires'
					when	'PN02' then 'PN02 - Mise en Demeure dont : Rappel, Préavis de mise en demeure, Résiliation pour non paiement'
					when	'PO01' then 'PO01 - Conditions Particulières dont : Opposition'
					when	'PO02' then 'PO02 - Avenant + Exemplaire Signé dont : Lettre avenant, Dont acte, Projet d’avenant'
					when	'PO06' then 'PO06 - Conditions générales dont : Conventions spéciales, Annexes'
					when	'PO08' then	'PO08 - Statistiques sinistres et/ou attestations de sinistres/surveillance du portefeuille'
					when	'PP05' then 'PP05 - Doc technique y/c Justif prévention, Bail, Stat. Sin, Certificat, Factures alarmes, Photos'
					when	'PP12' then 'PP12 - Saisine'
					when	'PP13' then 'PP13 - Etude'
					when	'PP15' then 'PP15 - Reporting / Compte rendu client'
					when	'PR01' then 'PR01 - Demande de la Cie dont : Demande au client, Déclaration du client, Envoi des éléments'
					when	'PR05' then 'PR05 - Parc et mouvements y/c Adjonction ou Retrait, Bilans, Demandes des CAC, Comptes de résulats'
					when	'PR08' then 'PR08 - Quittance de régularisation y/c  Avenant ou Décompte de régularisation, Quittance majorée'
					when	'SD01' then 'SD01 - Déclaration de sinistre'
					when	'SD02' then 'SD02 - Mise en cause adverse'
					when	'SE02' then 'SE02 - Mission/Prise en charge/Prise en charge entreprise service'
					when	'SE03' then 'SE03 - Convocation'
					when	'SE06' then	'SE06 - Rapport d''expertise'
					when	'SJ02' then	'SJ02 - Dépôt de plainte'
					when	'SJ03' then	'SJ03 - Justificatifs comptables - factures'
					when	'SJ06' then	'SJ06 - Réclamations adverses'
					when	'SO01' then	'SO01 - AR client'
					when	'SO02' then	'SO02 - AR compagnie'
					when	'SO04' then	'SO04 - Echanges - texte libre divers'
					when	'SR02' then	'SR02 - Règlement'
					when	'SR03' then 'SR03 - Chèque'
					else ''
					end,
    TYPE_COURRIER=case c1.[Type document]
					when	'PC02' then 'PC02 - Pièces d''identité dont : Extrait Kbis, Permis de conduire, Licence, Brevets - Client'
					when	'PC05' then 'PC05 - Mandat SEPA dont : RIB, Relevé de compte/échéance - Client'
					when	'PE01' then	'PE01 - Attestation'
					when    'PE03' then 'PE03 - Demande de résiliation'
					when	'PE04' then 'PE04 - Correspondances y/c Pièces Avec / Sans perception, Doc. technique, Relance impayé'
					when	'PM01' then 'PM01 - Quittance/Avis échéance dont Quittance de renégociation, Quittance ristourne, Note honoraires'
					when	'PN02' then 'PN02 - Mise en Demeure dont : Rappel, Préavis de mise en demeure, Résiliation pour non paiement'
					when	'PO01' then 'PO01 - Conditions Particulières dont : Opposition'
					when	'PO02' then 'PO02 - Avenant + Exemplaire Signé dont : Lettre avenant, Dont acte, Projet d’avenant'
					when	'PO06' then 'PO06 - Conditions générales dont : Conventions spéciales, Annexes'
					when	'PO08' then	'PO08 - Statistiques sinistres et/ou attestations de sinistres/surveillance du portefeuille'
					when	'PP05' then 'PP05 - Doc technique y/c Justif prévention, Bail, Stat. Sin, Certificat, Factures alarmes, Photos'
					when	'PP12' then 'PP12 - Saisine'
					when	'PP13' then 'PP13 - Etude'
					when	'PP15' then 'PP15 - Reporting / Compte rendu client'
					when	'PR01' then 'PR01 - Demande de la Cie dont : Demande au client, Déclaration du client, Envoi des éléments'
					when	'PR05' then 'PR05 - Parc et mouvements y/c Adjonction ou Retrait, Bilans, Demandes des CAC, Comptes de résulats'
					when	'PR08' then 'PR08 - Quittance de régularisation y/c  Avenant ou Décompte de régularisation, Quittance majorée'
					when	'SD01' then 'SD01 - Déclaration de sinistre'
					when	'SD02' then 'SD02 - Mise en cause adverse'
					when	'SE02' then 'SE02 - Mission/Prise en charge/Prise en charge entreprise service'
					when	'SE03' then 'SE03 - Convocation'
					when	'SE06' then	'SE06 - Rapport d''expertise'
					when	'SJ02' then	'SJ02 - Dépôt de plainte'
					when	'SJ03' then	'SJ03 - Justificatifs comptables - factures'
					when	'SJ06' then	'SJ06 - Réclamations adverses'
					when	'SO01' then	'SO01 - AR client'
					when	'SO02' then	'SO02 - AR compagnie'
					when	'SO04' then	'SO04 - Echanges - texte libre divers'
					when	'SR02' then	'SR02 - Règlement'
					when	'SR03' then 'SR03 - Chèque'
					else ''
					end,
    ARCHIVE_PAR =c1.[Archivé par],
    TITRE_OBJET=c1.[Titre / Objet],
    isnull(c1.[Date Document],'01/01/1900') AS DATE_DOCUMENT,
    isnull(c1.[Date d'acquisition],'01/01/1900') AS DATE_ACQUISITION,
    EXTRANET='Non',
	SOCIETE='SATEC',
	NOM_CLIENT=isnull(adr_nom,''),
	NO_CONTRAT = isnull(c1.[N° Contrat],''),
	ORDRE_CONTRAT=isnull(c1.[Ordre contrat],''),
	SOURCE_WINPASS='WP01',
	SINISTRE_SUIVI = '',
	CELLULE='Satec Saint Pierre',
	NO_BOITE=isnull(c1.[N° de boite],''),
	CLIENT_CONTRAT_ID=Cli_Client_id,
	RISQUE=isnull(c1.[Risque ass# / Locataire],''),
	COMMENTAIRE=isnull(c1.commentaire,''),
	NO_PLI='IDI'+isnull(c1.[IDI],'')
--select *
,c1.[numérodesinistre],c1.[N° Contrat],PRENOM_CLIENT=isnull(adr_prenom,''),DOSSIER=isnull(cli_dossier_id,''),SIRET=isnull(cli_siret,'')

from TMP_ELC_JCF_NOVAXEL_Autres c1
inner join TMP_ELC_JCF_NOVAXEL_SIN_IDI idi on convert(varchar(7),idi.IDI) = convert(varchar(7),c1.IDI)
left  join pp_contrats on c1.[client contrat id] = pol_client_id and c1.[Ordre contrat]=pol_ordre_contrat
inner join pc_clients on c1.[client contrat id] = cli_client_id
inner join pg_adresses on adr_adresse_id =cli_adresse_id
left join pp_contrats_4roues on polc1_contrat_id = pol_contrat_id
left join pp_contrats_divers on polc2_contrat_id  =pol_contrat_id

--where (idi.NomFichier like '%_2_880.%' or idi.NomFichier like '%_2_881.%' or idi.NomFichier like '%_2_882.%' or idi.NomFichier like '%_2_883.%')
where isnull(pol_contrat_id ,'')=''
"""
df = pd.read_sql(query, conn)

racine_dossier = r"D:/FICHIERS/Pascal/FDB_50/TPAGES_50"
dossier_cible = r"D:/FICHIERS/Pascal/FDB_50/TPAGES_50/EXPORT_XML_CLI"
dossier_cibleGED = r"//172.16.10.10/Import/Winpass"

os.makedirs(dossier_cible, exist_ok=True)


def trouver_fichier(nom_fichier_recherche):
    nom_recherche_normalise = normaliser_nom(nom_fichier_recherche)
    meilleur_match = None

    for root, dirs, files in os.walk(racine_dossier):
        # Ignore les dossiers de destination
        dirs[:] = [d for d in dirs if "EXPORT_XML_CLI" not in d and "EXPORT_XML_CTR" not in d]
        for f in files:
            if f.lower().endswith(".dwcontrol"):
                continue  # ⚠️ On ignore les .dwcontrol qui polluent la recherche

            nom_fichier_normalise = normaliser_nom(f)

            # 1. Correspondance exacte
            if nom_fichier_normalise == nom_recherche_normalise:
                return os.path.join(root, f)

            # 2. Correspondance partielle avec une certaine prudence
            if nom_fichier_normalise.startswith(nom_recherche_normalise[:20]):
                if meilleur_match is None:
                    meilleur_match = os.path.join(root, f)

    print(f"[MATCH DEBUG] Recherche: {nom_fichier_recherche} → Match exact: {meilleur_match is not None}")
    return meilleur_match


def generer_dwcontrol(nom_base, fichiers_paths, infos, output_folder, ged_folder):
    import xml.dom.minidom as minidom

    ET.register_namespace('', "http://dev.docuware.com/Jobs/Control")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")

    root = ET.Element("ControlStatements", {
        "xmlns": "http://dev.docuware.com/Jobs/Control",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"
    })

    document = ET.SubElement(root, "Document")
    fichiers_inserts = set()
    for path in fichiers_paths:
        if path and not path.lower().endswith(".dwcontrol") and path not in fichiers_inserts:
            fichiers_inserts.add(path)
            ged_path = os.path.join(ged_folder, os.path.basename(path)).replace("\\", "/")
            ET.SubElement(document, "InsertFile", {
                "path": ged_path
            })

    page = ET.SubElement(root, "Page")
    for dbName, type_attr, value in infos:
        if pd.isna(value):
            value = ""
        elif type_attr == "date":
            try:
                value = pd.to_datetime(value).strftime("%d/%m/%Y")
            except Exception:
                value = ""
        else:
            value = str(value)
        ET.SubElement(page, "Field", {
            "dbName": dbName,
            "type": type_attr,
            "value": value
        })

    nom_dwcontrol = f"{nom_base}.dwcontrol"
    chemin_xml = os.path.join(output_folder, nom_dwcontrol)

    if os.path.exists(chemin_xml):
        print(f"[XML-EXISTS] {chemin_xml} existe déjà. Ignoré.")
        return nom_dwcontrol

    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    pretty_xml_clean = "\n".join([line for line in pretty_xml.split('\n') if line.strip() != ""])

    with open(chemin_xml, "w", encoding="utf-8") as f:
        f.write(pretty_xml_clean)

    return nom_dwcontrol



df_logs = set()

for _, row in df.iterrows():
    fichier_nom = row["NomFichier"]
    nom_base = os.path.splitext(fichier_nom)[0]

    chemins = []
    extensions = [".html", ".pdf", ".emf", ".zip", ".rtf", ".pptx"]

    for ext in extensions:
        nom_recherche = nom_base + ext
        chemin = trouver_fichier(nom_recherche)
        print(f"[DEBUG] Recherche : {nom_recherche} → {chemin}")
        df_logs.add(f"[DEBUG] Recherche : {nom_recherche} → {chemin}")
        chemins.append(chemin)


    found_paths = [p for p in chemins if p]
    if found_paths:
        dest_paths = []
        for chemin in found_paths:
            nom_fichier = os.path.basename(chemin)
            dest = os.path.join(dossier_cible, nom_fichier)
            chemin_CTR = os.path.join(r"D:/FICHIERS/Pascal/FDB/TPAGES_400_800/EXPORT_XML_CTR", nom_fichier)

            if os.path.exists(chemin_CTR):
                df_logs.add(f"[SKIP-CTR] {nom_fichier} déjà présent dans EXPORT_XML_CTR")
                continue

            try:
                if not os.path.exists(dest):
                    shutil.copy2(chemin, dest)
                    df_logs.add(f"[COPY] {dest}")
                else:
                    df_logs.add(f"[SKIP] {dest} déjà présent")
            except PermissionError:
                df_logs.add(f"[ERROR] Accès refusé à {dest}")

            dest_paths.append(dest)

        if dest_paths:
            infos = [
                ("TYPE_ENREGISTREMENT", "string", row["TYPE_ENREGISTREMENT"]),
                ("NOM_CLIENT", "string", row["NOM_CLIENT"]+' '+row["PRENOM_CLIENT"]+' '+row["DOSSIER"]+' '+row["SIRET"]),
                ("POLE", "string", row["POLE"]),
                ("TYPE_DOCUMENT", "string", row["TYPE_DOCUMENT"]),
                ("TYPE_COURRIER", "string", row["TYPE_COURRIER"]),
                ("ARCHIVE_PAR", "string", row["ARCHIVE_PAR"]),
                ("TITRE_OBJET", "string", row["TITRE_OBJET"]),
                ("DATE_DOCUMENT", "date", formatter_date(row["DATE_DOCUMENT"])),
                ("DATE_ACQUISITION", "date", formatter_date(row["DATE_ACQUISITION"])),
                ("EXTRANET", "string", row["EXTRANET"]),
                ("CELLULE", "string", row["CELLULE"]),
                ("NO_PLI", "string", row["NO_PLI"]),
                ("SOCIETE", "string", row["SOCIETE"]),
                ("SOURCE_WINPASS", "string", row["SOURCE_WINPASS"]),
                ("NO_BOITE", "string", row["NO_BOITE"]),
                ("COMMENTAIRE", "string", row["COMMENTAIRE"]),
                ("CLIENT_CONTRAT_ID", "string", row["CLIENT_CONTRAT_ID"]),
                ("COMPLEXE", "string", row["COMPLEXE"])
            ]

            nom_xml = generer_dwcontrol(nom_base, dest_paths, infos, dossier_cible, dossier_cibleGED)
            df_logs.add(f"[XML] {nom_xml} généré.")

            chemin_complet_dwcontrol = os.path.join(dossier_cible, nom_xml)
            if not os.path.isfile(chemin_complet_dwcontrol):
                df_logs.add(f"[ERROR] Fichier .dwcontrol manquant pour {nom_base}")
    else:
        df_logs.add(f"[MISSING] Aucun fichier trouvé pour {nom_base}")

# GÉNÉRATION DU FICHIER DE LOG UNIQUE SANS DOUBLON
log_path = os.path.join(dossier_cible, "log_traitement.txt")
with open(log_path, "w", encoding="utf-8") as f:
    for ligne in sorted(df_logs):
        f.write(ligne + "\n")
print(f"\n📄 Log généré : {log_path}")
