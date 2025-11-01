import os
import sys
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem
)


class LotsSummary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Résumé des Lots")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # Bouton sélection dossier
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        layout.addWidget(self.btn_select_dir)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Lot (dossier)", "Nb JPG", "Nb XML Type 1", "Nb XML Type 2", "Nb XML Type 3", "Nb XML Type 4"
        ])
        layout.addWidget(self.table)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.load_summary(directory)

    def load_summary(self, lots_dir):
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

                # Ajouter une ligne dans le tableau
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(subdir))
                self.table.setItem(row, 1, QTableWidgetItem(str(jpg_count)))
                self.table.setItem(row, 2, QTableWidgetItem(str(xml_counts[1])))
                self.table.setItem(row, 3, QTableWidgetItem(str(xml_counts[2])))
                self.table.setItem(row, 4, QTableWidgetItem(str(xml_counts[3])))
                self.table.setItem(row, 5, QTableWidgetItem(str(xml_counts[4])))

    def get_xml_type(self, filepath):
        """Retourne la valeur du champ <type> dans un fichier XML"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            return int(root.findtext("type", "0"))
        except Exception:
            return 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotsSummary()
    window.show()
    sys.exit(app.exec())
