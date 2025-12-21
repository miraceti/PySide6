from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QMessageBox
)
from PySide6.QtGui import QAction

from forms.home_view import HomeView
from forms.form_intercalaire import FormIntercalaire
from forms.form_scan import FormScan
from forms.form_dispatcher import FormDispatcher


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GED – Traitement des plis")

        # Zone centrale
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.home_view = HomeView()
        self.form_intercalaire = FormIntercalaire()
        self.form_scan = FormScan()
        self.form_dispatcher = FormDispatcher()

        # Ajout au stack
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.form_intercalaire)
        self.stack.addWidget(self.form_scan)
        self.stack.addWidget(self.form_dispatcher)

        self.stack.setCurrentWidget(self.home_view)

        self._create_menu()

    # ---------------- MENU ---------------- #

    def _create_menu(self):
        menu_bar = self.menuBar()

        menu_fichier = menu_bar.addMenu("Fichier")
        menu_intercalaire = menu_bar.addMenu("Intercalaires")
        menu_scan = menu_bar.addMenu("Scan")
        menu_dispatcher = menu_bar.addMenu("Dispatcher")

        # --- Fichier ---
        act_quitter = QAction("Quitter", self)
        act_quitter.triggered.connect(self.close)
        menu_fichier.addAction(act_quitter)

        # --- Intercalaires ---
        act_intercalaire = QAction("Création intercalaire", self)
        act_intercalaire.triggered.connect(
            lambda: self.stack.setCurrentWidget(self.form_intercalaire)
        )
        menu_intercalaire.addAction(act_intercalaire)

        # --- Scan ---
        act_scan = QAction("Scan vers lots", self)
        act_scan.triggered.connect(
            lambda: self.stack.setCurrentWidget(self.form_scan)
        )
        menu_scan.addAction(act_scan)

        # --- Dispatcher ---
        act_dispatcher = QAction("Traitement des plis", self)
        act_dispatcher.triggered.connect(self._open_dispatcher)
        menu_dispatcher.addAction(act_dispatcher)

    # ---------------- DISPATCHER ---------------- #

    def _open_dispatcher(self):
        """
        Appelé uniquement quand l'utilisateur clique sur le menu Dispatcher
        """
        try:
            self.form_dispatcher.ask_and_open_lot_folder()
            self.stack.setCurrentWidget(self.form_dispatcher)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
