from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSlider

def respond_to_slider(data):
    print("slide move to : ", data)

app = QApplication()
slider = QSlider(Qt.Orientation.Horizontal)
slider.setMinimum(1)
slider.setMaximum(100)
slider.setValue(25)

slider.valueChanged.connect(respond_to_slider)
slider.show()
app.exec()