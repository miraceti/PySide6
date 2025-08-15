from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QLabel Image")

        image_label = QLabel()
        #image_label.setPixmap(QPixmap("/media/rico/SATURNE/rico/python/PySide6/PS6/v12_label_image/images/imagesatellite1.png"))
        image_label.setPixmap(QPixmap("/media/rico/SATURNE/rico/python/PySide6/PS6/v12_label_image/images/Pic.png"))


        v_layout = QVBoxLayout()
        v_layout.addWidget(image_label)

        self.setLayout(v_layout)
