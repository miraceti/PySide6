import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QLabel, QHBoxLayout, QTextEdit, QGraphicsView, QGraphicsScene,QFrame,
    QToolBar, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QIcon, QTransform
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction

import configparser

class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path, parent=None):
        super().__init__(parent)
        self.parent_window = parent # 🔹 on garde la référence du parent
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1400, 800)  # Augmente la largeur pour accommoder les 3 colonnes

        # Layout principal (horizontal)
        self.main_layout = QHBoxLayout(self)

        # --- Left Layout (vignettes) ---
        self.left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        self.left_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.left_layout, stretch=1)  # 1/4 de la largeur

        # --- Middle Layout (image + XML) ---
        self.middle_layout = QVBoxLayout()

        # Barre d'outils
        self.setup_toolbar()

        # Zone d'aperçu image
        self.setup_image_viewer()

        # Zone infos XML
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.middle_layout.addWidget(self.info_text, stretch=1)

        self.main_layout.addLayout(self.middle_layout, stretch=2)  # 2/4 de la largeur

        # --- Right Layout (4 sous-layouts encadrés avec labels centrés) ---
        self.right_layout = QVBoxLayout()

        # Frame 1 : Métadonnées
        self.frame1 = QFrame()
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setStyleSheet("border: 1px solid #cccccc; border-radius: 3px; padding: 5px;")
        frame1_layout = QVBoxLayout()
        self.label1 = QLabel("Indexation actuelle")
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setStyleSheet("font-weight: bold;")
        frame1_layout.addWidget(self.label1)
        frame1_layout.addStretch()
        self.frame1.setLayout(frame1_layout)
        self.right_layout.addWidget(self.frame1)

        # Frame 2 : Logs
        self.frame2 = QFrame()
        self.frame2.setFrameShape(QFrame.StyledPanel)
        self.frame2.setStyleSheet("border: 1px solid #cccccc; border-radius: 3px; padding: 5px;")
        frame2_layout = QVBoxLayout()
        self.label2 = QLabel("Liste Complexe trouvés")
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setStyleSheet("font-weight: bold;")
        frame2_layout.addWidget(self.label2)
        frame2_layout.addStretch()
        self.frame2.setLayout(frame2_layout)
        self.right_layout.addWidget(self.frame2)

        # Frame 3 : Statistiques
        self.frame3 = QFrame()
        self.frame3.setFrameShape(QFrame.StyledPanel)
        self.frame3.setStyleSheet("border: 1px solid #cccccc; border-radius: 3px; padding: 5px;")
        frame3_layout = QVBoxLayout()
        self.label3 = QLabel("Recherche")
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setStyleSheet("font-weight: bold;")
        frame3_layout.addWidget(self.label3)
        frame3_layout.addStretch()
        self.frame3.setLayout(frame3_layout)
        self.right_layout.addWidget(self.frame3)

        # Frame 4 : Actions
        self.frame4 = QFrame()
        self.frame4.setFrameShape(QFrame.StyledPanel)
        self.frame4.setStyleSheet("border: 1px solid #cccccc; border-radius: 3px; padding: 5px;")
        frame4_layout = QVBoxLayout()
        self.label4 = QLabel("Résultat Recherche")
        self.label4.setAlignment(Qt.AlignCenter)
        self.label4.setStyleSheet("font-weight: bold;")
        frame4_layout.addWidget(self.label4)
        frame4_layout.addStretch()
        self.frame4.setLayout(frame4_layout)
        self.right_layout.addWidget(self.frame4)


        self.main_layout.addLayout(self.right_layout, stretch=1)  # 1/4 de la largeur

        # Variables pour gérer les images
        self.lot_path = lot_path
        self.image_items = []
        self.current_index = 0
        self.zoom_factor = 0.2
        self.load_images()

    def setup_toolbar(self):
        """Configure la barre d'outils avec boutons de zoom, navigation et rotation et enregistrement"""
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Boutons de zoom
        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_out_action = QAction("Zoom -", self)
        self.reset_zoom_action = QAction("Réinitialiser Zoom", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)

        # Boutons de navigation
        self.prev_action = QAction("Précédent", self)
        self.next_action = QAction("Suivant", self)
        self.prev_action.triggered.connect(self.prev_image)
        self.next_action.triggered.connect(self.next_image)

        # Bouton de rotation
        self.rotate_action = QAction("Rotation 90°", self)
        self.rotate_action.triggered.connect(self.rotate_image)

        # Bouton d'enregistrement
        # self.save_action = QAction("Enregistrer", self)
        # self.save_action.triggered.connect(self.save_rotated_image)


        # Ajout des actions à la barre d'outils
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)
        toolbar.addSeparator()
        toolbar.addAction(self.prev_action)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.rotate_action)
        # toolbar.addAction(self.save_action)

        # self.right_layout.addWidget(toolbar)

        self.middle_layout.addWidget(toolbar)

    def setup_image_viewer(self):
        """Configure la zone d'affichage des images avec QGraphicsView"""
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)  # Active le défilement
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # self.right_layout.addWidget(self.view)
        self.middle_layout.addWidget(self.view)

    def load_images(self):
        """Charge toutes les images .jpg du lot et leurs XML associés"""
        self.image_items = []
        for file in sorted(os.listdir(self.lot_path)):
            if file.lower().endswith(".jpg"):
                img_path = os.path.join(self.lot_path, file)
                xml_path = os.path.splitext(img_path)[0] + ".xml"
                self.image_items.append((img_path, xml_path))

        # Remplit la liste des vignettes
        for img_path, xml_path in self.image_items:
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                item = QListWidgetItem(icon, os.path.basename(img_path))
                item.setData(Qt.UserRole, (img_path, xml_path))
                self.list_widget.addItem(item)

        # Affiche la première image si elle existe
        if self.image_items:
            self.show_image_and_info(self.list_widget.item(0))

    def show_image_and_info(self, item):
        """Affiche l'image et les infos XML de l'item sélectionné"""
        img_path, xml_path = item.data(Qt.UserRole)

        # Trouve l'index de l'image cliquée
        for i, (path, _) in enumerate(self.image_items):
            if path == img_path:
                self.current_index = i
                break

        # Affiche l'image et les infos XML
        self.display_image(img_path)
        self.display_xml_info(xml_path)

    def display_image(self, img_path):
        """Affiche l'image dans le QGraphicsView avec le zoom actuel"""
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.scene.clear()
            item = self.scene.addPixmap(pixmap)
            item.setTransformationMode(Qt.SmoothTransformation)
            self.reset_zoom()  # Applique le zoom initial

    def display_xml_info(self, xml_path):
        """Affiche les infos XML dans la zone de texte"""
        if os.path.exists(xml_path):
            infos = self.parse_xml(xml_path)  # Appel à parse_xml
            text = "\n".join(f"{k} : {v}" for k, v in infos.items() if v)
            self.info_text.setPlainText(text if text else "(Pas d'infos XML)")
        else:
            self.info_text.setPlainText("(Pas de fichier XML associé)")

    def parse_xml(self, xml_path):
        """Retourne les champs utiles du XML sous forme de dictionnaire"""
        data = {"Erreur": ""}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            data["Type"] = root.findtext("type", "")
            data["Etat"] = root.findtext("etat", "")
            data["Rotation"] = root.findtext("rotation", "")
            meta = root.find("meta")
            if meta is not None:
                data["Numaxa"] = meta.findtext("numaxa", "")
                data["Service"] = meta.findtext("service", "")
                data["Pôle"] = meta.findtext("pole", "")
                data["Complexe"] = meta.findtext("complexe", "")
                data["Gestionnaire"] = meta.findtext("gestionnaire", "")
                data["Titre objet"] = meta.findtext("titreobjet", "")
        except ET.ParseError as e:
            data["Erreur"] = f"Erreur de parsing XML : {e}"
        except Exception as e:
            data["Erreur"] = f"Erreur inattendue : {e}"
        return data

    # Fonctions de zoom
    def zoom_in(self):
        """Zoom avant sur l'image"""
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom arrière sur l'image"""
        self.view.scale(1 / 1.2, 1 / 1.2)

    def reset_zoom(self):
        """Réinitialise le zoom à la taille initiale"""
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)  # Applique le zoom initial réduit

    # Fonctions de navigation
    def prev_image(self):
        """Affiche l'image précédente"""
        if self.current_index > 0:
            self.current_index -= 1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)

    def next_image(self):
        """Affiche l'image suivante"""
        if self.current_index < len(self.image_items) - 1:
            self.current_index += 1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)

    def rotate_image(self):
        """Tourne l'image de 90° et écrase l'originale"""
        if not self.scene.items():
            return  # Pas d'image à tourner

        # Récupère l'image actuelle
        item = self.scene.items()[0]
        pixmap = item.pixmap()

        # Applique une rotation de 90°
        transform = QTransform().rotate(90)
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

        # Remplace l'image actuelle par la pixmap tournée
        self.scene.clear()
        new_item = self.scene.addPixmap(rotated_pixmap)
        new_item.setTransformationMode(Qt.SmoothTransformation)

        # Écrase l'image initiale avec la version tournée
        img_path, _ = self.image_items[self.current_index]
        rotated_pixmap.save(img_path)
        print(f"Image tournée enregistrée (écrasement) : {img_path}")

        # Met à jour la vignette dans la liste
        self.update_thumbnail()

    def update_thumbnail(self):
        """Met à jour la vignette de l'image actuelle dans la liste"""
        if self.current_index < 0 or self.current_index >= self.list_widget.count():
            return

        # Récupère l'item actuel dans la liste
        item = self.list_widget.item(self.current_index)

        # Met à jour l'icône de la vignette avec la nouvelle image tournée
        img_path, _ = self.image_items[self.current_index]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
            item.setIcon(icon)

    def closeEvent(self, event):
        """Quand la fenêtre du lot se ferme, on réaffiche la fenêtre principale"""
        if getattr(self, "parent_window", None) is not None:
            self.parent_window.show()
        super().closeEvent(event)


