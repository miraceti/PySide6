from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

import sys
app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("My first main app")

button = QPushButton()
button.setText("Press me!")

window.setCentralWidget(button)

window.show()
app.exec()