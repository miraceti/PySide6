import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLineEdit, QListView, QLabel
)
from PySide6.QtCore import QTimer
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel


class FullTextSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recherche Full-Text SQL Server")
        self.resize(600, 400)

        # --- UI ---
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Tapez au moins 2 caractères...")
        self.status = QLabel()
        self.view = QListView()

        layout = QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.view)
        layout.addWidget(self.status)

        # --- SQL ---
        self.db = self.create_connection()
        self.model = QSqlQueryModel(self)
        self.view.setModel(self.model)

        # --- Debounce ---
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)

        self.edit.textChanged.connect(self.timer.start)
        self.timer.timeout.connect(self.search)

    def create_connection(self):
        db = QSqlDatabase.addDatabase("QODBC")
        db.setDatabaseName(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=MON_SERVEUR;"
            "Database=MA_BASE;"
            "Trusted_Connection=yes;"
        )

        if not db.open():
            raise RuntimeError(db.lastError().text())

        return db

    def search(self):
        text = self.edit.text().strip()

        if len(text) < 2:
            self.model.setQuery("SELECT TOP 0 flor_immat_risque FROM fl_risque", self.db)
            self.status.setText("⏳ Entrez au moins 2 caractères")
            return

        # échappement minimal pour CONTAINS
        text = text.replace('"', '""')

        query = f"""
            SELECT TOP 50 flor_immat_risque
            FROM fl_risque
            WHERE CONTAINS(flor_immat_risque, '"{text}*"')
            ORDER BY flor_immat_risque
        """

        self.model.setQuery(query, self.db)

        if self.model.lastError().isValid():
            self.status.setText("❌ Erreur SQL")
        else:
            self.status.setText(f"✅ {self.model.rowCount()} résultat(s)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FullTextSearch()
    w.show()
    sys.exit(app.exec())
