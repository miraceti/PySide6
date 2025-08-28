from PySide6.QtWidgets import QApplication
import sys
from database import Widget


app = QApplication(sys.argv)

Widget = Widget()
Widget.show()

app.exec()