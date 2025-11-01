import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QSplitter
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize


class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images"""
    def __init__(self, lot_path):
        super().__init__()
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1000, 700)

        layout = QHBoxLayout(self)

        # Liste des images en vignettes
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image)
        layout.addWidget(self.list_widget, 2)

        # Zone d’aperçu
        self.preview_label = QLabel("Sélectionnez une image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label, 3)

        self.load_images(lot_path)

    def load_images(self, lot_path):
        """Charge toutes les images .jpg du lot"""
        for file in sorted(os.listdir(lot_path)):
            if file.lower().endswith(".jpg"):
                img_path = os.path.join(lot_path, file)
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                    item = QListWidgetItem(icon, file)
                    item.setData(Qt.UserRole, img_path)
                    self.list_widget.addItem(item)

    def show_image(self, item):
        """Affiche en grand l’image cliquée"""
        img_path = item.data(Qt.UserRole)
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))


class LotsSummary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résumé des Lots")
        self.resize(1100, 600)

        self.open_viewers = []  # 🔹 garder références aux fenêtres secondaires

        layout = QVBoxLayout(self)

        # Bouton sélection dossier
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        layout.addWidget(self.btn_select_dir)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Lot (dossier)", "Nb JPG",
            "Nb XML Type 1", "Nb XML Type 2", "Nb XML Type 3", "Nb XML Type 4",
            "Nb PDF (plis)", "Nb Pages PDF (total)"
        ])
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_lot_viewer)
        layout.addWidget(self.table)

        self.lots_dir = None

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.lots_dir = directory
            self.load_summary(directory)

    def load_summary(self, lots_dir):
        self.table.setRowCount(0)

        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)
            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:
                jpg_count = 0
                xml_counts = {1: 0, 2: 0, 3: 0, 4: 0}

                # Comptage des fichiers
                for file in os.listdir(subpath):
                    filepath = os.path.join(subpath, file)
                    f_lower = file.lower()
                    if f_lower.endswith(".jpg"):
                        jpg_count += 1
                    elif f_lower.endswith(".xml"):
                        xml_type = self.get_xml_type(filepath)
                        if xml_type in xml_counts:
                            xml_counts[xml_type] += 1

                nb_plis = xml_counts[2]                 # = nb de PDF à créer
                nb_pages_total = xml_counts[3] + xml_counts[4]  # pages sur tous les PDF

                # Ajout de la ligne
                row = self.table.rowCount()
                self.table.insertRow(row)
                values = [
                    subdir,
                    str(jpg_count),
                    str(xml_counts[1]),
                    str(xml_counts[2]),
                    str(xml_counts[3]),
                    str(xml_counts[4]),
                    str(nb_plis),
                    str(nb_pages_total)
                ]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(val)
                    if col != 0:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

    def get_xml_type(self, filepath):
        """Retourne la valeur entière du champ <type> dans un fichier XML, 0 si erreur."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except Exception:
            return 0

    def open_lot_viewer(self, row, column):
        """Ouvre une fenêtre secondaire avec toutes les images du lot sélectionné"""
        if not self.lots_dir:
            return
        lot_name = self.table.item(row, 0).text()
        lot_path = os.path.join(self.lots_dir, lot_name)
        if os.path.exists(lot_path):
            viewer = LotViewer(lot_path)
            self.open_viewers.append(viewer)  # 🔹 garder référence
            viewer.show()
            viewer.raise_()
            viewer.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsSummary()
    window.show()
    sys.exit(app.exec())
