from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout,QVBoxLayout,QPushButton,QLabel

from random import choice

app = QApplication([])
main_windows = QWidget()
main_windows.setWindowTitle("random word maker")
main_windows.resize(300, 200)


title = QLabel("Random Keywords")

text1 = QLabel("?")
text2 = QLabel("?")
text3 = QLabel("?")

button1 = QPushButton("Click me")
button2 = QPushButton("Click me")
button3 = QPushButton("Click me")

my_words = ['hello','goodbye','test','app','python','pyqt','pyside','vietnam','asia']


master_layout = QVBoxLayout()

row1_layout = QHBoxLayout()
row2_layout = QHBoxLayout()
row3_layout = QHBoxLayout() 

row1_layout.addWidget(title, alignment=Qt.AlignCenter)
row2_layout.addWidget(text1, alignment=Qt.AlignCenter)
row2_layout.addWidget(text2, alignment=Qt.AlignCenter)
row2_layout.addWidget(text3, alignment=Qt.AlignCenter)
row3_layout.addWidget(button1)
row3_layout.addWidget(button2)
row3_layout.addWidget(button3)

master_layout.addLayout(row1_layout)
master_layout.addLayout(row2_layout)
master_layout.addLayout(row3_layout)

main_windows.setLayout(master_layout)


def random_word1():
    word = choice(my_words)
    text1.setText(word)

def random_word2():
    word = choice(my_words)
    text2.setText(word)
    

def random_word3():
    word = choice(my_words)
    text3.setText(word)

button1.clicked.connect(random_word1)
button2.clicked.connect(random_word2)
button3.clicked.connect(random_word3)

main_windows.show()
app.exec()