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

        listwidget = QListWidget()
        listwidget.addItems(["One", "Two", "Three","A","B","C","D","E","F","G","H"])

        # In QListWidget there are two separate signals for the item, and the str
        listwidget.currentItemChanged.connect(self.index_changed)
        listwidget.currentTextChanged.connect(self.text_changed)

        self.setCentralWidget(listwidget)

    def index_changed(self, index):  # Not an index, index is a QListWidgetItem
        print(index.text())

    def text_changed(self, text):  # text is a str
        print(text)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()