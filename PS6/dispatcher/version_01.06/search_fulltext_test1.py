import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt


class FullTextSearchDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recherche Full-Text")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # 🔹 Label résultats
        self.result_label = QLabel("Résultats :")
        layout.addWidget(self.result_label)

        # 🔹 Liste des résultats
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.on_item_selected)
        layout.addWidget(self.result_list)

        # 🔹 Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Saisir les premiers caractères...")
        self.search_input.textChanged.connect(self.search_text)
        layout.addWidget(self.search_input)

        # 🔹 Source de données (simule fichier / table)
        self.data_source = [
            "Complexe automobile AXA",
            "Gestionnaire sinistre flotte",
            "Pole indemnisation",
            "Traitement sinistre automobile",
            "Complexe habitation",
            "Gestionnaire assurance vie",
            "Pole automobile",
            "Dossier sinistre flotte AXA",
            "Recherche documentaire",
            "Indexation pli sinistre",
            "Gestionnaire AXA Marseille",
            "Complexe entreprise"
        ]

    def search_text(self, text):
        self.result_list.clear()

        if not text.strip():
            return

        text = text.lower()

        # 🔹 Filtrage + tri alphabétique
        results = sorted(
            [item for item in self.data_source if text in item.lower()]
        )

        # 🔹 Limite à 10 résultats
        for result in results[:10]:
            self.result_list.addItem(QListWidgetItem(result))

    def on_item_selected(self, item):
        # 🎯 Action future ici
        print(f"✔ Sélectionné : {item.text()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullTextSearchDemo()
    window.show()
    sys.exit(app.exec())
