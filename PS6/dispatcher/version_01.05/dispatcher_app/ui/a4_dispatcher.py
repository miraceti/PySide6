import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from PySide6.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
                               QLabel,  QTextEdit, QGraphicsView, QGraphicsScene,QFrame,    QToolBar,QLineEdit,   QSizePolicy ,
                               QCheckBox ,QMenu
                               )
from PySide6.QtGui import QPixmap, QIcon, QTransform,QFont, QColor, QAction
from PySide6.QtCore import Qt, QSize, QTimer

import configparser
from config.loader import load_config


class LotViewer(QWidget):
    """Fenêtre secondaire pour afficher un lot et ses images avec infos XML"""
    def __init__(self, lot_path, parent=None, config=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config = config
        self.setWindowTitle(f"Lot : {os.path.basename(lot_path)}")
        self.resize(1600, 1000)

        self.lot_path = lot_path
        self.image_items = []
        self.pages_lues = set()  # Ensemble des images déjà visualisées
        self.current_index = 0
        self.zoom_factor = 0.3
        self.plis = []

        # Dictionnaire pour référencer les frames de droite
        self.frames = {}
        # self.frames["indexation"]      # cadre 1
        # self.frames["recherche"]       # cadre 2
        # self.frames["resultat"]        # cadre 3

        # --- Layout principal ---
        # Layout vertical principal : image et status
        main_v_layout = QVBoxLayout(self)
        self.setLayout(main_v_layout)

        # Layout horizontal principal (vignettes + image + plis)
        self.main_layout = QHBoxLayout()
        main_v_layout.addLayout(self.main_layout, stretch=1)

        # Barre d'état en bas
        self.status_label = QLabel("En attente d'action...")
        self.status_label.setAlignment(Qt.AlignCenter) # type: ignore
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #596fab;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }
        """)
        main_v_layout.addWidget(self.status_label)

        # --- Left : vignettes ---
        self.left_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 120))
        self.list_widget.setResizeMode(QListWidget.Adjust) # type: ignore
        self.list_widget.setViewMode(QListWidget.IconMode) # pyright: ignore[reportAttributeAccessIssue]
        self.list_widget.setMovement(QListWidget.Static) # type: ignore
        self.list_widget.itemClicked.connect(self.show_image_and_info)
        self.left_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.left_layout, stretch=1)

        # --- Middle : toolbar, image, xml ---
        self.middle_layout = QVBoxLayout()
        self.setup_toolbar()
        self.setup_image_viewer()

        # Zone infos XML (limitée à 6 lignes)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(160)  # environ 6 lignes
        self.middle_layout.addWidget(self.info_text)

        self.main_layout.addLayout(self.middle_layout, stretch=2)

        # --- Right : plis + 3 frames ---
        self.right_layout = QVBoxLayout()

        # Tableau des plis
        self.pli_table = QTableWidget()
        self.pli_table.setColumnCount(5)
        self.pli_table.setHorizontalHeaderLabels(["LUES","IND","PLI","DOC","PG"])
        self.pli_table.cellClicked.connect(self.filter_vignettes_by_pli)
        self.right_layout.addWidget(self.pli_table)

        # --- Frame 1 : Indexation pli en cours ---
        frame1 = QFrame()
        frame1.setFrameShape(QFrame.StyledPanel)
        frame1.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        frame1.setMaximumHeight(150)  # 🔹 environ 6 lignes de la table
        layout1 = QVBoxLayout()
        layout1.setSpacing(3)

        # Titre du cadre
        label_title = QLabel("Indexation pli en cours")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 2px;;background-color: #596fab;color: white;")
        layout1.addWidget(label_title)

        # Grille des labels/champs
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        grid.setVerticalSpacing(2)
        grid.setHorizontalSpacing(8)

        # Champs XML (lecture seule mais modifiables par le code)
        self.champ_complexe = QLineEdit()
        self.champ_pole = QLineEdit()
        self.champ_gestionnaire = QLineEdit()
        self.champ_titre_objet = QLineEdit()

        # Champs initialement vides
        self.champ_complexe.setText("")
        self.champ_pole.setText("")
        self.champ_gestionnaire.setText("")
        self.champ_titre_objet.setText("")

        for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
            champ.setReadOnly(True)
            champ.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 🔹 Affiche le début du texte
            champ.setCursorPosition(0)        # 🔹 Positionne le curseur au début si texte trop long
            champ.setStyleSheet("""
                QLineEdit {
                    background-color: #f9f9f9;
                    color: #003366;
                    border: 1px solid #ddd;
                    padding: 2px 3px;
                    font-size: 10px;
                    font-weight: bold;            
                    text-align: left;  /* 🔹 Forçage supplémentaire côté CSS */            
                }
            """)

            bold_font = QFont()
            bold_font.setBold(True)
            for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
                champ.setFont(bold_font)


            # --- Uniformisation visuelle des 4 champs XML ---
            common_style = """
                QLineEdit {
                    background-color: #f9f9f9;
                    color: #003366;
                    border: 1px solid #ddd;
                    padding: 2px 3px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: left;
                }
            """
            bold_font = QFont()
            bold_font.setBold(True)

            for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
                champ.setStyleSheet(common_style)
                champ.setFont(bold_font)

        labels = [
            ("Complexe", self.champ_complexe),
            ("Pôle", self.champ_pole),
            ("Gestionnaire", self.champ_gestionnaire),
            ("Titre objet", self.champ_titre_objet)
        ]

        for i, (text, champ) in enumerate(labels):
            label = QLabel(f"{text} :")
            label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
            # label.setStyleSheet("font-size: 10px; font-weight: bold;background-color: #0934E0; color: white;")
            label.setStyleSheet("font-weight: bold; font-size: 12px;background-color: #596fab;color: white;")
            grid.addWidget(label, i, 0)
            grid.addWidget(champ, i, 1)

        # 🔹 Met à jour l'info-bulle quand la valeur change
        for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
            champ.textChanged.connect(lambda text, c=champ: c.setToolTip(text))

        layout1.addLayout(grid)
        frame1.setLayout(layout1)
        self.right_layout.addWidget(frame1)
        self.frames["indexation"] = frame1

        # --- Frame 2 : Recherche complexe ---
        frame2 = QFrame()
        frame2.setFrameShape(QFrame.StyledPanel)
        frame2.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout2 = QVBoxLayout()
        layout2.setSpacing(3)
        label2 = QLabel("Recherche Complexe")
        label2.setAlignment(Qt.AlignCenter)
        label2.setStyleSheet("font-weight: bold; font-size: 12px;;background-color: #596fab;color: white;")
        layout2.addWidget(label2)
        layout2.addStretch()
        frame2.setLayout(layout2)
        self.right_layout.addWidget(frame2)
        self.frames["recherche"] = frame2

        # --- Frame 3 : Résultat recherche ---
        frame3 = QFrame()
        frame3.setFrameShape(QFrame.StyledPanel)
        frame3.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout3 = QVBoxLayout()
        layout3.setSpacing(3)
        label3 = QLabel("Résultat recherche")
        label3.setAlignment(Qt.AlignCenter)
        label3.setStyleSheet("font-weight: bold; font-size: 12px;background-color: #596fab;color: white;")
        layout3.addWidget(label3)
        layout3.addStretch()
        frame3.setLayout(layout3)
        self.right_layout.addWidget(frame3)
        self.frames["resultat"] = frame3



        self.main_layout.addLayout(self.right_layout, stretch=1)

        # Bouton pour voir toutes les vignettes
        self.btn_all_vignettes = QPushButton("Voir toutes les vignettes")
        self.btn_all_vignettes.setStyleSheet('QPushButton {background-color: #EEEEEE; color: black; font:bold; font-size:12px} QPushButton:hover { background-color: #E06609; color: #49F276; }')
        self.btn_all_vignettes.clicked.connect(self.show_all_vignettes)
        self.right_layout.insertWidget(0, self.btn_all_vignettes)

        # Bouton pour valider le pli courant
        self.btn_valid_pli = QPushButton("Valider le pli")
        # self.btn_valid_pli.setStyleSheet('QPushButton {background-color: #b0daa3; color: red;}')
        self.btn_valid_pli.setStyleSheet('QPushButton {background-color: #51de26; color: black; font:bold; font-size:16px} QPushButton:hover { color: red; }')
        # self.btn_valid_pli.setStyleSheet('QPushButton:pressed {background-color: #de2644;}')

        self.btn_valid_pli.clicked.connect(self.valid_pli)
        self.right_layout.addWidget(self.btn_valid_pli)

        # Bouton pour livrer le lot courant
        self.btn_livraison_lot = QPushButton("Livraison du lot")
        # self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: #1fb0e0; color: blue; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: white; color: grey; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        self.btn_livraison_lot.setEnabled(False)
        self.btn_livraison_lot.clicked.connect(self.show_all_vignettes)
        self.right_layout.addWidget(self.btn_livraison_lot)

        # # --- Barre d’état en bas ---
        # self.status_label = QLabel("")
        # self.status_label.setAlignment(Qt.AlignCenter)
        # self.status_label.setStyleSheet("""
        #     QLabel {
        #         background-color: #596fab;
        #         color: white;
        #         font-weight: bold;
        #         font-size: 12px;
        #         padding: 4px;
        #     }
        # """)
        # self.main_layout.addWidget(self.status_label)


        # Chargement
        self.populate_pli_table()
        self.show_all_vignettes()
        self.info_text.clear()
        self.champ_complexe.clear()
        self.champ_pole.clear()
        self.champ_gestionnaire.clear()
        self.champ_titre_objet.clear()
        self.update_page_status(False)

    # --- Toolbar et image ---
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))  # 🔹 Taille uniforme des icônes

        # --- Zoom ---
        self.zoom_in_action = QAction(QIcon.fromTheme("zoom-in"), "Zoom +", self)
        self.zoom_out_action = QAction(QIcon.fromTheme("zoom-out"), "Zoom -", self)
        self.reset_zoom_action = QAction(QIcon.fromTheme("zoom-original"), "Zoom par défaut", self)

        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.reset_zoom_action.triggered.connect(self.reset_zoom)

        # --- Navigation ---
        self.prev_action = QAction(QIcon.fromTheme("go-previous"), "Précédent", self)
        self.next_action = QAction(QIcon.fromTheme("go-next"), "Suivant", self)
        self.prev_action.triggered.connect(self.prev_image)
        self.next_action.triggered.connect(self.next_image)

        # --- Rotation ---
        self.rotate_action = QAction(QIcon.fromTheme("object-rotate-right"), "Rotation 90° page en cours", self)
        self.rotate_action.triggered.connect(self.rotate_image)

        # self.delete_page_action = QAction("Suppression page", self)
        # self.delete_page_action = QAction(QIcon("icons/x_red.svg"), "Suppression page", self)
        # self.delete_page_action.setToolTip("Suppression page en cours")
        # toolbar.setIconSize(QSize(24, 24))  # Ajuste la taille de l’icône sur la barre
        # self.delete_page_action.triggered.connect(self.rotate_image)

        # --- Suppression ---
        self.delete_page_action = QAction(QIcon.fromTheme("edit-delete"), "Suppression page en cours", self)
        self.delete_page_action.setToolTip("Suppression page en cours")  # 🔹 bulle d’info
        self.delete_page_action.triggered.connect(self.delete_image)       # 



        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)
        toolbar.addSeparator()
        toolbar.addAction(self.prev_action)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.rotate_action)
        toolbar.addSeparator()
        toolbar.addAction(self.delete_page_action)

        # --- Ajout d'un indicateur d'état du pli ---
        

        # Espace flexible pour pousser les éléments vers la droite
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Champ texte "État de la page"
        self.page_status = QLineEdit()
        self.page_status.setReadOnly(True)
        self.page_status.setAlignment(Qt.AlignCenter)
        self.page_status.setFixedWidth(150)
        self.page_status.setText("Page non lue")

        self.page_status.setStyleSheet("""
            QLineEdit {
                background-color: #f9d0d0;
                color: #990000;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 2px;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        # 🔹 Ajoute un "étirement" pour pousser le champ à droite
        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addWidget(self.page_status)

        self.middle_layout.addWidget(toolbar)
        # self.update_page_status(False)
    def set_page_status(self, text, color="#003366"):
        """Met à jour le message de statut de la page"""
        self.page_status.setText(text)
        self.page_status.setStyleSheet(f"""
            QLineEdit {{
                background-color: #f0f0f0;
                color: {color};
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 2px;
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        #self.set_page_status("Pli validé", "#008000")     # vert
        # ou
        #self.set_page_status("Pli non validé", "#cc0000")  # rouge

    def setup_image_viewer(self):
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.middle_layout.addWidget(self.view)

    # --- Chargement des plis ---
    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except Exception:
            return 0
    def populate_pli_table(self):
        xml_files = sorted([f for f in os.listdir(self.lot_path) if f.lower().endswith(".xml")])
        self.plis = []
        current_pli = None
        for xml_file in xml_files:
            path = os.path.join(self.lot_path, xml_file)
            t = self.get_xml_type(path)
            if t == 2:
                current_pli = {"PLI": len(self.plis)+1, "DOC":1, "PG":0, "files":[path]}
                self.plis.append(current_pli)
            elif t in [3,4] and current_pli is not None:
                current_pli["PG"] += 1
                current_pli["files"].append(path)

        self.pli_table.setRowCount(len(self.plis))
        for i, pli in enumerate(self.plis):
            for col, key in enumerate(["LUES","IND","PLI","DOC","PG"]):
                val = str(pli.get(key,""))
                item = QTableWidgetItem(val)
                font = QFont()
                font.setBold(True)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)
                self.pli_table.setItem(i, col, item)
            # Couleurs alternées
            color = Qt.GlobalColor.red if i%2==0 else Qt.GlobalColor.green
            for col in range(5):
                self.pli_table.item(i,col).setBackground(color)
            
            #largeur fixex
            self.pli_table.setColumnWidth(0, 40)  # LUES
            self.pli_table.setColumnWidth(1, 40)  # IND
            self.pli_table.setColumnWidth(2, 50)  # PLI
            self.pli_table.setColumnWidth(3, 50)  # DOC
            self.pli_table.setColumnWidth(4, 50)  # PG

    # --- Vignettes ---
    def refresh_vignettes(self, images):
        self.list_widget.clear()
        self.image_items = []
        for img_path, xml_path in images:
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                item = QListWidgetItem(icon, os.path.basename(img_path))
                item.setData(Qt.UserRole, (img_path, xml_path))
                self.list_widget.addItem(item)
                self.image_items.append((img_path, xml_path))
        if self.image_items:
            self.show_image_and_info(self.list_widget.item(0))
    def show_all_vignettes(self):
        images = []
        for pli in self.plis:
            for xml_path in pli["files"]:
                img_path = os.path.splitext(xml_path)[0]+".jpg"
                if os.path.exists(img_path):
                    images.append((img_path, xml_path))
        self.refresh_vignettes(images)
    def filter_vignettes_by_pli(self, row, col):

        ###################tests
        # print('row : ', row, " - col : ", col)
        # print(self.pli_table.selectedItems()[0].data(0))
        # valeur = self.pli_table.item(row, 1).text()
        # print("Valeur de la cellule avant  :", valeur)
        # # self.pli_table.setItem(row, 1, QTableWidgetItem("IND"))
        # # valeur = self.pli_table.item(row, 1).text()
        # # print("Valeur de la cellule apres  :", valeur)

        # item = self.pli_table.item(row, 1)
        # if item:
        #     item.setText("IND")  # 🔹 Met à jour seulement le texte, garde le style existant
        # else:
        #     self.pli_table.setItem(row, col, QTableWidgetItem("IND"))  # si la cellule était vide
        # valeur = self.pli_table.item(row, 1).text()
        # print("Valeur de la cellule apres  :", valeur)
        ####################
       
        
        if row >= len(self.plis):
            return
        pli = self.plis[row]
        images = []
        for xml_path in pli["files"]:
            img_path = os.path.splitext(xml_path)[0]+".jpg"
            if os.path.exists(img_path):
                images.append((img_path, xml_path))
        self.refresh_vignettes(images)

        # Mise à jour des champs XML quand on clique sur un pli
        if pli["files"]:
            xml_path = pli["files"][0]  # on prend le premier XML du pli
            if os.path.exists(xml_path):
                infos = self.parse_xml(xml_path)
                self.champ_complexe.setText(infos.get("Complexe", ""))
                self.champ_complexe.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
                self.champ_complexe.setCursorPosition(0)
                self.champ_pole.setText(infos.get("Pôle", ""))
                self.champ_gestionnaire.setText(infos.get("Gestionnaire", ""))
                self.champ_titre_objet.setText(infos.get("Titre objet", ""))

                # 🔸 Mise à jour des info-bulles
                for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
                    champ.setToolTip(champ.text())

                # 🔸 Couleur orange si complexe vide
                if not self.champ_complexe.text().strip():
                    self.champ_complexe.setStyleSheet("""
                        QLineEdit {
                            background-color: orange;
                            color: #003366;
                            border: 1px solid #ddd;
                            padding: 2px 3px;
                            font-size: 10px;
                            font-weight: bold;
                            text-align: left;
                        }
                    """)
                    f = self.champ_complexe.font()
                    f.setBold(True)
                    self.champ_complexe.setFont(f)
                else:
                    self.champ_complexe.setStyleSheet("""
                        QLineEdit {
                            background-color: #f9f9f9;
                            color: #003366;
                            border: 1px solid #ddd;
                            padding: 2px 3px;
                            font-size: 10px;
                            font-weight: bold;
                            text-align: left;
                        }
                    """)
                    f = self.champ_complexe.font()
                    f.setBold(True)
                    self.champ_complexe.setFont(f)

        self.update_page_status(False)

    def is_pli_selected(self) -> bool:
        """Retourne True si un pli est sélectionné dans la table des plis."""
        return self.pli_table.currentRow() != -1

    # --- Affichage image et XML ---
    def show_image_and_info(self, item):
        """Affiche une image + ses infos XML, et marque la page comme lue seulement si un pli est sélectionné"""
        img_path, xml_path = item.data(Qt.UserRole)
        for i, (path, _) in enumerate(self.image_items):
            if path == img_path:
                self.current_index = i
                break

        self.display_image(img_path)
        self.display_xml_info(xml_path)

        if self.is_pli_selected():
            # ✅ Un pli est sélectionné → statut “page lue”
            if img_path not in self.pages_lues:
                self.pages_lues.add(img_path)
                self.update_page_status(True)
                self.check_all_pages_lues()
            else:
                self.update_page_status(True)
        else:
            # 🚫 Aucun pli sélectionné → ne pas changer le statut
            self.update_page_status(False)
    def display_image(self, img_path):
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.scene.clear()
            item = self.scene.addPixmap(pixmap)
            item.setTransformationMode(Qt.SmoothTransformation)
            self.reset_zoom()
    def display_xml_info(self, xml_path):
        if os.path.exists(xml_path):
            infos = self.parse_xml(xml_path)
            text = "\n".join(f"{k} : {v}" for k,v in infos.items() if v)
            lines = text.splitlines()
            self.info_text.setPlainText("\n".join(lines[:7]))

        #     self.champ_complexe.setText(infos.get("Complexe", ""))
        #     self.champ_complexe.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        #     self.champ_complexe.setCursorPosition(0)
        #     self.champ_pole.setText(infos.get("Pôle", ""))
        #     self.champ_gestionnaire.setText(infos.get("Gestionnaire", ""))
        #     self.champ_titre_objet.setText(infos.get("Titre objet", ""))
        # else:
        #     self.info_text.setPlainText("(Pas de fichier XML associé)")
        #     self.champ_complexe.setText( "")
        #     self.champ_pole.setText( "")
        #     self.champ_gestionnaire.setText( "")
        #     self.champ_titre_objet.setText("")

             # --- Remplissage des champs
            complexe_val = infos.get("Complexe", "")
            self.champ_complexe.setText(complexe_val)
            self.champ_complexe.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_complexe.setCursorPosition(0)
            self.champ_complexe.setToolTip(complexe_val)

            # 🔸 couleur du champ selon si vide ou non
            if complexe_val.strip() == "":
                self.champ_complexe.setStyleSheet("""
                    QLineEdit {
                        background-color: orange;
                        color: #003366;
                        border: 1px solid #ddd;
                        padding: 2px 3px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: left;
                    }
                """)
            else:
                self.champ_complexe.setStyleSheet("""
                    QLineEdit {
                        background-color: #f9f9f9;
                        color: #003366;
                        border: 1px solid #ddd;
                        padding: 2px 3px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: left;
                    }
                """)
            self.champ_complexe.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_complexe.setCursorPosition(0)
            self.champ_complexe.setStyleSheet("""
                    QLineEdit {
                        background-color: #f9f9f9;
                        color: #003366;
                        border: 1px solid #ddd;
                        padding: 2px 3px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: left;
                    }""")
            # autres champs
            self.champ_pole.setText(infos.get("Pôle", ""))
            self.champ_pole.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_pole.setCursorPosition(0)
            self.champ_pole.setStyleSheet("""
                QLineEdit {
                    background-color: #f9f9f9;
                    color: #003366;
                    border: 1px solid #ddd;
                    padding: 2px 3px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: left;
                }""")
            self.champ_gestionnaire.setText(infos.get("Gestionnaire", ""))
            self.champ_gestionnaire.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_gestionnaire.setCursorPosition(0)
            self.champ_gestionnaire.setStyleSheet("""
                QLineEdit {
                    background-color: #f9f9f9;
                    color: #003366;
                    border: 1px solid #ddd;
                    padding: 2px 3px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: left;
                }""")
            self.champ_titre_objet.setText(infos.get("Titre objet", ""))
            self.champ_titre_objet.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_titre_objet.setCursorPosition(0)
            self.champ_titre_objet.setStyleSheet("""
                QLineEdit {
                    background-color: #f9f9f9;
                    color: #003366;
                    border: 1px solid #ddd;
                    padding: 2px 3px;
                    font-size: 10px;
                    font-weight: bold;
                    text-align: left;
                }""")

        else:
            self.info_text.setPlainText("(Pas de fichier XML associé)")
            self.champ_complexe.clear()
            self.champ_pole.clear()
            self.champ_gestionnaire.clear()
            self.champ_titre_objet.clear()


        # Déterminer le pli auquel appartient cette page
        pli_type2_xml = None
        for pli in self.plis:
            if xml_path in pli["files"]:
                # Trouver la première page type 2 dans ce pli
                for f in pli["files"]:
                    infos = self.parse_xml(f)
                    if infos.get("Type") == "2":   # type 2 = pli
                        pli_type2_xml = f
                        break
                break


        if pli_type2_xml and os.path.exists(pli_type2_xml):
            infos = self.parse_xml(pli_type2_xml)
            # Mettre à jour les champs indexation
            self.champ_complexe.setText(infos.get("Complexe", ""))
            self.champ_complexe.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_complexe.setCursorPosition(0)
            self.champ_pole.setText(infos.get("Pôle", ""))
            self.champ_pole.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_pole.setCursorPosition(0)
            self.champ_gestionnaire.setText(infos.get("Gestionnaire", ""))
            self.champ_gestionnaire.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_gestionnaire.setCursorPosition(0)
            self.champ_titre_objet.setText(infos.get("Titre objet", ""))
            self.champ_titre_objet.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # ✅ Forçage
            self.champ_titre_objet.setCursorPosition(0)

            # Mettre à jour la zone info_text
            text = "\n".join(f"{k} : {v}" for k, v in infos.items() if v)
            lines = text.splitlines()
            self.info_text.setPlainText("\n".join(lines[:7]))

            # Info-bulles
            for champ in [self.champ_complexe, self.champ_pole, self.champ_gestionnaire, self.champ_titre_objet]:
                champ.setToolTip(champ.text())

        else:
            # Pas de pli type 2 trouvé pour ce pli
            self.info_text.setPlainText("(Pas de fichier XML de type 2 associé)")
            self.champ_complexe.clear()
            self.champ_pole.clear()
            self.champ_gestionnaire.clear()
            self.champ_titre_objet.clear()
    def parse_xml(self, xml_path):
        data = {"Erreur": ""}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            data["Type"] = root.findtext("type","")
            data["Etat"] = root.findtext("etat","")
            data["Rotation"] = root.findtext("rotation","")
            meta = root.find("meta")
            if meta is not None:
                data["Numaxa"] = meta.findtext("numaxa","")
                data["Service"] = meta.findtext("service","")
                data["Pôle"] = meta.findtext("pole","")
                data["Complexe"] = meta.findtext("complexe","")
                data["Gestionnaire"] = meta.findtext("gestionnaire","")
                data["Titre objet"] = meta.findtext("titreobjet","")
        except Exception as e:
            data["Erreur"] = f"Erreur: {e}"
        return data

    # --- Navigation et zoom ---
    def zoom_in(self): self.view.scale(1.2,1.2)
    def zoom_out(self): self.view.scale(1/1.2,1/1.2)
    def reset_zoom(self): self.view.resetTransform(); self.view.scale(self.zoom_factor,self.zoom_factor)
    def prev_image(self):
        if self.current_index>0:
            self.current_index-=1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)

             # 🔹 Vérifie qu'un pli est bien sélectionné dans la table
            if self.is_pli_selected():
                if img_path not in self.pages_lues:
                    self.pages_lues.add(img_path)
                self.update_page_status(True)
                self.check_all_pages_lues()
            else:
                # Aucun pli sélectionné → ne pas changer le statut
                self.update_page_status(False)
    def next_image(self):
        if self.current_index<len(self.image_items)-1:
            self.current_index+=1
            img_path, xml_path = self.image_items[self.current_index]
            self.display_image(img_path)
            self.display_xml_info(xml_path)
            self.list_widget.setCurrentRow(self.current_index)

            # 🔹 Vérifie qu'un pli est bien sélectionné dans la table
            if self.is_pli_selected():
                if img_path not in self.pages_lues:
                    self.pages_lues.add(img_path)
                self.update_page_status(True)
                self.check_all_pages_lues()
            else:
                # Aucun pli sélectionné → ne pas changer le statut
                self.update_page_status(False)
    def rotate_image(self):
        if not self.scene.items(): return
        item = self.scene.items()[0]
        pixmap = item.pixmap()
        transform = QTransform().rotate(90)
        rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.scene.clear()
        self.scene.addPixmap(rotated_pixmap).setTransformationMode(Qt.SmoothTransformation)
        img_path, _ = self.image_items[self.current_index]
        rotated_pixmap.save(img_path)
        self.update_thumbnail()

    def update_thumbnail(self):
        item = self.list_widget.item(self.current_index)
        img_path,_ = self.image_items[self.current_index]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            icon = QIcon(pixmap.scaled(120,120,Qt.KeepAspectRatio))
            item.setIcon(icon)

    def show_status_message(self, message, duration=4000):
        """Affiche un message temporaire dans la barre d’état."""
        self.status_label.setText(message)
        QTimer.singleShot(duration, lambda: self.status_label.setText(""))

    def delete_image(self):
        self.btn_livraison_lot.setEnabled(True)
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: #1fb0e0; color: blue; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')

    def valid_pli(self):
        self.btn_livraison_lot.setEnabled(False)
        self.btn_livraison_lot.setStyleSheet('QPushButton {background-color: white; color: grey; font:bold; font-size:16px} QPushButton:hover { color: yellow; }')
        # self.champ_gestionnaire.setText("Nouveau gestionnaire")
        # self.champ_titre_objet.setText("Titre modifié automatiquement")

    def update_page_status(self, lue: bool):
        """Met à jour la zone de statut de page"""
        if lue:
            self.page_status.setText("Page lue")
            self.page_status.setStyleSheet("""
                QLineEdit {
                    background-color: #d8f5d0;
                    color: #006600;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
        else:
            self.page_status.setText("Page non lue")
            self.page_status.setStyleSheet("""
                QLineEdit {
                    background-color: #f9d0d0;
                    color: #990000;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

    def check_all_pages_lues(self):
        """Vérifie si toutes les pages du pli courant sont lues, sinon met à jour la colonne LUES"""
        if not hasattr(self, "pli_table") or not hasattr(self, "plis"):
            return

        if not self.image_items:
            return

        current_xml = self.image_items[self.current_index][1]
        pli_index = None

        for i, pli in enumerate(self.plis):
            if current_xml in pli["files"]:
                pli_index = i
                break

        if pli_index is None:
            return

        pli = self.plis[pli_index]
        toutes_lues = True

        for xml_path in pli["files"]:
            img_path = os.path.splitext(xml_path)[0] + ".jpg"
            if os.path.exists(img_path) and img_path not in self.pages_lues:
                toutes_lues = False
                break

        item = self.pli_table.item(pli_index, 0)  # Colonne "LUES"
        if not item:
            item = QTableWidgetItem()
            self.pli_table.setItem(pli_index, 0, item)

        if toutes_lues:
            item.setText("L")
            item.setTextAlignment(Qt.AlignCenter)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor("#006600"))

             # ✅ Message console
            msg_pli = f"✅ Toutes les pages du pli {pli_index + 1} sont lues"
            print(msg_pli)
            self.show_status_message(msg_pli)

            # 🔹 Vérifie si tous les plis du lot sont lues
            tous_lus = True
            for row in range(self.pli_table.rowCount()):
                cell = self.pli_table.item(row, 0)
                if not cell or cell.text().strip() != "L":
                    tous_lus = False
                    break

            if tous_lus:
                lot_num = os.path.basename(self.lot_path)
                msg_lot = f"🟢 Tous les plis du lot {lot_num} sont lues"
                print(msg_lot)
                self.show_status_message(msg_lot, duration=6000)

        else:
            item.setText("")

    def closeEvent(self,event):
        if self.parent_window is not None:
            self.parent_window.show()
        super().closeEvent(event)


class LotsSummary(QWidget):
    """Fenêtre principale pour sélectionner un dossier LOTS et afficher un résumé"""

    def __init__(self, parent=None, config=None):
        super().__init__()
        self.parent_window = parent
        self.config = config
        self.setWindowTitle("Choix et Résumé des Lots")
        self.resize(1500, 700)
        self.layout = QVBoxLayout(self)
        self.open_viewers = []
        self.lots_dir = None
        
        # --- Lecture config.ini ---
        # self.config = load_config()

        # --------------------------
        # Bouton selection dossier
        # --------------------------
        self.btn_select_dir = QPushButton("Sélectionner le dossier 'Lots'")
        self.btn_select_dir.clicked.connect(self.select_directory)
        self.layout.addWidget(self.btn_select_dir)

        # --------------------------
        # Tableau des Lots
        # --------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(18)  # AJUSTÉ !
        self.table.setHorizontalHeaderLabels([
            "N° SATEC", "Service", "N° Lot",

            "Date Création", "Créé par", "Ouvert le", "Ouvert par",
            "Verrouillé", "Pli", "Page", "Date Livraison",

            "NbJPG", "NbXT1", "NbXT2",
            "NbXT3", "NbXT4", "NbPDF", "NbPages"
        ])

        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.open_lot_viewer)
        self.layout.addWidget(self.table)

        self.setup_table_style()

        self.check_widgets = {}

        # Chargement auto si config.ini
        if self.config and os.path.exists(self.config.get("lots_path", "")):
            self.lots_dir = self.config["lots_path"]
            self.load_summary(self.lots_dir)
        else:
            print("⚠️ Aucun chemin valide dans config.ini")
            
        #menu contextuel activation
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        print("Lots path:", self.config["lots_path"]) # type: ignore
        print("dsn", self.config["dsn"]) # type: ignore
        

        

    # --------------------------------------------------------------------
    # STYLE TABLE
    # --------------------------------------------------------------------
    def setup_table_style(self):
        """Style général de la grille"""
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #CCCCCC;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #E8EEF7;
                font-weight: bold;
                font-size: 13px;
                padding: 4px;
                border: 1px solid #AAAAAA;
            }
        """)

        # Colonnes XML SATEC
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 250)

        # Colonnes "Nb..."
        for col in range(11, 18):
            self.table.setColumnWidth(col, 60)

        # Colonnes supplémentaires
        self.table.setColumnWidth(3, 150)  # Date Création
        self.table.setColumnWidth(4, 120)  # Créé par
        self.table.setColumnWidth(5, 150)  # Ouvert le
        self.table.setColumnWidth(6, 120)  # Ouvert par
        self.table.setColumnWidth(7, 100)  # Verrouillé
        self.table.setColumnWidth(8, 70)   # Pli
        self.table.setColumnWidth(9, 70)   # Page
        self.table.setColumnWidth(10, 150) # Date Livraison


    
       

    # --------------------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------------------
    # def load_config(self):
    #     config = configparser.ConfigParser()

    #     # base_dir = os.path.dirname(os.path.dirname(__file__))  # dispatcher_app/
    #     # config_path = os.path.join(base_dir, "config", "config.ini")

    #     # --- Calcul du dossier où se trouve l'exe/script ---
    #     if getattr(sys, 'frozen', False):
    #         # Mode exe
    #         base_dir = os.path.dirname(sys.executable)
    #         config_path = os.path.join(base_dir, "config.ini")
    #     else:
    #         # Mode script Python
    #         base_dir = os.path.dirname(os.path.dirname(__file__))  # dispatcher_app/
    #         config_path = os.path.join(base_dir, "config", "config.ini")


    #     if not os.path.exists(config_path):
    #         print("⚠️ config.ini introuvable :", config_path)
    #         return None

    #     config.read(config_path, encoding="utf-8")

    #     if "PARAMS" in config:
    #         return {
    #             "lots_path": config["PARAMS"].get("lots_path", "")
    #         }
    #     return None

    # --------------------------------------------------------------------
    # ACTIVATION MENU CONTEXTUEL
    # --------------------------------------------------------------------
    def open_context_menu(self, position):
        """Menu clic droit sur un lot."""
        index = self.table.indexAt(position)

        if not index.isValid():
            return  # clic hors des lignes

        # Récupération du nom du lot cliqué
        row = index.row()
        lot_name = self.table.item(row, 0).text() if self.table.item(row, 0) else None

        menu = QMenu(self)

        action_unlock = QAction("Déverrouiller lot", self)
        action_refresh = QAction("Rafraîchir", self)

        menu.addAction(action_unlock)
        menu.addAction(action_refresh)

        # Connexions
        action_unlock.triggered.connect(lambda: self.unlock_lot(lot_name))
        action_refresh.triggered.connect(self.refresh_lots)

        # afficher le menu à la position du curseur
        menu.exec(self.table.viewport().mapToGlobal(position))

    # --------------------------------------------------------------------
    # SELECTION DOSSIER LOTS
    # --------------------------------------------------------------------
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir le dossier Lots")
        if directory:
            self.lots_dir = directory
            self.load_summary(directory)

    # --------------------------------------------------------------------
    # EXTRACTION XML TYPE 1
    # --------------------------------------------------------------------
    def extract_type1_info(self, lot_dir):
        for file in os.listdir(lot_dir):
            if file.lower().endswith(".xml"):
                path = os.path.join(lot_dir, file)
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()

                    if root.findtext("type", "").strip() == "1":
                        meta = root.find("meta")
                        if meta is None:
                            return "", ""
                        return (
                            meta.findtext("numaxa", "").strip(),
                            meta.findtext("service", "").strip()
                        )
                except Exception:
                    pass
        return "", ""

    # --------------------------------------------------------------------
    # CENTRAGE DE LA CASE A COCHER
    # --------------------------------------------------------------------
    def make_centered_checkbox(self, checked=False):
        """Retourne un widget contenant une checkbox centrée dans la cellule."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        chk = QCheckBox()
        chk.setChecked(checked)
        chk.setEnabled(False)     # ❌ l'utilisateur NE PEUT PAS cliquer

        layout.addWidget(chk)
        return widget, chk
    
    # --------------------------------------------------------------------
    # CHARGEMENT DES LOTS
    # --------------------------------------------------------------------
    def load_summary(self, lots_dir):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for subdir in sorted(os.listdir(lots_dir)):
            subpath = os.path.join(lots_dir, subdir)

            if os.path.isdir(subpath) and subdir.isdigit() and len(subdir) == 5:

                numaxa, service = self.extract_type1_info(subpath)

                jpg_count = 0
                xml_counts = {1: 0, 2: 0, 3: 0, 4: 0}

                for file in os.listdir(subpath):
                    fpath = os.path.join(subpath, file)

                    if file.lower().endswith(".jpg"):
                        jpg_count += 1

                    elif file.lower().endswith(".xml"):
                        t = self.get_xml_type(fpath)
                        if t in xml_counts:
                            xml_counts[t] += 1

                nb_plis = xml_counts[2]
                nb_pages_total = xml_counts[3] + xml_counts[4]

                # Date actuelle
                date_creation = datetime.now().strftime("%d/%m/%Y %H:%M")

                # Ligne
                row = self.table.rowCount()
                self.table.insertRow(row)

                values = [
                    numaxa, service, subdir,
                    date_creation, "dispatcher", "", "",  # ouvert le / par vides
                    "",   # Verrouillé → case cochable, valeur mise plus tard
                    str(nb_plis), str(nb_pages_total), 
                    "",#date livraison
                    str(jpg_count), str(xml_counts[1]), str(xml_counts[2]),
                    str(xml_counts[3]), str(xml_counts[4]),
                    str(nb_plis), str(nb_pages_total)
                ]

                for col, val in enumerate(values):

                    # --------------------
                    # COCHAGE (col 7)
                    # --------------------
                    # if col == 7:
                    #     item = QTableWidgetItem()
                    #     item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    #     item.setCheckState(Qt.Unchecked)
                    #     self.table.setItem(row, col, item)
                    #     continue

                    if col == 7:  # colonne Verrouillé -> checkbox centrée
                        widget, chk = self.make_centered_checkbox(False)
                        self.table.setCellWidget(row, col, widget)
                        self.check_widgets[(row, col)] = chk  # pour pouvoir la modifier plus tard
                        continue

                    #modification case par code
                    
                    # chk = self.table.check_widgets.get((row, 7))
                    # #cocher
                    # if chk:
                    #     chk.setChecked(True)

                    # chk = self.table.check_widgets.get((row, 7))
                    # #decocher
                    # if chk:
                    #     chk.setChecked(False)


                    item = QTableWidgetItem(val)
                    item.setToolTip(val)

                    # Alignement centré sauf pour XML SATEC/service et dates
                    if col not in (0, 1, 3, 10):
                        item.setTextAlignment(Qt.AlignCenter)

                    # Style spécial XML type 1 (cols 0 et 1)
                    if col in (0, 1):
                        item.setBackground(QColor("#FFF6D1"))
                        f = item.font()
                        f.setBold(True)
                        item.setFont(f)
                        item.setForeground(QColor("#003366"))

                    self.table.setItem(row, col, item)

        self.table.setSortingEnabled(True)

    # --------------------------------------------------------------------
    # TYPE XML
    # --------------------------------------------------------------------
    def get_xml_type(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            t = root.findtext("type", "").strip()
            return int(t) if t.isdigit() else 0
        except:
            return 0

    # --------------------------------------------------------------------
    # OUVERTURE LOT VIEWER
    # --------------------------------------------------------------------
    def open_lot_viewer(self, row, column):
        if not self.lots_dir:
            return

        lot_name = self.table.item(row, 2).text()
        lot_path = os.path.join(self.lots_dir, lot_name)

        if os.path.exists(lot_path):
            
            viewer = LotViewer(lot_path)
            viewer.parent_window = self
            self.open_viewers.append(viewer)

            viewer.show()
            viewer.raise_()
            viewer.activateWindow()
            self.hide()

    # --------------------------------------------------------------------
    # MENU CONTEXTUEL DEVERROUILLER LOT
    # --------------------------------------------------------------------
    def unlock_lot(self, lot_name):
        """Déverrouille un lot (fonction à compléter)."""
        print(f"[DEBUG] Demande de déverrouillage du lot : {lot_name}")

    # --------------------------------------------------------------------
    # MENU CONTEXTUEL RAFFRAICHIR LISTE DES LOTS
    # --------------------------------------------------------------------
    def refresh_lots(self):
        """Rafraîchit la liste des lots (fonction à compléter)."""
        print("[DEBUG] Rafraîchissement demandé")

    # --------------------------------------------------------------------
    # RETOUR A LA FENETRE PRINCIPALE DE DEMARRAGE
    # --------------------------------------------------------------------
    def closeEvent(self,event):
        if self.parent_window is not None:
            self.parent_window.show()
        event.accept()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = LotsSummary()
#     window.show()
#     sys.exit(app.exec())
