import pymysql
import os
import time
import configparser
import socket

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')
        
# Connect to the SQL database
class MysqlSearch(object):
    def __init__(self):
        self.conn = None
        self.get_conn()
 
    # Get connection
    def get_conn(self):
        print('Connecting to database...')
        try:
            socket.setdefaulttimeout(7) # Set maximum attempt timeout to 7 seconds
            self.conn = pymysql.connect(
                host='45.76.177.52',
                user='root',
                passwd='ausmat',
                db='ausmat',
                charset='utf8'
            )
        except pymysql.OperationalError as e:
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
            except pymysql.Error as e:
                print(f'Error: {e}')

    # Get user info from database
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
            startup_menu()
            return

        sql_check = 'SELECT username FROM user WHERE username = %s'
        sql_insert = 'INSERT INTO user(username, password) VALUES(%s, %s)'
        with self.conn.cursor() as cursor:
            cursor.execute(sql_check, (a,))
            if cursor.fetchone():
                print("User already exists! \nYou will be returned to the main menu \n")
                time.sleep(2)
                startup_menu()
                return

            try:
                cursor.execute(sql_insert, (a, b))
                self.conn.commit()
                print("Registration successful. \nYou will be returned to the Start menu to login \n")
                time.sleep(2)
                startup_menu()
            except pymysql.Error as e:
                self.conn.rollback()
                print(f'Error: {e}\nRegistration failed. \nYou will be returned to the Start menu \n')
                startup_menu()
        self.close_conn()

    def get_user_booking(self, booked_user):
        sql = 'SELECT * FROM facilities_details WHERE booked_user = %s'
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (booked_user,))
            result = cursor.fetchall()
            result = [dict(zip([k[0] for k in cursor.description], row)) for row in result]
        self.close_conn()
        return result


# Defining variables to be output in Startup Menu

# (1) LOGIN
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
        startup_menu()

# (2) REGISTER
def register():
    print('Registration menu:')
    register_name = input("Enter a username: \n")
    register_pwd = input("Enter a password: \n")
    obj_r = MysqlSearch()
    obj_r.insert_userinfo(register_name, register_pwd)
    
tempuser=str()


# Defining necessary variables to be output in Main Menu:
# VIEW BOOKINGS
def check(username):
    print('Registration menu:')
    obj_c = MysqlSearch()
    bookings = obj_c.get_user_booking(username)
    if bookings:
        print("Your bookings:")
        for booking in bookings:
            fac_id = booking['fac_id']
            print(f'Facility id booked: {fac_id}')
            main_menu(username)
    else:
        print("No bookings found.\nYou will be returned to the Main menu \n")
        time.sleep(2)
        main_menu(username)


# STARTUP MENU
def startup_menu():
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
        startup_menu()

### TODO: Main menu
def main_menu(username):
    os.system('cls')
    choice = input(f"Welcome {username}!: \nEnter \"1\" for Check booking status \nEnter \"2\" for Make a booking \nEnter \"3\" to exit the program \n")
    os.system('cls')
    if choice == "1":
        #TODO: Check booking service
        print('1')
        check(username)
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
        startup_menu()

if __name__ == "__main__": # Ensure that certain code is only executed when the script is run directly
    startup_menu()
