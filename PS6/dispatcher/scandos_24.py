import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from PySide6.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
                               QLabel,  QTextEdit, QGraphicsView, QGraphicsScene,QFrame,    QToolBar,QLineEdit,   QSizePolicy ,
                               QCheckBox 
                               )
from PySide6.QtGui import QPixmap, QIcon, QTransform,QFont, QColor, QAction,QPalette
from PySide6.QtCore import Qt, QSize, QTimer

import configparser


class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1400, 900)

        self.lot_path = lot_path
        self.image_items = []
        self.pages_lues = set()
        self.current_index = 0
        self.zoom_factor = 0.2
        self.plis = []
        self.frames = {}

        # Layout principal
        main_v_layout = QVBoxLayout(self)
        self.setLayout(main_v_layout)

        self.main_layout = QHBoxLayout()
        main_v_layout.addLayout(self.main_layout, stretch=1)

        # Barre d'état
        self.status_label = QLabel("En attente d'action...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #596fab;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }
        """)
        main_v_layout.addWidget(self.status_label)

        # --- Left : vignettes ---
        self.left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setFlow(QListWidget.LeftToRight)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        self.left_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.left_layout, stretch=1)

        # --- Middle : toolbar + image + xml ---
        self.middle_layout = QVBoxLayout()
        self.setup_toolbar()
        self.setup_image_viewer()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(160)
        self.middle_layout.addWidget(self.info_text)
        self.main_layout.addLayout(self.middle_layout, stretch=2)

        # --- Right : plis + 3 frames ---
        self.right_layout = QVBoxLayout()

        self.pli_table = QTableWidget()
        self.pli_table.setColumnCount(5)
        self.pli_table.setHorizontalHeaderLabels(["LUES","IND","PLI","DOC","PG"])
        self.pli_table.cellClicked.connect(self.filter_vignettes_by_pli)
        self.right_layout.addWidget(self.pli_table)

        # Frame 1 : indexation pli
        self.frames["indexation"] = self.create_frame_indexation()
        self.right_layout.addWidget(self.frames["indexation"])

        # Frame 2 : recherche
        self.frames["recherche"] = self.create_frame_generic("Recherche Complexe")
        self.right_layout.addWidget(self.frames["recherche"])

        # Frame 3 : résultat recherche
        self.frames["resultat"] = self.create_frame_generic("Résultat recherche")
        self.right_layout.addWidget(self.frames["resultat"])

        # Boutons
        self.btn_all_vignettes = QPushButton("Voir toutes les vignettes")
        self.btn_all_vignettes.setStyleSheet('QPushButton {background-color: #EEEEEE; color: black; font:bold; font-size:12px} QPushButton:hover { background-color: #E06609; color: #49F276; }')
        self.btn_all_vignettes.clicked.connect(self.show_all_vignettes)
        self.right_layout.insertWidget(0, self.btn_all_vignettes)

        self.btn_valid_pli = QPushButton("Valider le pli")
        self.btn_valid_pli.setStyleSheet('QPushButton {background-color: #51de26; color: black; font:bold; font-size:16px} QPushButton:hover { color: red; }')
        self.btn_valid_pli.clicked.connect(self.valid_pli)
        self.right_layout.addWidget(self.btn_valid_pli)

        self.btn_livraison_lot = QPushButton("Livraison du lot")
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: white; color: grey; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        self.btn_livraison_lot.setEnabled(False)
        self.btn_livraison_lot.clicked.connect(self.show_all_vignettes)
        self.right_layout.addWidget(self.btn_livraison_lot)

        self.main_layout.addLayout(self.right_layout, stretch=1)

        # Chargement des plis et vignettes
        self.populate_pli_table()
        self.show_all_vignettes()
        self.info_text.clear()
        self.clear_indexation_fields()
        self.update_page_status(False)

    # ---------------- Toolbar ----------------
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        # Actions
        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_out_action = QAction("Zoom -", self)
        self.reset_zoom_action = QAction("Zoom par défaut", self)
        self.prev_action = QAction("Précédent", self)
        self.next_action = QAction("Suivant", self)
        self.rotate_action = QAction("Rotation 90°", self)
        self.delete_page_action = QAction("Suppression page", self)

        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        self.prev_action.triggered.connect(self.prev_image)
        self.next_action.triggered.connect(self.next_image)
        self.rotate_action.triggered.connect(self.rotate_image)
        self.delete_page_action.triggered.connect(self.delete_image)

        for action in [self.zoom_in_action, self.zoom_out_action, self.reset_zoom_action,
                       self.prev_action, self.next_action, self.rotate_action, self.delete_page_action]:
            toolbar.addAction(action)
            toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Statut page
        self.page_status = QLineEdit("Page non lue")
        self.page_status.setReadOnly(True)
        self.page_status.setAlignment(Qt.AlignCenter)
        self.page_status.setFixedWidth(150)
        self.middle_layout.addWidget(toolbar)
        self.update_page_status(False)

    def setup_image_viewer(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.middle_layout.addWidget(self.view)

    # ---------------- Création des frames ----------------
    def create_frame_indexation(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setMaximumHeight(150)
        layout = QVBoxLayout(frame)

        label_title = QLabel("Indexation pli en cours")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-weight:bold; font-size:12px;background-color:#596fab;color:white;")
        layout.addWidget(label_title)

        grid = QGridLayout()
        self.champ_complexe = QLineEdit()
        self.champ_pole = QLineEdit()
        self.champ_gestionnaire = QLineEdit()
        self.champ_titre_objet = QLineEdit()

        for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
            champ.setReadOnly(True)
            champ.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            champ.setStyleSheet("QLineEdit { background-color:#f9f9f9; color:#003366; font-weight:bold; font-size:10px; }")

        labels = [("Complexe", self.champ_complexe),
                  ("Pôle", self.champ_pole),
                  ("Gestionnaire", self.champ_gestionnaire),
                  ("Titre objet", self.champ_titre_objet)]

        for i, (text, champ) in enumerate(labels):
            lbl = QLabel(f"{text} :")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignCenter)
            lbl.setStyleSheet("font-weight:bold; font-size:12px; background-color:#596fab;color:white;")
            grid.addWidget(lbl, i, 0)
            grid.addWidget(champ, i, 1)
            champ.textChanged.connect(lambda t, c=champ: c.setToolTip(t))

        layout.addLayout(grid)
        return frame

    def create_frame_generic(self, title):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight:bold; font-size:12px;background-color:#596fab;color:white;")
        layout.addWidget(label)
        layout.addStretch()
        return frame

    # ---------------- Chargement plis ----------------
    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except:
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
                item.setFont(QFont("", -1, QFont.Bold))
                item.setTextAlignment(Qt.AlignCenter)
                self.pli_table.setItem(i, col, item)

    # ---------------- Vignettes ----------------
    def refresh_vignettes(self, images):
        self.list_widget.clear()
        self.image_items = []
        for img_path, xml_path in images:
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
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
                img_path = os.path.splitext(xml_path)[0] + ".jpg"
                if os.path.exists(img_path):
                    images.append((img_path, xml_path))
        self.refresh_vignettes(images)

    def filter_vignettes_by_pli(self, row, col):
        if row >= len(self.plis):
            return
        pli = self.plis[row]
        images = []
        for xml_path in pli["files"]:
            img_path = os.path.splitext(xml_path)[0] + ".jpg"
            if os.path.exists(img_path):
                images.append((img_path, xml_path))
        self.refresh_vignettes(images)
        if pli["files"]:
            infos = self.parse_xml(pli["files"][0])
            self.champ_complexe.setText(infos.get("Complexe",""))
            self.champ_pole.setText(infos.get("Pôle",""))
            self.champ_gestionnaire.setText(infos.get("Gestionnaire",""))
            self.champ_titre_objet.setText(infos.get("Titre objet",""))
        self.update_page_status(False)

    # ---------------- Affichage image et XML ----------------
    def show_image_and_info(self, item):
        img_path, xml_path = item.data(Qt.UserRole)
        for i, (path, _) in enumerate(self.image_items):
            if path == img_path:
                self.current_index = i
                break
        self.display_image(img_path)
        self.display_xml_info(xml_path)
        if img_path not in self.pages_lues:
            self.pages_lues.add(img_path)
        self.update_page_status(True)
        self.check_all_pages_lues()

    def display_image(self, img_path):
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.reset_zoom()

    def display_xml_info(self, xml_path):
        infos = self.parse_xml(xml_path)
        text = "\n".join(f"{k} : {v}" for k,v in infos.items() if v)
        self.info_text.setPlainText("\n".join(text.splitlines()[:7]))

    def parse_xml(self, xml_path):
        data = {}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            data["Type"] = root.findtext("type","")
            meta = root.find("meta")
            if meta is not None:
                data["Pôle"] = meta.findtext("pole","")
                data["Complexe"] = meta.findtext("complexe","")
                data["Gestionnaire"] = meta.findtext("gestionnaire","")
                data["Titre objet"] = meta.findtext("titreobjet","")
        except:
            pass
        return data

    # ---------------- Navigation et zoom ----------------
    def zoom_in(self): self.view.scale(1.2,1.2)
    def zoom_out(self): self.view.scale(1/1.2,1/1.2)
    def reset_zoom(self): self.view.resetTransform(); self.view.scale(self.zoom_factor,self.zoom_factor)

    def prev_image(self):
        if self.current_index>0:
            self.current_index-=1
            self.show_image_and_info(self.list_widget.item(self.current_index))

    def next_image(self):
        if self.current_index<len(self.image_items)-1:
            self.current_index+=1
            self.show_image_and_info(self.list_widget.item(self.current_index))

    def rotate_image(self):
        if not self.scene.items(): return
        item = self.scene.items()[0]
        pixmap = item.pixmap()
        rotated = pixmap.transformed(QTransform().rotate(90))
        self.scene.clear()
        self.scene.addPixmap(rotated)
        img_path,_ = self.image_items[self.current_index]
        rotated.save(img_path)
        self.update_thumbnail()

    def update_thumbnail(self):
        item = self.list_widget.item(self.current_index)
        img_path,_ = self.image_items[self.current_index]
        pixmap = QPixmap(img_path)
        icon = QIcon(pixmap.scaled(120,120,Qt.KeepAspectRatio))
        item.setIcon(icon)

    def delete_image(self):
        self.btn_livraison_lot.setEnabled(True)

    def valid_pli(self):
        self.btn_livraison_lot.setEnabled(False)

    def update_page_status(self, lue: bool):
        if lue:
            self.page_status.setText("Page lue")
        else:
            self.page_status.setText("Page non lue")

    def check_all_pages_lues(self):
        if not self.image_items: return
        current_xml = self.image_items[self.current_index][1]
        pli_index = None
        for i, pli in enumerate(self.plis):
            if current_xml in pli["files"]:
                pli_index = i
                break
        if pli_index is None: return
        pli = self.plis[pli_index]
        toutes_lues = all(os.path.splitext(f)[0]+".jpg" in self.pages_lues for f in pli["files"])
        item = self.pli_table.item(pli_index, 0)
        if not item:
            item = QTableWidgetItem()
            self.pli_table.setItem(pli_index, 0, item)
        item.setText("L" if toutes_lues else "")

    def clear_indexation_fields(self):
        for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
            champ.clear()

    # ---------------- Fermeture ----------------
    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        super().closeEvent(event)



class LotsSummary(QWidget):
    """Fenêtre principale pour sélectionner un dossier LOTS et afficher un résumé"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choix et Résumé des Lots")
        self.resize(1500, 700)
        self.layout = QVBoxLayout(self)
        self.open_viewers = []
        self.lots_dir = None
        
        # --- Lecture config.ini ---
        self.config = self.load_config()

        # --------------------------
        # Bouton selection dossier
        # --------------------------
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        self.layout.addWidget(self.btn_select_dir)

        # --------------------------
        # Tableau des Lots
        # --------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(18)  # AJUSTÉ !
        self.table.setHorizontalHeaderLabels([
            "N° SATEC", "Service", "N° Lot",

            "Date Création", "Créé par", "Ouvert le", "Ouvert par",
            "Verrouillé", "Pli", "Page", "Date Livraison",

            "NbJPG", "NbXT1", "NbXT2",
            "NbXT3", "NbXT4", "NbPDF", "NbPages"
        ])

        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_lot_viewer)
        self.layout.addWidget(self.table)

        self.setup_table_style()

        self.check_widgets = {}

        # Chargement auto si config.ini
        if self.config and os.path.exists(self.config.get("lots_path", "")):
            self.lots_dir = self.config["lots_path"]
            self.load_summary(self.lots_dir)
        else:
            print("⚠️ Aucun chemin valide dans config.ini")

    # --------------------------------------------------------------------
    # STYLE TABLE
    # --------------------------------------------------------------------
    def setup_table_style(self):
        """Style général de la grille"""
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #CCCCCC;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #E8EEF7;
                font-weight: bold;
                font-size: 13px;
                padding: 4px;
                border: 1px solid #AAAAAA;
            }
        """)

        # Colonnes XML SATEC
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 250)

        # Colonnes "Nb..."
        for col in range(11, 18):
            self.table.setColumnWidth(col, 60)

        # Colonnes supplémentaires
        self.table.setColumnWidth(3, 150)  # Date Création
        self.table.setColumnWidth(4, 120)  # Créé par
        self.table.setColumnWidth(5, 150)  # Ouvert le
        self.table.setColumnWidth(6, 120)  # Ouvert par
        self.table.setColumnWidth(7, 100)  # Verrouillé
        self.table.setColumnWidth(8, 70)   # Pli
        self.table.setColumnWidth(9, 70)   # Page
        self.table.setColumnWidth(10, 150) # Date Livraison

    # --------------------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------------------
    def load_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), "config.ini")

        if not os.path.exists(config_path):
            print(f"⚠️ config.ini introuvable")
            return None

        config.read(config_path, encoding="utf-8")
        if "PARAMS" in config:
            return {"lots_path": config["PARAMS"].get("lots_path", "")}
        return None

    # --------------------------------------------------------------------
    # SELECTION DOSSIER LOTS
    # --------------------------------------------------------------------
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.lots_dir = directory
            self.load_summary(directory)

    # --------------------------------------------------------------------
    # EXTRACTION XML TYPE 1
    # --------------------------------------------------------------------
    def extract_type1_info(self, lot_dir):
        for file in os.listdir(lot_dir):
            if file.lower().endswith(".xml"):
                path = os.path.join(lot_dir, file)
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()

                    if root.findtext("type", "").strip() == "1":
                        meta = root.find("meta")
                        if meta is None:
                            return "", ""
                        return (
                            meta.findtext("numaxa", "").strip(),
                            meta.findtext("service", "").strip()
                        )
                except Exception:
                    pass
        return "", ""

    # --------------------------------------------------------------------
    # CENTRAGE DE LA CASE A COCHER
    # --------------------------------------------------------------------
    def make_centered_checkbox(self, checked=False):
        """Retourne un widget contenant une checkbox centrée dans la cellule."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        chk = QCheckBox()
        chk.setChecked(checked)
        chk.setEnabled(False)     # ❌ l'utilisateur NE PEUT PAS cliquer

        layout.addWidget(chk)
        return widget, chk
    
    # --------------------------------------------------------------------
    # CHARGEMENT DES LOTS
    # --------------------------------------------------------------------
    def load_summary(self, lots_dir):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)

            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:

                numaxa, service = self.extract_type1_info(subpath)

                jpg_count = 0
                xml_counts = {1: 0, 2: 0, 3: 0, 4: 0}

                for file in os.listdir(subpath):
                    fpath = os.path.join(subpath, file)

                    if file.lower().endswith(".jpg"):
                        jpg_count += 1

                    elif file.lower().endswith(".xml"):
                        t = self.get_xml_type(fpath)
                        if t in xml_counts:
                            xml_counts[t] += 1

                nb_plis = xml_counts[2]
                nb_pages_total = xml_counts[3] + xml_counts[4]

                # Date actuelle
                date_creation = datetime.now().strftime("%d/%m/%Y %H:%M")

                # Ligne
                row = self.table.rowCount()
                self.table.insertRow(row)

                values = [
                    numaxa, service, subdir,
                    date_creation, "dispatcher", "", "",  # ouvert le / par vides
                    "",   # Verrouillé → case cochable, valeur mise plus tard
                    str(nb_plis), str(nb_pages_total), 
                    "",#date livraison
                    str(jpg_count), str(xml_counts[1]), str(xml_counts[2]),
                    str(xml_counts[3]), str(xml_counts[4]),
                    str(nb_plis), str(nb_pages_total)
                ]

                for col, val in enumerate(values):

                    # --------------------
                    # COCHAGE (col 7)
                    # --------------------
                    # if col == 7:
                    #     item = QTableWidgetItem()
                    #     item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    #     item.setCheckState(Qt.Unchecked)
                    #     self.table.setItem(row, col, item)
                    #     continue

                    if col == 7:  # colonne Verrouillé -> checkbox centrée
                        widget, chk = self.make_centered_checkbox(False)
                        self.table.setCellWidget(row, col, widget)
                        self.check_widgets[(row, col)] = chk  # pour pouvoir la modifier plus tard
                        continue

                    #modification case par code
                    
                    # chk = self.table.check_widgets.get((row, 7))
                    # #cocher
                    # if chk:
                    #     chk.setChecked(True)

                    # chk = self.table.check_widgets.get((row, 7))
                    # #decocher
                    # if chk:
                    #     chk.setChecked(False)


                    item = QTableWidgetItem(val)
                    item.setToolTip(val)

                    # Alignement centré sauf pour XML SATEC/service et dates
                    if col not in (0, 1, 3, 10):
                        item.setTextAlignment(Qt.AlignCenter)

                    # Style spécial XML type 1 (cols 0 et 1)
                    if col in (0, 1):
                        item.setBackground(QColor("#FFF6D1"))
                        f = item.font()
                        f.setBold(True)
                        item.setFont(f)
                        item.setForeground(QColor("#003366"))

                    self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)

    # --------------------------------------------------------------------
    # TYPE XML
    # --------------------------------------------------------------------
    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except:
            return 0

    # --------------------------------------------------------------------
    # OUVERTURE LOT VIEWER
    # --------------------------------------------------------------------
    def open_lot_viewer(self, row, column):
        if not self.lots_dir:
            return

        lot_name = self.table.item(row, 2).text()
        lot_path = os.path.join(self.lots_dir, lot_name)

        if os.path.exists(lot_path):
            
            viewer = LotViewer(lot_path)
            viewer.parent_window = self
            self.open_viewers.append(viewer)

            viewer.show()
            viewer.raise_()
            viewer.activateWindow()
            self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsSummary()
    window.show()
    sys.exit(app.exec())