class LotsSummary(QWidget):
    """Fenêtre principale pour sélectionner un dossier LOTS et afficher un résumé"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choix et Résumé des Lots")
        self.resize(1100, 600)
        self.layout = QVBoxLayout(self)
        self.open_viewers = []  # Garde les références des fenêtres secondaires
        self.lots_dir = None

        # --- Lecture du fichier de configuration ---
        self.config = self.load_config()

        # Bouton pour sélectionner le dossier LOTS
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        self.layout.addWidget(self.btn_select_dir)

        # Tableau pour afficher les lots
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Lot (dossier)", "Nb JPG", "Nb XML Type 1", "Nb XML Type 2",
            "Nb XML Type 3", "Nb XML Type 4", "Nb PDF (plis)", "Nb Pages PDF (total)"
        ])
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_lot_viewer)
        self.layout.addWidget(self.table)

        # --- Si un chemin est défini dans le .ini, on le charge automatiquement ---
        if self.config and os.path.exists(self.config.get("lots_path", "")):
            self.lots_dir = self.config["lots_path"]
            self.load_summary(self.lots_dir)
        else:
            print("⚠️ Aucun chemin valide trouvé dans config.ini, sélection manuelle requise.")

    def load_config(self):
        """Charge les paramètres depuis un fichier config.ini"""
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")

        if not os.path.exists(config_path):
            print(f"⚠️ Fichier config.ini introuvable à {config_path}")
            return None

        config.read(config_path, encoding="utf-8")
        if "PARAMS" in config:
            return {
                "lots_path": config["PARAMS"].get("lots_path", "")
            }
        else:
            print("⚠️ Section [PARAMS] introuvable dans config.ini")
            return None

    def select_directory(self):
        """Ouvre une boîte de dialogue pour sélectionner le dossier LOTS"""
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.lots_dir = directory
            self.load_summary(directory)

    def load_summary(self, lots_dir):
        """Charge et affiche les informations des lots dans le tableau"""
        self.table.setRowCount(0)
        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)
            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:
                jpg_count = 0
                xml_counts = {1: 0, 2: 0, 3: 0, 4: 0}

                for file in os.listdir(subpath):
                    filepath = os.path.join(subpath, file)
                    if file.lower().endswith(".jpg"):
                        jpg_count += 1
                    elif file.lower().endswith(".xml"):
                        xml_type = self.get_xml_type(filepath)
                        if xml_type in xml_counts:
                            xml_counts[xml_type] += 1

                nb_plis = xml_counts[2]  # Nb de PDF à créer (type 2 = pli)
                nb_pages_total = xml_counts[3] + xml_counts[4]  # Pages des plis

                # Ajoute une ligne au tableau
                row = self.table.rowCount()
                self.table.insertRow(row)
                values = [
                    subdir, str(jpg_count),
                    str(xml_counts[1]), str(xml_counts[2]),
                    str(xml_counts[3]), str(xml_counts[4]),
                    str(nb_plis), str(nb_pages_total)
                ]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(val)
                    if col != 0:  # Alignement centré sauf pour la première colonne
                        item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

    def get_xml_type(self, filepath):
        """Retourne le type du fichier XML (1, 2, 3 ou 4)"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except Exception:
            return 0

    def open_lot_viewer(self, row, column):
        """Ouvre la fenêtre de visualisation pour le lot sélectionné"""
        if not self.lots_dir:
            return
        
        lot_name = self.table.item(row, 0).text()
        lot_path = os.path.join(self.lots_dir, lot_name)

        if os.path.exists(lot_path):
            # créer le viewer SANS parent pour qu'il soit une fenêtre top-level
            viewer = LotViewer(lot_path)          # <- pas de parent ici
            viewer.parent_window = self           # on garde la référence au parent manuellement
            self.open_viewers.append(viewer)      # garder la référence pour éviter le GC

            # afficher la fenêtre secondaire, puis cacher la principale (ordre plus sûr)
            viewer.show()
            viewer.raise_()
            viewer.activateWindow()
            self.hide()

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsSummary()
    window.show()
    sys.exit(app.exec())
