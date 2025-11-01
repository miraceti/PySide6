import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class LotsExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Explorateur de Lots")
        self.resize(1200, 700)

        main_layout = QHBoxLayout(self)

        # Partie gauche = tableau
        left_layout = QVBoxLayout()
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        left_layout.addWidget(self.btn_select_dir)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Fichier", "Type XML", "Numaxa", "Service", "Pôle",
            "Complexe", "Gestionnaire", "Titre objet", "État", "Rotation"
        ])
        self.table.cellClicked.connect(self.show_image_preview)
        left_layout.addWidget(self.table)

        # Partie droite = aperçu image
        self.preview_label = QLabel("Aperçu de l'image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.preview_label, 2)

        self.current_lots_dir = None

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.current_lots_dir = directory
            self.load_lots(directory)

    def load_lots(self, lots_dir):
        self.table.setRowCount(0)  # reset tableau

        # Parcourir sous-dossiers
        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)
            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:
                files = os.listdir(subpath)
                for file in sorted(files):
                    if file.endswith(".xml"):
                        xml_path = os.path.join(subpath, file)
                        jpg_path = os.path.splitext(xml_path)[0] + ".jpg"
                        row_data = self.parse_xml(xml_path)
                        row_data["Fichier"] = jpg_path

                        # Ajouter au tableau
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        for col, key in enumerate([
                            "Fichier", "Type", "Numaxa", "Service", "Pôle",
                            "Complexe", "Gestionnaire", "Titreobjet", "Etat", "Rotation"
                        ]):
                            item = QTableWidgetItem(row_data.get(key, ""))
                            self.table.setItem(row, col, item)

    def parse_xml(self, xml_path):
        """Extrait les champs utiles du XML"""
        data = {}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            data["Rotation"] = root.findtext("rotation", "")
            data["Etat"] = root.findtext("etat", "")
            data["Type"] = root.findtext("type", "")

            meta = root.find("meta")
            if meta is not None:
                data["Numaxa"] = meta.findtext("numaxa", "")
                data["Service"] = meta.findtext("service", "")
                data["Pôle"] = meta.findtext("pole", "")
                data["Complexe"] = meta.findtext("complexe", "")
                data["Gestionnaire"] = meta.findtext("gestionnaire", "")
                data["Titreobjet"] = meta.findtext("titreobjet", "")
        except Exception as e:
            print(f"Erreur XML {xml_path}: {e}")

        return data

    def show_image_preview(self, row, column):
        """Affiche l'image quand on clique sur une ligne du tableau"""
        item = self.table.item(row, 0)  # colonne fichier
        if item:
            img_path = item.text()
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    self.preview_label.setPixmap(pixmap.scaled(
                        self.preview_label.width(),
                        self.preview_label.height(),
                        Qt.KeepAspectRatio
                    ))
            else:
                self.preview_label.setText("Image introuvable")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsExplorer()
    window.show()
    sys.exit(app.exec())
