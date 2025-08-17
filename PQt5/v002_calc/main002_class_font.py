from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout,QVBoxLayout,QPushButton,QLineEdit,QGridLayout
from PySide6.QtGui import QFont

class CalcApp(QWidget):

    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("Calculator")
        self.resize(250, 300) 

        self.text_box = QLineEdit()
        self.text_box.setFont(QFont("helvetica", 32))

        self.grid = QGridLayout()

        self.buttons = [
            "7","8","9","/",
            "4","5","6","*",
            "1","2","3","-",
            "0",".","=","+"
        ]

        row = 0
        col = 0

        for text in self.buttons:
            button = QPushButton(text)
            button.clicked.connect(lambda checked, t=text: self.button_click(t))
            button.setStyleSheet("QPushbutton { font: 25pt Comic Sans MS; padding: 10px;}")
            button.setFont(QFont("helvetica", 20))
            self.grid.addWidget(button, row, col)
            col += 1

            if col > 3 :
                col = 0
                row += 1 

        self.clear = QPushButton("Clear")
        self.delete = QPushButton("Del")

        # self.clear.setStyleSheet("QPushbutton { font: 25pt Comic Sans MS; padding: 10px;}")
        # self.delete.setStyleSheet("QPushbutton { font: 25pt Comic Sans MS; padding: 10px;}")
        self.delete.setFont(QFont("helvetica", 20))
        self.clear.setFont(QFont("helvetica", 20))

        button_row = QHBoxLayout()
        button_row.addWidget(self.clear)
        button_row.addWidget(self.delete)

        self.clear.clicked.connect(lambda _, t="Clear": self.button_click(t))
        self.delete.clicked.connect(lambda _, t="Del": self.button_click(t))

        master_layout = QVBoxLayout()
        master_layout.addWidget(self.text_box)
        master_layout.addLayout(self.grid)
        master_layout.addLayout(button_row)
        master_layout.setContentsMargins(25,25,25,25)

        self.setLayout(master_layout)


    def button_click(self,text:str):
        print(text)

        if text == "=":
            symbol = self.text_box.text()

            try:
                res = eval(symbol)
                self.text_box.setText(str(res))

            except Exception as e:
                print("error:", e)

        elif text == "Clear":
            self.text_box.clear()

        elif text == "Del":
            current_value = self.text_box.text()
            self.text_box.setText(current_value[:-1])

        else:
            current_value = self.text_box.text()
            self.text_box.setText(current_value + text)
            

if __name__ in "__main__":
    app = QApplication([])
    main_windows = CalcApp()
    main_windows.setStyleSheet("QWidget { background-color: #337 }")
    main_windows.show()
    app.exec()