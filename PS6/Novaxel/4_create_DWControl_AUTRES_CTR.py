import os
import re
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pyodbc


conn = pyodbc.connect('DSN=WINPASS_SATEC_RW_64;') 
query = """


SELECT 
    IDI=c1.IDI,
    NomFichier=idi.NomFichier,
    TYPE_ENREGISTREMENT='DOC',
    COMPLEXE=isnull(c1.[N° contrat],'')+' - ' + isnull(adr_nom,'')+' '+ isnull(adr_prenom,'')+' ' + isnull(cli_dossier_id,'')+' '+ isnull(cli_siret,'') +' - ' + isnull(POLC1_IMMATRICULATION,'') +
						' - '+isnull(PolC2_ACTIVITE,'') + --' - '+isnull(PolC2_IMMAT,'') + ' - '+isnull(PolC2_NATURE_RISQUE,'') + ' - '+isnull(PolC2_NOM_ASS,'') + ' - '+isnull(POLC2_PRENOM_ASS,'') + ' - '+isnull(PolC2_NOM_ASSURE_SOUSC,'') + 
						isnull(PolC6_ADRESSE1,'')+' - '+ isnull(POLC6_CODE_POSTAL,'')+' ' + isnull(POLC6_VILLE,'')+
						' - NC - WP01',
    POLE='91',
    TYPE_DOCUMENT=case c1.[Type document]
					when	'PC02' then 'PC02 - Pièces d''identité dont : Extrait Kbis, Permis de conduire, Licence, Brevets - Client'
					when	'PC05' then 'PC05 - Mandat SEPA dont : RIB, Relevé de compte/échéance - Client'
					when	'PE01' then	'PE01 - Attestations'
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
					when	'PE01' then	'PE01 - Attestations'
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
	NO_PLI='IDI'+isnull(c1.[IDI],''),

    PRODUIT_LONG = ISNULL(pol_famille_id,'')+'-'+ISNULL(pol_branche_id,'')+'-'+ISNULL(pol_produit_id,'')+'-'+ISNULL(prd_intitule,'')

from TMP_ELC_JCF_NOVAXEL_Autres c1
inner join TMP_ELC_JCF_NOVAXEL_SIN_IDI idi on convert(varchar(7),idi.IDI) = convert(varchar(7),c1.IDI)
inner join pp_contrats on c1.[client contrat id] = pol_client_id and c1.[Ordre contrat]=pol_ordre_contrat
inner join pc_clients on c1.[client contrat id] = cli_client_id
inner join pg_adresses on adr_adresse_id =cli_adresse_id
inner join PA_Produits on Pol_Produit_id=Prd_Produit_id
left join pp_contrats_4roues on polc1_contrat_id = pol_contrat_id
left join pp_contrats_divers on polc2_contrat_id  =pol_contrat_id
left join PP_Contrats_MultiRisques on polc6_contrat_id = pol_contrat_id

--where (idi.NomFichier like '%_2_880.%' or idi.NomFichier like '%_2_881.%' or idi.NomFichier like '%_2_882.%' or idi.NomFichier like '%_2_883.%')

"""
df = pd.read_sql(query, conn)

racine_dossier = r"E:/FICHIERS/Pascal/FDB_50/TPAGES_50"
dossier_cible = r"E:/FICHIERS/Pascal/FDB_50/TPAGES_50/EXPORT_XML_CTR"
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
            
                ("PRODUIT_LONG", "string", row["PRODUIT_LONG"])
            ]
            nom_base = os.path.splitext(fichier)[0]
            generer_dwcontrol(nom_base, [dest], infos, dossier_cible, dossier_cibleGED)
