from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface PySide6 avec Dark/Light Mode")
        self.setFixedSize(600, 450)

        # Suivi du thème actuel
        self.dark_mode = False

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Champ de texte
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Entrez votre nom")
        layout.addWidget(self.entry)

        # Liste déroulante
        self.combo = QComboBox()
        self.combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(self.combo)

        # Ligne de boutons
        button_layout = QHBoxLayout()

        # Bouton d'ajout
        self.btn_valider = QPushButton("Valider")
        self.btn_valider.clicked.connect(self.ajouter_ligne)
        button_layout.addWidget(self.btn_valider)

        # Bouton dark/light mode
        self.btn_theme = QPushButton("🌙 Activer le mode sombre")
        self.btn_theme.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.btn_theme)

        layout.addLayout(button_layout)

        # Tableau
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom", "Choix", "Statut"])
        layout.addWidget(self.table)

        # Appliquer thème initial (clair)
        self.set_light_mode()

    def ajouter_ligne(self):
        nom = self.entry.text()
        choix = self.combo.currentText()
        statut = "Ajouté"

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(nom))
        self.table.setItem(row, 1, QTableWidgetItem(choix))
        self.table.setItem(row, 2, QTableWidgetItem(statut))

        self.entry.clear()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.set_dark_mode()
            self.btn_theme.setText("☀️ Activer le mode clair")
        else:
            self.set_light_mode()
            self.btn_theme.setText("🌙 Activer le mode sombre")

    def set_dark_mode(self):
        dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-size: 14px;
        }
        QLineEdit, QComboBox, QTableWidget {
            background-color: #3c3f41;
            color: #ffffff;
            border: 1px solid #5c5c5c;
        }
        QPushButton {
            background-color: #444;
            border: 1px solid #666;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #555;
        }
        QHeaderView::section {
            background-color: #3c3f41;
            color: white;
            font-weight: bold;
        }
        """
        self.setStyleSheet(dark_style)

    def set_light_mode(self):
        light_style = """
        QWidget {
            background-color: #f0f0f0;
            color: #000000;
            font-size: 14px;
        }
        QLineEdit, QComboBox, QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
        }
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #aaa;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QHeaderView::section {
            background-color: #dcdcdc;
            color: black;
            font-weight: bold;
        }
        """
        self.setStyleSheet(light_style)

# Lancement
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
