from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt

# Import des fenêtres secondaires
from ui.a4_dispatcher import LotsSummary
from ui.a1_boite import Boite
from ui.a2_pli import Pli
# ( A2, A3 seront ajoutées plus tard)


class Accueil(QWidget):
    def __init__(self,config):
        super().__init__()
        self.config = config
        self.setWindowTitle("DISPATCHER - Accueil")
        self.setFixedSize(420, 320)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)

        # Titre
        titre = QLabel("DISPATCHER")
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #003366;
            }
        """)
        layout.addWidget(titre)

        # Sous-titre
        sous_titre = QLabel("Choisissez une action")
        sous_titre.setAlignment(Qt.AlignCenter)
        sous_titre.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(sous_titre)

        # Boutons
        self.btn_a1 = QPushButton("1 - Création intercalaire BOITE")
        self.btn_a2 = QPushButton("2 - Création intercalaire PLI")
        self.btn_a3 = QPushButton("3 - Scan to Dispatcher")
        self.btn_a4 = QPushButton("4 - Dispatcher")

        buttons = [self.btn_a1, self.btn_a2, self.btn_a3, self.btn_a4]

        for btn in buttons:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E8EEF7;
                    border: 1px solid #AAB4C8;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #596FAB;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #3D4F8A;
                    color: white;
                }
            """)
            layout.addWidget(btn)

        self.setLayout(layout)

        # Connexions
        self.btn_a1.clicked.connect(self.open_a1)
        self.btn_a2.clicked.connect(self.open_a2)
        self.btn_a3.clicked.connect(self.open_a3)
        self.btn_a4.clicked.connect(self.open_a4)

    # -------------------------------------------------
    # OUVERTURE DES FENÊTRES
    # -------------------------------------------------

    def open_a1(self):
        self.hide()
        self.fenetre = Boite(parent=self,config=self.config)
        self.fenetre.show()

    def open_a2(self):
        self.hide()
        self.fenetre = Pli(parent=self,config=self.config)
        self.fenetre.show()

    def open_a3(self):
        self.hide()
        # À remplacer plus tard par la vraie fenêtre A3
        self.fenetre = PlaceholderWindow(
            "Scan to Dispatcher", self
        )
        self.fenetre.show()

    def open_a4(self):
        self.hide()
        self.fenetre = LotsSummary(parent=self,config=self.config)
        self.fenetre.show()

    def reload_config(self):
        return self.load_config()
# -------------------------------------------------
# FENÊTRE TEMPORAIRE (A1 / A2 / A3)
# -------------------------------------------------

class PlaceholderWindow(QWidget):
    """Fenêtre temporaire pour A1, A2, A3"""

    def __init__(self, title, parent=None):
        super().__init__()
        self.parent_window = parent
        self.setWindowTitle(title)
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        info = QLabel("Fenêtre en cours de développement")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        self.setLayout(layout)

    def closeEvent(self, event):
        if self.parent_window:
            self.parent_window.show()
        event.accept()
