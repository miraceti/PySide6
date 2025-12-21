from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class FormScan(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Formulaire : Scan vers lots")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
