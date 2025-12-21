from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class FormIntercalaire(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Formulaire : Création intercalaire")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
