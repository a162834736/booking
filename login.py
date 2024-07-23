import MySQLdb
import os
import time
import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to the database
class MysqlSearch(object):
    def __init__(self):
        self.conn = None
        self.get_conn()
 
    # Get connection
    def get_conn(self):
        os.system('cls')
        print('Connecting to database...')
        try:
            self.conn = MySQLdb.connect(
                host=config.get('database', 'host'),
                user=config.get('database', 'user'),
                passwd=config.get('database', 'passwd'),
                db=config.get('database', 'db'),
                charset='utf8'
            )

        except MySQLdb.Error as e:
            print(f'Error: {e}')

    # Close connection 
    def close_conn(self):
        if self.conn:
            try:
                self.conn.close()
            except MySQLdb.Error as e:
                print(f'Error: {e}')

    # Get user info
    def get_userinfo(self):
        sql = 'SELECT * FROM user'
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            result = [dict(zip([k[0] for k in cursor.description], row)) for row in result]
        self.close_conn()
        return result

    # Register
    def insert_userinfo(self, a, b):
        if not a or not b:
            print("Registration failed. You will be returned to the main menu \n")
            time.sleep(1)
            start()
            return

        sql_check = 'SELECT username FROM user WHERE username = %s'
        sql_insert = 'INSERT INTO user(username, password) VALUES(%s, %s)'
        with self.conn.cursor() as cursor:
            cursor.execute(sql_check, (a,))
            if cursor.fetchone():
                print("User already exists! \nYou will be returned to the main menu \n")
                time.sleep(2)
                start()
                return

            try:
                cursor.execute(sql_insert, (a, b))
                self.conn.commit()
                print("Registration successfully. \nYou will be returned to the main menu \n")
                time.sleep(2)
                start()
            except MySQLdb.Error as e:
                self.conn.rollback()
                print(f'Error: {e}\nRegistration failed.')
                start()
        self.close_conn()

def register():
    register_name = input("Enter a username: \n")
    register_pwd = input("Enter a password: \n")
    obj_r = MysqlSearch()
    obj_r.insert_userinfo(register_name, register_pwd)

def login():
    obj = MysqlSearch()
    result = obj.get_userinfo()
    name = input("Enter your username: \n")
    pwd = input("Enter your password: \n")
    
    user = next((item for item in result if item['username'] == name and item['password'] == pwd), None)
    
    if user:
        print("Login successfully.")
    else:
        print("Username or password is wrong.\n You will be returned to the main menu")
        time.sleep(2)
        start()

def start():
    os.system('cls')
    choice = input("Main Menu: \nEnter \"1\" for Login Menu \nEnter \"2\" for Registration Menu \n")
    if choice == "1":
        os.system('cls')
        login()
    elif choice == "2":
        os.system('cls')
        register()
    else:
        print('Your input is not valid!')
        time.sleep(2)
        start()

### TODO: Create main menu


start()
