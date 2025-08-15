from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QWidget, QVBoxLayout, QMenuBar, QMenu
)
from PySide6.QtGui import QAction
import sys

# Fenêtre secondaire
class SecondWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fenêtre secondaire")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ceci est une autre fenêtre."))
        self.setLayout(layout)

# Fenêtre principale
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Multi-fenêtres")

        # Barre de menus
        menubar = self.menuBar()
        fichier_menu = menubar.addMenu("Fichier")
        quitter_action = QAction("Quitter", self)
        quitter_action.triggered.connect(self.close)
        fichier_menu.addAction(quitter_action)

        aide_menu = menubar.addMenu("Aide")
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        aide_menu.addAction(about_action)

        # Corps principal
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel("Bienvenue dans l'application.")
        layout.addWidget(self.label)

        self.btn_ouvrir = QPushButton("Ouvrir une autre fenêtre")
        self.btn_ouvrir.clicked.connect(self.open_new_window)
        layout.addWidget(self.btn_ouvrir)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.second_window = None

    def open_new_window(self):
        self.second_window = SecondWindow()
        self.second_window.show()

    def show_about(self):
        self.label.setText("Application multi-fenêtres avec PySide6.")

# Lancement
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
