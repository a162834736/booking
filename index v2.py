import pymysql
import os
import time
import configparser
import socket
# 连接数据库
class MysqlSearch:
    def __init__(self):
        self.conn = None
        self.get_conn()

    def get_conn(self):
        print('Connecting to database...')
        try:
            self.conn = pymysql.connect(
                host='host',
                user='user',
                passwd='passwd',
                db='db',
                connect_timeout=7
            )
        except pymysql.OperationalError as e:
            print(f"Error: {e} \nMake sure you are not connected to the school network!")
            exit(1)
        except socket.timeout:
            print("Connection attempt timed out.")
            exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)

    def close_conn(self):
        if self.conn:
            self.conn.close()

    def get_userinfo(self):
        sql = 'SELECT * FROM user'
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def insert_userinfo(self, username, password):
        sql_check = 'SELECT * FROM user WHERE username = %s'
        sql_insert = 'INSERT INTO user(username, password) VALUES(%s, %s)'
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_check, (username,))
                if cursor.fetchone():
                    print("User already exists!")
                    return

                cursor.execute(sql_insert, (username, password))
                self.conn.commit()
                print("Registration successful.")
        except pymysql.Error as e:
            self.conn.rollback()
            print(f"Error during registration: {e}")

    def get_user_booking(self, booked_user):
        sql = 'SELECT * FROM facilities_details WHERE booked_user = %s'
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (booked_user,))
            return cursor.fetchall()

    def get_available_facilities(self):
        sql = 'SELECT * FROM facilities_details WHERE availability = 1'
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def insert_booking(self, fac_id, booked_user):
        sql_update_user = 'UPDATE facilities_details SET booked_user = %s WHERE fac_id = %s'
        sql_update_availability = 'UPDATE facilities_details SET availability = 0 WHERE fac_id = %s'
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_update_user, (booked_user, fac_id))
                cursor.execute(sql_update_availability, (fac_id,))
                self.conn.commit()
                print(f"Booking successful for facility ID: {fac_id}")
        except pymysql.Error as e:
            self.conn.rollback()
            print(f"Error during booking: {e}")

    def cancel_booking(self, fac_id, booked_user):
        sql_update_availability = 'UPDATE facilities_details SET availability = 1 WHERE fac_id = %s AND booked_user = %s'
        sql_update_user = 'UPDATE facilities_details SET booked_user = NULL WHERE fac_id = %s'
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_update_availability, (fac_id,booked_user))
                cursor.execute(sql_update_user, (fac_id,))
                self.conn.commit()
                print(f"Booking cancelled for facility ID: {fac_id}")
        except pymysql.Error as e:
            self.conn.rollback()
            print(f"Error during cancellation: {e}")

# 用户交互函数
def login():
    print('Login menu:')
    db = MysqlSearch()
    result = db.get_userinfo()
    name = input("Enter your username: \n")
    pwd = input("Enter your password: \n")

    user = next((item for item in result if item['username'] == name and item['password'] == pwd), None)

    if user:
        user_username = user["username"]
        print(f"Successfully logged in to '{user_username}'. \nYou will be moved to the Main menu")
        time.sleep(2)
        main_menu(user_username)
    else:
        print("Username or password is wrong.\n You will be returned to the Start menu")
        time.sleep(2)
        startup_menu()

def register():
    print('Registration menu:')
    register_name = input("Enter a username: \n")
    register_pwd = input("Enter a password: \n")
    db = MysqlSearch()
    db.insert_userinfo(register_name, register_pwd)
    startup_menu()

def startup_menu():
    os.system('cls')
    print("Start Menu:")
    print("Enter [1] for Login Menu")
    print("Enter [2] for Registration Menu")
    print("Enter [3] to exit the program")
    choice = input()
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

def check_bookings(username):
    print('Your bookings:')
    db = MysqlSearch()
    bookings = db.get_user_booking(username)
    if bookings:
        print("Your bookings:")
        for booking in bookings:
            fac_id = booking['fac_id']
            print(f'Facility id booked: {fac_id}')
            time.sleep(0.2)
        input('Press [ENTER] to continue \n')

        cancel = input("Do you want to cancel any bookings? [Y/N]: ")
        if cancel == "Y":
            cancellation = input("Please enter the id of the facility you wish to cancel your booking for: ")
            db.cancel_booking(cancellation,username)
            print(f"You have cancelled the booking for {cancellation}. Returning to Main Menu...")
            time.sleep(3)
            main_menu(username)
        else:
            print("You will be returned to the Main menu")
            time.sleep(3)
            main_menu(username)
    else:
        print("No bookings found.\nYou will be returned to the Main menu \n")
        input('Press [ENTER] to continue \n')
        main_menu(username)

def make_booking(username):
    db = MysqlSearch()
    available_facilities = db.get_available_facilities()
    print('Available facilities:')
    for facility in available_facilities:
        fac_id = facility['fac_id']
        print(f'Facility ID: {fac_id}')

    fac_id_input = input("Enter the id of the facility you want to book: \n")

    if any(facility['fac_id'] == fac_id_input for facility in available_facilities):
        confirmation = input("Are you sure you want to book this facility? [Y/N]: \n")
        if confirmation == 'Y':
            db.insert_booking(fac_id_input, username)
            time.sleep(2)
            main_menu(username)
        else:
            print("Booking cancelled. You will be returned to the Main Menu.")
            input('Press [ENTER] to continue \n')
            main_menu(username)
    else:
        print("Booking unsuccessful: INVALID ID.\nYou will be returned to the Main menu.")
        time.sleep(2)
        main_menu(username)

def main_menu(username):
    os.system('cls')
    print(f"Welcome {username}!")
    print("Enter [1] for Check booking status")
    print("Enter [2] for Make a booking")
    print("Enter [3] to exit the program")
    choice = input()
    os.system('cls')
    if choice == "1":
        check_bookings(username)
    elif choice == "2":
        make_booking(username)
    elif choice == "3":
        print("Good-bye!")
        time.sleep(1)
        exit(1)
    else:
        print('Your input is not valid!')
        time.sleep(2)
        main_menu(username)

if __name__ == "__main__":
    startup_menu()
