from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLineEdit, QGridLayout
)

app = QApplication([])
main_windows = QWidget()
main_windows.setWindowTitle("Calculator")
main_windows.resize(250, 300)

text_box = QLineEdit()
grid = QGridLayout()

# Liste des boutons de la grille
buttons = [
    "7", "8", "9", "/",
    "4", "5", "6", "*",
    "1", "2", "3", "-",
    "0", ".", "=", "+"
]

clear = QPushButton("Clear")
delete = QPushButton("Del")


def button_click(text: str):
    """Gestion des clics sur tous les boutons."""
    if text == "=":
        symbol = text_box.text()
        try:
            res = eval(symbol)   # ⚠️ attention à eval en vrai projet
            text_box.setText(str(res))
        except Exception as e:
            print("error:", e)

    elif text == "Clear":
        text_box.clear()

    elif text == "Del":
        current_value = text_box.text()
        text_box.setText(current_value[:-1])

    else:
        current_value = text_box.text()
        text_box.setText(current_value + text)


# Création des boutons numériques et opérateurs
row, col = 0, 0
for text in buttons:
    button = QPushButton(text)
    button.clicked.connect(lambda _, t=text: button_click(t))
    grid.addWidget(button, row, col)
    col += 1
    if col > 3:
        col = 0
        row += 1

# Ligne du bas : Clear et Del
button_row = QHBoxLayout()
button_row.addWidget(clear)
button_row.addWidget(delete)

clear.clicked.connect(lambda _, t="Clear": button_click(t))
delete.clicked.connect(lambda _, t="Del": button_click(t))

# Disposition principale
master_layout = QVBoxLayout()
master_layout.addWidget(text_box)
master_layout.addLayout(grid)
master_layout.addLayout(button_row)
main_windows.setLayout(master_layout)

main_windows.show()
app.exec()
