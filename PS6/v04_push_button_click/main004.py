from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

def button_clicked():
    print("you click ?")

app = QApplication()


button = QPushButton("Press me!")

button.clicked.connect(button_clicked)

button.show()
app.exec()