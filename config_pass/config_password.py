from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTabWidget,
    QLabel, QInputDialog,QLineEdit
)
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Onglet protégé par mot de passe")

        layout = QVBoxLayout(self)

        # Création du widget d'onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(QLabel("Contenu onglet 1"), "Accueil")
        self.tabs.addTab(QLabel("Contenu onglet 2"), "Infos")

        # Onglet configuration (non ajouté au début)
        self.config_tab = QLabel("Paramètres sensibles")
        self.password = "1234"  # ⚠️ à remplacer par une vérif sécurisée

        # Bouton pour afficher l’onglet protégé
        btn_show_config = QPushButton("Afficher configuration")
        btn_show_config.clicked.connect(self.request_password)

        layout.addWidget(self.tabs)
        layout.addWidget(btn_show_config)

    def request_password(self):
        pwd, ok = QInputDialog.getText(
            self, "Mot de passe", "Entrez le mot de passe :",
            echo=QLineEdit.Password
        )
        if ok and pwd == self.password:
            # Ajouter l’onglet s’il n’est pas déjà visible
            if self.tabs.indexOf(self.config_tab) == -1:
                self.tabs.addTab(self.config_tab, "Configuration")
            self.tabs.setCurrentWidget(self.config_tab)
        else:
            print("Mot de passe incorrect ou annulé.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
