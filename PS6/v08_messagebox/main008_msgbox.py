import sys
from PySide6.QtWidgets import QApplication, QMessageBox

def button_clicked_hard(self):
    message = QMessageBox()
    message.setMinimumSize(700, 200)
    message.setWindowTitle("message title")
    message.setText("Something happened")
    message.setInformativeText("Do you want to do something about it?")
    message.setIcon(QMessageBox.critical)
    message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    message.setDefaultButton(QMessageBox.ok)

    ret = message.exec()

    if ret == QMessageBox.Ok:
        print("User chose OK")
    else:
        print("User chose Cancel")


def button_clicked_critical(self):
    ret = QMessageBox.critical(self, "Message title", "Critical message" , QMessageBox.Ok | QMessageBox.Cancel)

    if ret == QMessageBox.Ok:
        print("User chose OK")
    else:
        print("User chose Cancel")