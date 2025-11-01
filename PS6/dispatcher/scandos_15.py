import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QLabel, QHBoxLayout, QTextEdit, QGraphicsView, QGraphicsScene,QFrame,
    QToolBar, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QIcon, QTransform,QFont, QColor, QAction
from PySide6.QtCore import Qt, QSize


import configparser


import os
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QPushButton,
    QGraphicsView, QGraphicsScene, QFrame, QToolBar
)
from PySide6.QtGui import QPixmap, QIcon, QTransform, QAction, QColor, QFont
from PySide6.QtCore import Qt, QSize


import os
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QListWidget, QListWidgetItem, QLabel, QTextEdit,
                               QGraphicsView, QGraphicsScene, QTableWidget, QTableWidgetItem)
from PySide6.QtGui import QPixmap, QIcon, QTransform
from PySide6.QtCore import Qt, QSize

class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1400, 900)

        self.lot_path = lot_path
        self.image_items = []
        self.current_index = 0
        self.zoom_factor = 0.2
        self.plis = []

        # --- Layout principal ---
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        # --- Left : vignettes ---
        self.left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        self.left_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.left_layout, stretch=1)

        # --- Middle : toolbar, image, xml ---
        self.middle_layout = QVBoxLayout()
        self.setup_toolbar()
        self.setup_image_viewer()

        # Zone infos XML (limitée à 6 lignes)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(130)  # environ 6 lignes
        self.middle_layout.addWidget(self.info_text)

        self.main_layout.addLayout(self.middle_layout, stretch=2)

        # --- Right : plis + 3 frames ---
        self.right_layout = QVBoxLayout()

        # Tableau des plis
        self.pli_table = QTableWidget()
        self.pli_table.setColumnCount(5)
        self.pli_table.setHorizontalHeaderLabels(["LUES","IND","PLI","DOC","PG"])
        self.pli_table.cellClicked.connect(self.filter_vignettes_by_pli)
        self.right_layout.addWidget(self.pli_table)

        # 3 Frames existantes
        for title in ["Indexation pli en cours","Recherche Complexe", "Résultat recherche"]:
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("border: 1px solid #cccccc; border-radius: 3px; padding: 5px;")
            layout = QVBoxLayout()
            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold;")
            layout.addWidget(label)
            layout.addStretch()
            frame.setLayout(layout)
            self.right_layout.addWidget(frame)

        self.main_layout.addLayout(self.right_layout, stretch=1)

        # Bouton pour voir toutes les vignettes
        self.btn_all_vignettes = QPushButton("Voir toutes les vignettes")
        self.btn_all_vignettes.clicked.connect(self.show_all_vignettes)
        self.right_layout.insertWidget(0, self.btn_all_vignettes)

        # Bouton pour valider le pli courant
        self.btn_valid_pli = QPushButton("Valider le pli")
        # self.btn_valid_pli.setStyleSheet('QPushButton {background-color: #b0daa3; color: red;}')
        self.btn_valid_pli.setStyleSheet('QPushButton {background-color: #51de26; color: black; font:bold; font-size:16px} QPushButton:hover { color: red; }')
        # self.btn_valid_pli.setStyleSheet('QPushButton:pressed {background-color: #de2644;}')

        self.btn_valid_pli.clicked.connect(self.valid_pli)
        self.right_layout.addWidget(self.btn_valid_pli)

        # Bouton pour livrer le lot courant
        self.btn_livraison_lot = QPushButton("Livraison du lot")
        # self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: #1fb0e0; color: blue; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: white; color: grey; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        self.btn_livraison_lot.setEnabled(False)
        self.btn_livraison_lot.clicked.connect(self.show_all_vignettes)
        self.right_layout.addWidget(self.btn_livraison_lot)

        # Chargement
        self.populate_pli_table()
        self.show_all_vignettes()

    # --- Toolbar et image ---
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))  # 🔹 Taille uniforme des icônes

        # --- Zoom ---
        self.zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom +", self)
        self.zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom -", self)
        self.reset_zoom_action = QAction(QIcon.fromTheme("zoom-original"), "Zoom par défaut", self)

        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)

        # --- Navigation ---
        self.prev_action = QAction(QIcon.fromTheme("go-previous"), "Précédent", self)
        self.next_action = QAction(QIcon.fromTheme("go-next"), "Suivant", self)
        self.prev_action.triggered.connect(self.prev_image)
        self.next_action.triggered.connect(self.next_image)

        # --- Rotation ---
        self.rotate_action = QAction(QIcon.fromTheme("object-rotate-right"), "Rotation 90° page en cours", self)
        self.rotate_action.triggered.connect(self.rotate_image)

        # self.delete_page_action = QAction("Suppression page", self)
        # self.delete_page_action = QAction(QIcon("icons/x_red.svg"), "Suppression page", self)
        # self.delete_page_action.setToolTip("Suppression page en cours")
        # toolbar.setIconSize(QSize(24, 24))  # Ajuste la taille de l’icône sur la barre
        # self.delete_page_action.triggered.connect(self.rotate_image)

        # --- Suppression ---
        self.delete_page_action = QAction(QIcon.fromTheme("edit-delete"), "Suppression page en cours", self)
        self.delete_page_action.setToolTip("Suppression page en cours")  # 🔹 bulle d’info
        self.delete_page_action.triggered.connect(self.delete_image)       # 



        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)
        toolbar.addSeparator()
        toolbar.addAction(self.prev_action)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.rotate_action)
        toolbar.addSeparator()
        toolbar.addAction(self.delete_page_action)

        self.middle_layout.addWidget(toolbar)

    def setup_image_viewer(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.middle_layout.addWidget(self.view)

    # --- Chargement des plis ---
    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except Exception:
            return 0

    def populate_pli_table(self):
        xml_files = sorted([f for f in os.listdir(self.lot_path) if f.lower().endswith(".xml")])
        self.plis = []
        current_pli = None
        for xml_file in xml_files:
            path = os.path.join(self.lot_path, xml_file)
            t = self.get_xml_type(path)
            if t == 2:
                current_pli = {"PLI": len(self.plis)+1, "DOC":1, "PG":0, "files":[path]}
                self.plis.append(current_pli)
            elif t in [3,4] and current_pli is not None:
                current_pli["PG"] += 1
                current_pli["files"].append(path)

        self.pli_table.setRowCount(len(self.plis))
        for i, pli in enumerate(self.plis):
            for col, key in enumerate(["LUES","IND","PLI","DOC","PG"]):
                val = str(pli.get(key,""))
                item = QTableWidgetItem(val)
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)
                self.pli_table.setItem(i, col, item)
            # Couleurs alternées
            color = Qt.GlobalColor.red if i%2==0 else Qt.GlobalColor.green
            for col in range(5):
                self.pli_table.item(i,col).setBackground(color)
            
            #largeur fixex
            self.pli_table.setColumnWidth(0, 40)  # LUES
            self.pli_table.setColumnWidth(1, 40)  # IND
            self.pli_table.setColumnWidth(2, 50)  # PLI
            self.pli_table.setColumnWidth(3, 50)  # DOC
            self.pli_table.setColumnWidth(4, 50)  # PG

    # --- Vignettes ---
    def refresh_vignettes(self, images):
        self.list_widget.clear()
        self.image_items = []
        for img_path, xml_path in images:
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                item = QListWidgetItem(icon, os.path.basename(img_path))
                item.setData(Qt.UserRole, (img_path, xml_path))
                self.list_widget.addItem(item)
                self.image_items.append((img_path, xml_path))
        if self.image_items:
            self.show_image_and_info(self.list_widget.item(0))

    def show_all_vignettes(self):
        images = []
        for pli in self.plis:
            for xml_path in pli["files"]:
                img_path = os.path.splitext(xml_path)[0]+".jpg"
                if os.path.exists(img_path):
                    images.append((img_path, xml_path))
        self.refresh_vignettes(images)

        

    def filter_vignettes_by_pli(self, row, col):
        if row >= len(self.plis):
            return
        pli = self.plis[row]
        images = []
        for xml_path in pli["files"]:
            img_path = os.path.splitext(xml_path)[0]+".jpg"
            if os.path.exists(img_path):
                images.append((img_path, xml_path))
        self.refresh_vignettes(images)

    # --- Affichage image et XML ---
    def show_image_and_info(self, item):
        img_path, xml_path = item.data(Qt.UserRole)
        for i, (path, _) in enumerate(self.image_items):
            if path == img_path:
                self.current_index = i
                break
        self.display_image(img_path)
        self.display_xml_info(xml_path)

    def display_image(self, img_path):
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.scene.clear()
            item = self.scene.addPixmap(pixmap)
            item.setTransformationMode(Qt.SmoothTransformation)
            self.reset_zoom()

    def display_xml_info(self, xml_path):
        if os.path.exists(xml_path):
            infos = self.parse_xml(xml_path)
            text = "\n".join(f"{k} : {v}" for k,v in infos.items() if v)
            lines = text.splitlines()
            self.info_text.setPlainText("\n".join(lines[:6]))
        else:
            self.info_text.setPlainText("(Pas de fichier XML associé)")

    def parse_xml(self, xml_path):
        data = {"Erreur": ""}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            data["Type"] = root.findtext("type","")
            data["Etat"] = root.findtext("etat","")
            data["Rotation"] = root.findtext("rotation","")
            meta = root.find("meta")
            if meta is not None:
                data["Numaxa"] = meta.findtext("numaxa","")
                data["Service"] = meta.findtext("service","")
                data["Pôle"] = meta.findtext("pole","")
                data["Complexe"] = meta.findtext("complexe","")
                data["Gestionnaire"] = meta.findtext("gestionnaire","")
                data["Titre objet"] = meta.findtext("titreobjet","")
        except Exception as e:
            data["Erreur"] = f"Erreur: {e}"
        return data

    # --- Navigation et zoom ---
    def zoom_in(self): self.view.scale(1.2,1.2)
    def zoom_out(self): self.view.scale(1/1.2,1/1.2)
    def reset_zoom(self): self.view.resetTransform(); self.view.scale(self.zoom_factor,self.zoom_factor)
    def prev_image(self):
        if self.current_index>0:
            self.current_index-=1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)
    def next_image(self):
        if self.current_index<len(self.image_items)-1:
            self.current_index+=1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)

    def rotate_image(self):
        if not self.scene.items(): return
        item = self.scene.items()[0]
        pixmap = item.pixmap()
        transform = QTransform().rotate(90)
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.scene.clear()
        self.scene.addPixmap(rotated_pixmap).setTransformationMode(Qt.SmoothTransformation)
        img_path, _ = self.image_items[self.current_index]
        rotated_pixmap.save(img_path)
        self.update_thumbnail()

    def update_thumbnail(self):
        item = self.list_widget.item(self.current_index)
        img_path,_ = self.image_items[self.current_index]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            icon = QIcon(pixmap.scaled(120,120,Qt.KeepAspectRatio))
            item.setIcon(icon)

    def delete_image(self):
        self.btn_livraison_lot.setEnabled(True)
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: #1fb0e0; color: blue; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')

    def valid_pli(self):
        self.btn_livraison_lot.setEnabled(False)
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: white; color: grey; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')

    def closeEvent(self,event):
        if self.parent_window is not None:
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
