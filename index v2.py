import pymysql
import os
import time
import configparser
import socket

'''
startup_menu() = startup men
login() = login function
register() = register function
check_bookings() = view available bookings
make_booking() = make a booking
cancel_booking() = cancel a booking


'''

# Read configuration file for SQL host, user, password, database.
config = configparser.ConfigParser()
config.read('config.ini')

# Using class to provide more modularity to the code.
# Most of this code here is to connect and compare to the database.

class MysqlSearch:
    # If initialized, will attempt to connect to Database
    def __init__(self):
        self.conn = None
        self.get_conn()


    def get_conn(self):
        print('Connecting to database...')
        try:

            socket.setdefaulttimeout(7)

            self.conn = pymysql.connect(
                host=config.get('database', 'host'),
                user=config.get('database', 'user'),
                password=config.get('database', 'passwd'),
                database=config.get('database', 'db'),
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
        
    def get_studentinfo(self, username):
        sql = 'SELECT stu_name FROM students WHERE stu_id = %s' 
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, (username,))
                fetched_StuName = cursor.fetchall()
                if fetched_StuName:
                    fetched_StuName = fetched_StuName[0]['stu_name']
                    return(fetched_StuName)
                else:
                    return(username)
        
        except pymysql.Error :
            self.conn.rollback()

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
                input('Press [ENTER] to continue to the Main Menu\n')
                main_menu(booked_user)
        except pymysql.Error as e:
            self.conn.rollback()
            print(f"Error during cancellation: {e}")
# End of class MysqlSearch

# User inserts their Student ID and Password
# It will be compared against the database
# If both is correct then user will be logged in and redirected to Main Menu
# If either is wrong, user will be redirected back to the Startup page.

def login():
    print('Login menu:')
    db = MysqlSearch()
    result = db.get_userinfo()
    name = input("Enter your Student ID: \n")
    pwd = input("Enter your password: \n")

    user = next((item for item in result if item['username'] == name and item['password'] == pwd), None)

    if user:
        
        user_username = user["username"]
        StuName = db.get_studentinfo(user_username)
        
        print(f"Successfully logged in to '{StuName}'. \nYou will be moved to the Main menu")
        time.sleep(2)
        main_menu(StuName)
    else:
        print("Username or password is wrong.\n You will be returned to the Start menu")
        time.sleep(2)
        startup_menu()

def register():
    print('Registration menu:')
    register_name = input("Enter your Student ID: \n")
    register_pwd = input("Enter a password: \n")
    db = MysqlSearch()
    db.insert_userinfo(register_name, register_pwd)
    startup_menu()

# Check Booking users existing booking and lists them
# From their bookings user will be given a choice to cancel their booking using the Facility ID
# If user keys in a Facility ID they that isnt their booking, cancellation will not proceed.

def check_bookings(username):
    print('Your bookings:')
    db = MysqlSearch()
    bookings = db.get_user_booking(username)
    if bookings:
        print("Your bookings:")
        fac_list = []
        for booking in bookings:
            fac_id = booking['fac_id']
            print(f'Facility id booked: {fac_id}')
            time.sleep(0.2)
            fac_list.append(fac_id)
        input('Press [ENTER] to continue \n')

        cancel = input("Do you want to cancel any bookings? [Y/N]: ").upper()
        if cancel == "Y":
            cancellation = input("Please enter the id of the facility you wish to cancel your booking for: ")
            if cancellation in fac_list:
                db.cancel_booking(cancellation,username)
                print(f"You have cancelled the booking for {cancellation}. \nYou will be returned to the Main menu...")
                time.sleep(2)
                main_menu(username)
            else:
                print("The facility id you entered dosen\'t seem valid. \n You will be returned to Main Menu...")
                time.sleep(3)
                main_menu(username)
        else:
            print("You will be returned to the Main menu")
            time.sleep(2)
            main_menu(username)
    else:
        print("No bookings found. \nYou will be returned to the Main menu...")
        input('Press [ENTER] to continue \n')
        main_menu(username)

# Lists out all available facilities
# User selects an available facility from the list
# If facility is not available, user will not be able to book facility
# After user confirms booking, database will be updated.

def make_booking(username):
    db = MysqlSearch()
    available_facilities = db.get_available_facilities()
    print('Available facilities:')
    for facility in available_facilities:
        fac_id = facility['fac_id']
        fac_type = facility['fac_type']
        fac_floor = facility['fac_floor']
        fac_capacity = facility['fac_capacity']

        # This print function will equally space out each column so that it is alot more neater for users to actually see and easily compare.
        print(f'Facility ID: {fac_id:>10},  Facility type: {fac_type:<10},  Facility floor: {fac_floor:>2},  Facility capacity: {fac_capacity:>3}')
        time.sleep(0.2)

    fac_id_input = input("Enter the id of the facility you want to book: \n")

    if any(facility['fac_id'] == fac_id_input for facility in available_facilities):
        confirmation = input("Are you sure you want to book this facility? [Y/N]: \n").upper()
        if confirmation == 'Y':
            db.insert_booking(fac_id_input, username)
            print("Booking Successful!")
            input('Press [ENTER] to continue to the Main Menu\n')
            main_menu(username)
        else:
            print("Booking process cancelled!")
            input('Press [ENTER] to continue to the Main Menu\n')
            main_menu(username)
    else:
        print("Booking unsuccessful: INVALID ID.")
        input('Press [ENTER] to continue to the Main Menu\n')
        main_menu(username)

# Prints the Start Menu
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

# Prints the Main Menu
def main_menu(username):
    os.system('cls')
    print(f"Welcome {username}!")
    print("Enter [1] to Check your bookings")
    print("Enter [2] to Make a booking")
    print("Enter [3] to Exit the program")

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


# All this line of code does is check if it is being ran as a script and not a module and runs the startup menu :)
if __name__ == "__main__":
    startup_menu()
