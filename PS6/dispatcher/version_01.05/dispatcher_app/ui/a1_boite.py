from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel,QLineEdit,QComboBox
)
from PySide6.QtCore import Qt

# Import des fenêtres secondaires
from ui.a4_dispatcher import LotsSummary
# (A1, A2, A3 seront ajoutées plus tard)

class Boite(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__()
        self.parent_window = parent
        self.config = config
        print(self.config["lots_path"]) # type: ignore
        self.setWindowTitle("Intercalaire Boite")
        self.setFixedSize(420, 320)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 30, 40, 30)

        # ===== Bloc 1 : Boite Archive =====
        bloc_boite = QVBoxLayout()
        bloc_boite.setSpacing(2)

        label_boite = QLabel("N° Boite Archive")
        label_boite.setAlignment(Qt.AlignCenter)
        label_boite.setStyleSheet("font-weight: bold;font-size: 12px;color: #003366;")

        self.Boite_Archive = QLineEdit()
        self.Boite_Archive.setAlignment(Qt.AlignCenter)
        self.Boite_Archive.setStyleSheet("font-weight: bold;font-size: 12px;")

        bloc_boite.addWidget(label_boite)
        bloc_boite.addWidget(self.Boite_Archive)


         # ===== Bloc 2 : Service =====
        bloc_service = QVBoxLayout()
        bloc_service.setSpacing(2)

        label_service = QLabel("Service")
        label_service.setAlignment(Qt.AlignCenter)
        label_service.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.nom_service = QComboBox()
        self.nom_service.addItems([
            "Informatique",
            "Ressources Humaines",
            "Comptabilité",
            "Direction"
        ])

        bloc_service.addWidget(label_service)
        bloc_service.addWidget(self.nom_service)

        # ===== Bloc 3 : Imprimante =====
        bloc_printer = QVBoxLayout()
        bloc_printer.setSpacing(2)

        label_printer = QLabel("Imprimante")
        label_printer.setAlignment(Qt.AlignCenter)
        label_printer.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.nom_printer = QComboBox()
        self.nom_printer.addItems([
            "HP_Laser_01",
            "Canon_Office",
            "Epson_Stock"
        ])

        bloc_printer.addWidget(label_printer)
        bloc_printer.addWidget(self.nom_printer)

        # ===== Ajout des blocs au layout principal =====
        layout.addLayout(bloc_boite)
        layout.addLayout(bloc_service)
        layout.addLayout(bloc_printer)

        layout.addStretch()  # ancre tout en haut

                
        # Boutons
        self.btn_b1 = QPushButton("Impression intercalaire BOITE")
       
        # buttons = [self.btn_b1, self.btn_b2]
        buttons = [self.btn_b1]

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
        self.btn_b1.clicked.connect(self.open_b1)


    # -------------------------------------------------
    # Si changement de valeur de service
    # -------------------------------------------------
        self.nom_service.currentTextChanged.connect(self.on_service_change)

    def on_service_change(self, valeur):
        print("Service sélectionné :", valeur)


    # -------------------------------------------------
    # Si changement de valeur de printer
    # -------------------------------------------------
        self.nom_printer.currentTextChanged.connect(self.on_printer_change)

    def on_printer_change(self, valeur):
        print("Imprimante sélectionné :", valeur)


    # -------------------------------------------------
    # OUVERTURE DES FENÊTRES
    # -------------------------------------------------
    def open_b1(self):
        pass

    # --------------------------------------------------------------------
    # RETOUR A LA FENETRE PRINCIPALE DE DEMARRAGE
    # --------------------------------------------------------------------
    def closeEvent(self,event):
        if self.parent_window is not None:
            self.parent_window.show()
        event.accept()


