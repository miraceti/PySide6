from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem
)
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface PySide6 avec tableau")
        self.setFixedSize(500, 400)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout vertical principal
        layout = QVBoxLayout(central_widget)

        # Champ de texte
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Entrez votre nom")
        layout.addWidget(self.entry)

        # Liste déroulante
        self.combo = QComboBox()
        self.combo.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(self.combo)

        # Bouton
        button = QPushButton("Valider")
        button.clicked.connect(self.ajouter_ligne)
        layout.addWidget(button)

        # Tableau
        self.table = QTableWidget(0, 3)  # 0 lignes, 3 colonnes
        self.table.setHorizontalHeaderLabels(["Nom", "Choix", "Statut"])
        layout.addWidget(self.table)

    def ajouter_ligne(self):
        nom = self.entry.text()
        choix = self.combo.currentText()
        statut = "Enregistré"

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(nom))
        self.table.setItem(row, 1, QTableWidgetItem(choix))
        self.table.setItem(row, 2, QTableWidgetItem(statut))

        self.entry.clear()

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
