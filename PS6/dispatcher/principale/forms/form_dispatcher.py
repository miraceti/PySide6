from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFileDialog
)


class FormDispatcher(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Aucun dossier chargé")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def ask_and_open_lot_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner un dossier de lots"
        )
        if not folder:
            raise Exception("Aucun dossier sélectionné")

        self.label.setText(f"Dossier chargé :\n{folder}")

        # ICI tu appelleras ton dispatcher existant
        # dispatcher.process(folder)
