from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QMessageBox,
    QMenuBar, QMenu,  QLabel, QHBoxLayout
)
from PySide6.QtGui import QAction
import sys

class FenetreSecondaire(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenêtre secondaire")
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        label = QLabel("Ceci est une fenêtre secondaire.")
        layout.addWidget(label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application PySide6 complète")
        self.setFixedSize(650, 500)
        self.dark_mode = False

        self.init_menu()

        # Onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_accueil = QWidget()
        self.tab_tableau = QWidget()
        self.tabs.addTab(self.tab_accueil, "Accueil")
        self.tabs.addTab(self.tab_tableau, "Tableau")

        self.init_accueil()
        self.init_tableau()
        self.set_light_mode()

    def init_menu(self):
        menubar = QMenuBar()
        self.setMenuBar(menubar)

        menu_fichier = QMenu("Fichier", self)
        menubar.addMenu(menu_fichier)
        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)

        menu_aide = QMenu("Aide", self)
        menubar.addMenu(menu_aide)
        action_info = QAction("À propos", self)
        action_info.triggered.connect(self.show_about)
        menu_aide.addAction(action_info)

    def init_accueil(self):
        layout = QVBoxLayout()
        self.tab_accueil.setLayout(layout)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Entrez votre nom")
        layout.addWidget(self.entry)

        self.combo = QComboBox()
        self.combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(self.combo)

        button_row = QHBoxLayout()

        btn_valider = QPushButton("Valider")
        btn_valider.clicked.connect(self.ajouter_ligne)
        button_row.addWidget(btn_valider)

        self.btn_theme = QPushButton("🌙 Mode sombre")
        self.btn_theme.clicked.connect(self.toggle_theme)
        button_row.addWidget(self.btn_theme)

        btn_popup = QPushButton("Fenêtre secondaire")
        btn_popup.clicked.connect(self.open_secondary)
        button_row.addWidget(btn_popup)

        layout.addLayout(button_row)

    def init_tableau(self):
        layout = QVBoxLayout()
        self.tab_tableau.setLayout(layout)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom", "Choix", "Statut"])
        layout.addWidget(self.table)

    def ajouter_ligne(self):
        nom = self.entry.text()
        choix = self.combo.currentText()
        statut = "Ajouté"

        if nom.strip() == "":
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(nom))
        self.table.setItem(row, 1, QTableWidgetItem(choix))
        self.table.setItem(row, 2, QTableWidgetItem(statut))

        self.entry.clear()

    def open_secondary(self):
        self.popup = FenetreSecondaire()
        self.popup.show()

    def show_about(self):
        QMessageBox.information(self, "À propos", "Cette application a été créée avec PySide6.")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.set_dark_mode()
            self.btn_theme.setText("☀️ Mode clair")
        else:
            self.set_light_mode()
            self.btn_theme.setText("🌙 Mode sombre")

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
