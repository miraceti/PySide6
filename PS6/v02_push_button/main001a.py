
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys

class ButtonHolder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Holder app")
        button = QPushButton("Press me!")
        self.setCentralWidget(button)

app = QApplication(sys.argv)

window = ButtonHolder()

window.show()
app.exec()