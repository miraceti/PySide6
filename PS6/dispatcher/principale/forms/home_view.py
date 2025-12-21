from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class HomeView(QWidget):
    def __init__(self):
        super().__init__()

        title = QLabel("Application GED")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        subtitle = QLabel(
            "Sélectionnez une action dans le menu\n"
            "pour commencer le traitement"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #666;")

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setLayout(layout)
