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


class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.lot_path = lot_path
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1400, 900)

        self.image_items = []  # liste complète de toutes les images du lot
        self.current_index = 0
        self.zoom_factor = 0.2

        # --- Layout principal ---
        self.main_layout = QHBoxLayout(self)
        
        # --- Left: Vignettes ---
        self.left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        self.left_layout.addWidget(self.list_widget)
        # Bouton pour toutes les vignettes
        self.btn_show_all = QPushButton("Toutes les vignettes")
        self.btn_show_all.clicked.connect(self.show_all_vignettes)
        self.left_layout.addWidget(self.btn_show_all)
        self.main_layout.addLayout(self.left_layout, stretch=1)

        # --- Middle: image + XML ---
        self.middle_layout = QVBoxLayout()
        self.setup_toolbar()
        self.setup_image_viewer()

        # Zone XML réduite à max 10 lignes
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        font = self.info_text.font()
        metrics = self.info_text.fontMetrics()
        line_height = metrics.lineSpacing()
        self.info_text.setFixedHeight(line_height * 6)
        self.middle_layout.addWidget(self.info_text, stretch=1)

        self.main_layout.addLayout(self.middle_layout, stretch=2)

        # --- Right: Plis et autres cadres ---
        self.right_layout = QVBoxLayout()
        
        # Tableau des plis
        self.pli_table = QTableWidget()
        self.pli_table.setColumnCount(5)
        self.pli_table.setHorizontalHeaderLabels(["LUES","IND","PLI","DOC","PG"])
        self.pli_table.cellClicked.connect(self.filter_vignettes_by_pli)
        self.right_layout.addWidget(QLabel("Liste des plis du lot", alignment=Qt.AlignCenter))
        self.right_layout.addWidget(self.pli_table)
        
        # Cadres supplémentaires
        for title in ["Logs", "Statistiques", "Résultat Recherche"]:
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

        # --- Chargement des images et plis ---
        self.load_images()
        self.populate_pli_table()
        self.show_all_vignettes()

    # -------------------------
    # Barre d'outils
    # -------------------------
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)

        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_out_action = QAction("Zoom -", self)
        self.reset_zoom_action = QAction("Réinitialiser Zoom", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)

        self.prev_action = QAction("Précédent", self)
        self.next_action = QAction("Suivant", self)
        self.prev_action.triggered.connect(self.prev_image)
        self.next_action.triggered.connect(self.next_image)

        self.rotate_action = QAction("Rotation 90°", self)
        self.rotate_action.triggered.connect(self.rotate_image)

        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)
        toolbar.addSeparator()
        toolbar.addAction(self.prev_action)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.rotate_action)

        self.middle_layout.addWidget(toolbar)

    # -------------------------
    # Zone image
    # -------------------------
    def setup_image_viewer(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.middle_layout.addWidget(self.view)

    # -------------------------
    # Chargement images
    # -------------------------
    def load_images(self):
        self.image_items = []
        for file in sorted(os.listdir(self.lot_path)):
            if file.lower().endswith(".jpg"):
                img_path = os.path.join(self.lot_path, file)
                xml_path = os.path.splitext(img_path)[0] + ".xml"
                self.image_items.append((img_path, xml_path))

    # -------------------------
    # Table des plis
    # -------------------------
    def populate_pli_table(self):
        self.pli_table.setRowCount(0)
        type2_counter = 0
        xml_files = sorted([f for f in os.listdir(self.lot_path) if f.lower().endswith(".xml")])
        for f in xml_files:
            path = os.path.join(self.lot_path, f)
            t = self.get_xml_type(path)
            if t == 2:
                type2_counter += 1
                pages = 0
                start = False
                for f2 in xml_files:
                    path2 = os.path.join(self.lot_path, f2)
                    t2 = self.get_xml_type(path2)
                    if t2 == 2:
                        start = (path2 == path)
                    if start and t2 in [3,4]:
                        pages += 1
                row = self.pli_table.rowCount()
                self.pli_table.insertRow(row)
                values = ["", "", str(type2_counter), "1", str(pages)]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    # Couleur alternée
                    if row % 2 == 0:
                        item.setBackground(Qt.red)
                    else:
                        item.setBackground(Qt.green)
                    self.pli_table.setItem(row, col, item)

    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type","0")
            return int(t) if t.isdigit() else 0
        except:
            return 0

    # -------------------------
    # Filtrage vignettes
    # -------------------------
    def filter_vignettes_by_pli(self, row, column):
        pli_num = int(self.pli_table.item(row, 2).text())
        self.list_widget.clear()
        type2_counter = 0
        for img_path, xml_path in self.image_items:
            t = self.get_xml_type(xml_path)
            if t == 2:
                type2_counter += 1
                if type2_counter != pli_num:
                    continue
            elif t in [3,4]:
                if type2_counter != pli_num:
                    continue
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                item = QListWidgetItem(icon, os.path.basename(img_path))
                item.setData(Qt.UserRole, (img_path, xml_path))
                self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.show_image_and_info(self.list_widget.item(0))

    # -------------------------
    # Bouton toutes les vignettes
    # -------------------------
    def show_all_vignettes(self):
        self.list_widget.clear()
        for img_path, xml_path in self.image_items:
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                item = QListWidgetItem(icon, os.path.basename(img_path))
                item.setData(Qt.UserRole, (img_path, xml_path))
                self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.show_image_and_info(self.list_widget.item(0))

    # -------------------------
    # Affichage image et XML
    # -------------------------
    def show_image_and_info(self, item):
        img_path, xml_path = item.data(Qt.UserRole)
        for i, (p, _) in enumerate(self.image_items):
            if p == img_path:
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
            self.info_text.setPlainText(text if text else "(Pas d'infos XML)")
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
            data["Erreur"] = str(e)
        return data

    # -------------------------
    # Zoom / Navigation / Rotation
    # -------------------------
    def zoom_in(self):
        self.view.scale(1.2, 1.2)
    def zoom_out(self):
        self.view.scale(1/1.2, 1/1.2)
    def reset_zoom(self):
        self.view.resetTransform()
        self.view.scale(self.zoom_factor, self.zoom_factor)
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)
    def next_image(self):
        if self.current_index < len(self.image_items)-1:
            self.current_index += 1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)
    def rotate_image(self):
        if not self.scene.items():
            return
        item = self.scene.items()[0]
        pixmap = item.pixmap()
        transform = QTransform().rotate(90)
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.scene.clear()
        new_item = self.scene.addPixmap(rotated_pixmap)
        new_item.setTransformationMode(Qt.SmoothTransformation)
        img_path, _ = self.image_items[self.current_index]
        rotated_pixmap.save(img_path)
        self.update_thumbnail()
    def update_thumbnail(self):
        if self.current_index < 0 or self.current_index >= self.list_widget.count():
            return
        item = self.list_widget.item(self.current_index)
        img_path, _ = self.image_items[self.current_index]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
            item.setIcon(icon)

    # -------------------------
    # Re-affichage de la fenêtre principale
    # -------------------------
    def closeEvent(self, event):
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
