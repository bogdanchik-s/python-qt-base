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

        for u in db_data['user']:
            if u['login'] == login and u['password'] == password:
                global current_user
                current_user = u

                main_window.show()
                self.accept()
                
                return
        
        if register == True:
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
