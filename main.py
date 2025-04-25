from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from mysql.connector import MySQLConnection

from ui_auth_dialog import UI_AuthDialog


db_connect: MySQLConnection = None
db_data = {}

current_user = None

auth_dialog = None
main_window = None


def load_data():
    tables = ['user']

    with db_connect.cursor(dictionary=True) as db_cursor:
        for table in tables:
            db_cursor.execute(f'select * from `{table}`;')
            db_data[table] = db_cursor.fetchall()


def get_data_by_field(table: str, field: str, value: str):
    if table not in db_data:
        return None
    
    for item in db_data[table]:
        if item[field] == value:
            return item
    
    return None


class AuthDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = UI_AuthDialog()
        self.ui.setupUi(self)

        self.ui.loginButton.released.connect(self.login)
        self.ui.registerButton.released.connect(lambda: self.login(register=True))
    
    def login(self, register=False):
        login = self.ui.loginInput.text()
        password = self.ui.passwordInput.text()

        if not login or not password:
            return

        user = get_data_by_field('user', 'login', login)

        if user is not None:
            if password == user['password']:
                global current_user
                current_user = user

                main_window.show()
                
                return self.accept()
        
        elif register == True:
            with db_connect.cursor() as db_cursor:
                db_cursor.execute('insert into `user` (`login`, `password`) values (%s,%s)', (login, password))
            
            load_data()

            return self.login(register=register)


if __name__ == '__main__':
    app = QApplication([])

    load_data()

    auth_dialog = AuthDialog()
    auth_dialog.show()

    app.exec()
