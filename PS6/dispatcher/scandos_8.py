import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QTextEdit
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize


class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path):
        super().__init__()
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1200, 800)

        main_layout = QHBoxLayout(self)

        # Liste des images en vignettes
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        main_layout.addWidget(self.list_widget, 2)

        # Partie droite = aperçu + infos
        right_layout = QVBoxLayout()

        # Zone d’aperçu image
        self.preview_label = QLabel("Sélectionnez une image")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        right_layout.addWidget(self.preview_label, 3)

        # Zone infos XML
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        right_layout.addWidget(self.info_text, 1)

        main_layout.addLayout(right_layout, 4)

        self.lot_path = lot_path
        self.load_images()

    def load_images(self):
        """Charge toutes les images .jpg du lot"""
        for file in sorted(os.listdir(self.lot_path)):
            if file.lower().endswith(".jpg"):
                img_path = os.path.join(self.lot_path, file)
                xml_path = os.path.splitext(img_path)[0] + ".xml"

                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                    item = QListWidgetItem(icon, file)
                    item.setData(Qt.UserRole, (img_path, xml_path))
                    self.list_widget.addItem(item)

    def show_image_and_info(self, item):
        """Affiche en grand l’image cliquée + ses infos XML"""
        img_path, xml_path = item.data(Qt.UserRole)

        # Affichage image
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

        # Affichage infos XML
        if os.path.exists(xml_path):
            infos = self.parse_xml(xml_path)
            text = "\n".join(f"{k} : {v}" for k, v in infos.items() if v)
            print('infos : ', infos, ' -- text : ', text)

            if not text:
                text = "(Pas d'infos XML)"
            self.info_text.setText(text)
        else:
            self.info_text.setText("(Pas de fichier XML associé)")

    def parse_xml(self, xml_path):
        """Retourne les champs utiles du XML sous forme de dict"""
        data = {}
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
        except Exception as e:
            data["Erreur XML"] = str(e)

        return data


class LotsSummary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résumé des Lots")
        self.resize(1100, 600)

        layout = QVBoxLayout(self)

        self.open_viewers = []  # garder références fenêtres secondaires
        self.lots_dir = None

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

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.lots_dir = directory
            self.load_summary(directory)

    def load_summary(self, lots_dir):
        self.table.setRowCount(0)
        file_list=[]
        pdfnum=0
        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)
            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:
                jpg_count = 0
                xml_counts = {1: 0, 2: 0, 3: 0, 4: 0}
                
                if subpath[-5:] == '63906':
                    jpg_countj = 0
                    for file in os.listdir(subpath):
                        filepath = os.path.join(subpath, file)

                        if file.lower().endswith(".jpg"):
                            jpg_countj += 1
                    print("nombre de fichier JPG : ", jpg_countj )


                for file in os.listdir(subpath):
                    filepath = os.path.join(subpath, file)

                    if file.lower().endswith(".jpg"):
                        jpg_count += 1
                    elif file.lower().endswith(".xml"):
                        xml_type = self.get_xml_type(filepath)
                        if xml_type in xml_counts:
                            xml_counts[xml_type] += 1

                        if subpath[-5:] == '63906':
                            
                            if xml_type == 1:
                                print("new lot : ", subpath[-6:])
                                file_list = []
                                pdfnum=0

                            if (xml_type == 2 and jpg_count > 2) or jpg_count==jpg_countj:
                                pdfnum+=1
                                print("\ncompteur ficjier jpg : ",jpg_count," sur ",jpg_countj)
                                if jpg_countj==jpg_count:
                                    file_list.append(file)
                                    print("new pli donc new pdf :",  subpath[-6:], pdfnum)
                                    print(file_list)
                                else:
                                    print("new pli donc new pdf :",  subpath[-6:], pdfnum)
                                    print(file_list)
                                    file_list=[]
                                
                            
                            if xml_type == 3 or xml_type == 4:
                                file_list.append(file)
                                
                        


                nb_plis = xml_counts[2]                 # nb de PDF à créer
                nb_pages_total = xml_counts[3] + xml_counts[4]

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
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except Exception:
            return 0

    def open_lot_viewer(self, row, column):
        if not self.lots_dir:
            return
        lot_name = self.table.item(row, 0).text()
        lot_path = os.path.join(self.lots_dir, lot_name)
        if os.path.exists(lot_path):
            viewer = LotViewer(lot_path)
            self.open_viewers.append(viewer)  # garder référence
            viewer.show()
            viewer.raise_()
            viewer.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsSummary()
    window.show()
    sys.exit(app.exec())
