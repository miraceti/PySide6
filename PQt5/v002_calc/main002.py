from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout,QVBoxLayout,QPushButton,QLabel

from random import choice

app = QApplication([])
main_windows = QWidget()
main_windows.setWindowTitle("random word maker")
main_windows.resize(300, 200)


title = QLabel("Random Keywords")