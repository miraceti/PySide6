import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDial,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QSpinBox,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        combobox = QComboBox()
        combobox.addItems(["One", "Two", "Three"])

        # The default signal from currentIndexChanged sends the index
        combobox.currentIndexChanged.connect(self.index_changed)

        # The same signal can send a text string
        combobox.currentTextChanged.connect(self.text_changed)

        self.setCentralWidget(combobox)

    def index_changed(self, index):  # index is an int starting from 0
        print(index)

    def text_changed(self, text):  # text is a str
        print(text)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()