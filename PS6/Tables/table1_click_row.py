from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtCore import QAbstractTableModel,QAbstractItemModel, QModelIndex, Qt

class MyTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 400, 300)

        data = [
            ["Row 0, Col 0", "Row 0, Col 1"],
            ["Row 1, Col 0", "Row 1, Col 1"],
            ["Row 2, Col 0", "Row 2, Col 1"]
        ]
        self.model = MyTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.setCentralWidget(self.table_view)

        # Connect the clicked signal to a slot
        self.table_view.clicked.connect(self.on_table_clicked)

    def on_table_clicked(self, index: QModelIndex):
        row = index.row()
        column = index.column()
        print(f"Clicked on row: {row}, column: {column}")
        # To get the entire row's data:
        row_data = [self.model.data(self.model.index(row, col)) for col in range(self.model.columnCount())]
        print(f"Row data: {row_data}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()