import sqlite3
from PySide6.QtWidgets import *

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLITE Database")
        self.setGeometry(100,100,900,200)

        name_label = QLabel("Name")
        profession_label = QLabel("Profession")
        address_label = QLabel("Address")
        age_label = QLabel("Age")

        self.name_line_edit = QLineEdit()
        self.profession_line_edit = QLineEdit()
        self.address_line_edit = QLineEdit()
        self.age_line_edit = QLineEdit()

        button_add_data = QPushButton("Add new row")
        button_add_data.clicked.connect(self.add_data)

        button_update_data = QPushButton("Update selected row")
        button_update_data.clicked.connect(self.update_data)

        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(name_label)
        h_layout1.addWidget(self.name_line_edit)

        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(profession_label)
        h_layout2.addWidget(self.profession_line_edit)

        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(address_label)
        h_layout3.addWidget(self.address_line_edit)

        h_layout4 = QHBoxLayout()
        h_layout4.addWidget(age_label)
        h_layout4.addWidget(self.age_line_edit)

        h_layout5 = QHBoxLayout()
        h_layout5.addWidget(button_add_data)
        h_layout5.addWidget(button_update_data)


        add_form = QGroupBox("Add New Employee")
        form_layout = QVBoxLayout()
        form_layout.addLayout(h_layout1)
        form_layout.addLayout(h_layout2)
        form_layout.addLayout(h_layout3)
        form_layout.addLayout(h_layout4)
        form_layout.addLayout(h_layout5)
        add_form.setLayout(form_layout)

        self.table = QTableWidget(self)
        self.table.setMaximumWidth(800)

        self.table.setColumnCount(4)
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 50)

        self.table.setHorizontalHeaderLabels(["Name","Profession","Address","Age"])

        button_insert_data = QPushButton("Insert DEMO data")
        button_insert_data.clicked.connect(self.insert_data)

        button_load_data = QPushButton("Load DEMO data")
        button_load_data.clicked.connect(self.load_data)

        button_call_data = QPushButton("Extract data")
        button_call_data.clicked.connect(self.call_data)

        button_delete_data = QPushButton("Delete data")
        button_delete_data.clicked.connect(self.delete_data)



        layout = QVBoxLayout()
        layout.addWidget(add_form)
        layout.addWidget(self.table)
        layout.addWidget(button_insert_data)
        layout.addWidget(button_load_data)
        layout.addWidget(button_call_data)
        layout.addWidget(button_delete_data)

        self.setLayout(layout)
        

    def create_connection(self):
        self.connection = sqlite3.connect("employees.db")

        return self.connection

    def insert_data(self):
        self.cursor = self.create_connection().cursor()

        self.cursor.execute("create table employees_list (Name text, Profession text, Address text, Age integer)")

        self.list_of_employees = [
            ("Emmanuel Olega", "Software Engineer", "Kampala", 28),
            ("Esther Olega", "Veterinarian", "Wakiso", 24),
            ("jjuuko Henry", "Accountant", "Masaka", 25),
            ("Apio Brenda", "Civil Engineer", "Gulu", 22),
        ]

        self.cursor.executemany("Insert into employees_list values (?,?,?,?)", self.list_of_employees)
        print("Insertion data faite ok")
        self.connection.commit()

        self.connection.close()

    def add_data(self):
        self.cursor = self.create_connection().cursor()

        self.new_employee = [
            self.name_line_edit.text(),
            self.profession_line_edit.text(),
            self.address_line_edit.text(),
            self.age_line_edit.text(),
        ]

        self.cursor.execute("Insert into employees_list values(?,?,?,?)", self.new_employee)

        print("Nouveau nom ajouté : ", self.name_line_edit.text())

        self.name_line_edit.clear()
        self.profession_line_edit.clear()
        self.address_line_edit.clear()
        self.age_line_edit.clear()

        
        self.connection.commit()
        self.connection.close()
    

    def load_data(self):
        self.cursor = self.create_connection().cursor()
        rowCount_sqlquery = "SELECt COUNT(*) FROM employees_list"
        employees_sqlquery = "SELECT * FROM employees_list"

        self.cursor.execute(rowCount_sqlquery)
        results = self.cursor.fetchone()

        print("Nombre de lignes : ", results[0])
        self.table.setRowCount(results[0])

        table_row = 0
        for i in self.cursor.execute(employees_sqlquery):
            self.table.setItem(table_row, 0, QTableWidgetItem(i[0]))
            self.table.setItem(table_row, 1, QTableWidgetItem(i[1]))
            self.table.setItem(table_row, 2, QTableWidgetItem(i[2]))
            self.table.setItem(table_row, 3, QTableWidgetItem(str(i[3])))
            table_row = table_row + 1

    def call_data(self):
        current_row_index = self.table.currentRow()

        self.name_edit = str(self.table.item(current_row_index, 0).text())
        self.profession_edit = str(self.table.item(current_row_index, 1).text())
        self.address_edit = str(self.table.item(current_row_index, 2).text())
        self.age_edit = str(self.table.item(current_row_index, 3).text())

        self.name_line_edit.setText(self.name_edit)
        self.profession_line_edit.setText(self.profession_edit)
        self.address_line_edit.setText(self.address_edit)
        self.age_line_edit.setText(self.age_edit)

    def update_data(self):
        self.cursor = self.create_connection().cursor()

        params = (
            self.name_line_edit.text(),
            self.profession_line_edit.text(),
            self.address_line_edit.text(),
            self.age_line_edit.text(),
            self.name_edit
        )

        self.cursor.execute("UPDATE employees_list SET Name=?, Profession=?, Address=?, Age=? WHERE Name=?",
                            params)
        
        print("the old name was ", self.name_edit)
        print("the new name is ", self.name_line_edit.text())

        self.name_line_edit.clear()
        self.profession_line_edit.clear()
        self.address_line_edit.clear()
        self.age_line_edit.clear()

        self.connection.commit()
        self.connection.close()

    def delete_data(self):
        self.cursor = self.create_connection().cursor()

        current_row_index = self.table.currentRow()

        name_item = str(self.table.item(current_row_index, 0).text())

        if current_row_index < 0:
            Warning = QMessageBox.warning(self, 'Warning', 'merci de sélectionner une ligne a supprimer')
        else:
            Message = QMessageBox.question(self, 'Confirmation', 'Etes vous sur de supprimer la ligne sélectionnée ?',
                                           QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            
        if Message == QMessageBox.StandardButton.Yes:
            sqlquery = "DELETE FROM employees_list WHERE Name=?"
            self.cursor.execute(sqlquery, (name_item,))
            print("tu as supprimé ", name_item)

        self.connection.commit()
        self.connection.close()



