from PySide6.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QTextEdit example")

        self.text_edit = QTextEdit()
        #self.text_edit.textChanged.connect(self.text_changed)

        current_text_button = QPushButton('Current text')
        current_text_button.clicked.connect(self.current_text_button_clicked)

        copy_button = QPushButton("Copier")
        copy_button.clicked.connect(self.text_edit.copy)

        cut_button = QPushButton("Couper")
        cut_button.clicked.connect(self.text_edit.cut)

        paste_button = QPushButton("Coller")
        paste_button.clicked.connect(self.text_edit.paste)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.text_edit.undo)
        
        redo_button = QPushButton("Redo")
        redo_button.clicked.connect(self.text_edit.redo)
        
        set_plain_text_button = QPushButton("Set Plain text")
        set_plain_text_button.clicked.connect(self.set_plain_text)
        
        set_HTML_button = QPushButton("Set HTML")
        set_HTML_button.clicked.connect(self.set_html)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.text_edit.clear)


        #layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(current_text_button)
        h_layout.addWidget(copy_button)
        h_layout.addWidget(cut_button)
        h_layout.addWidget(paste_button)
        h_layout.addWidget(undo_button)
        h_layout.addWidget(redo_button)
        h_layout.addWidget(set_plain_text_button)
        h_layout.addWidget(set_HTML_button)
        h_layout.addWidget(clear_button)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.text_edit)
        
        self.setLayout(v_layout)


    def paste(self):
        self.text_edit.paste()
    #     print(" le texte à changé en ", self.text_edit.text())
        
    def current_text_button_clicked(self):
        print(self.text_edit.toPlainText())

    def set_plain_text(self):
        self.text_edit.setPlainText(" ceci est un exemple de testeur amis sans limite de ligne et etc...")

    def set_html(self):
        self.text_edit.setHtml("<h1>King of los alamos</h1><p> ville de New-york !</p> <ul> <li> GAS </li> <li>NEW NEW</li></ul></p>")





 



    