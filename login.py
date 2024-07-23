import MySQLdb
import os
import time
import configparser
import socket

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
        print('Connecting to database...')
        try:
            socket.setdefaulttimeout(7) # Set maximum attempt timeout to 7 seconds
            self.conn = MySQLdb.connect(
                host=config.get('database', 'host'),
                user=config.get('database', 'user'),
                passwd=config.get('database', 'passwd'),
                db=config.get('database', 'db'),
                charset='utf8'
            )
        except MySQLdb.OperationalError as e:
            print(f"Error: {e} \nMake sure you are not connected to school network!")
            exit(1)

        except socket.timeout:
            print(f"Connection attempt timed out.")
            exit(1)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)
    
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
                print("Registration successfully. \nYou will be returned to the Start menu to login \n")
                time.sleep(2)
                start()
            except MySQLdb.Error as e:
                self.conn.rollback()
                print(f'Error: {e}\nRegistration failed. \nYou will be returned to the Start menu \n')
                start()
        self.close_conn()

def register():
    print('Registration menu:')
    register_name = input("Enter a username: \n")
    register_pwd = input("Enter a password: \n")
    obj_r = MysqlSearch()
    obj_r.insert_userinfo(register_name, register_pwd)

def login():
    print('Login menu:')
    obj = MysqlSearch()
    result = obj.get_userinfo()
    name = input("Enter your username: \n")
    pwd = input("Enter your password: \n")
    
    user = next((item for item in result if item['username'] == name and item['password'] == pwd), None)
    
    if user:
        user_username = user["username"]
        print(f"Successfully logged in to \'{user_username}\'. \nYou will be moved to the Main menu")
        time.sleep(2)
        main_menu(user_username)
    else:
        print("Username or password is wrong.\n You will be returned to the Start menu")
        time.sleep(2)
        start()

# Startup menu
def start():
    os.system('cls')
    choice = input("Start Menu: \nEnter \"1\" for Login Menu \nEnter \"2\" for Registration Menu \nEnter \"3\" to exit the program \n")
    os.system('cls')
    if choice == "1":
        login()
    elif choice == "2":
        register()
    elif choice == "3":
        print("Good-bye!")
        time.sleep(1)
        exit(1)
    else:
        print('Your input is not valid!')
        time.sleep(2)
        start()

### TODO: Main menu
def main_menu(username):
    os.system('cls')
    choice = input(f"Welcome {username}!: \nEnter \"1\" for Check booking status \nEnter \"2\" for Make a booking \nEnter \"3\" to exit the program \n")
    os.system('cls')

    if choice == "1":
        #TODO: Check booking service
        print('1')
    elif choice == "2":
        #TODO: Booking service
        print('2')
    elif choice == "3":
        print("Good-bye!")
        time.sleep(1)
        exit(1)
    else:
        print('Your input is not valid!')
        time.sleep(2)
        start()

if __name__ == "__main__": # Ensure that certain code is only executed when the script is run directly
    start()
