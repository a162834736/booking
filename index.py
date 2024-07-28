'''
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
        os.system('cls')
        print('Connecting to database...')
        try:
            socket.setdefaulttimeout(7) # Set maximum attempt timeout to 7 seconds
            self.conn = pymysql.connect(
                host=config.get('database', 'host'),
                user=config.get('database', 'user'),
                passwd=config.get('database', 'passwd'),
                db=config.get('database', 'db'),
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

    # DEFINE REGISTER OUTPUT
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

    #Find user ID in facilities_details to display in bookings:
    def get_user_booking(self, booked_user):
        sql = 'SELECT * FROM facilities_details WHERE booked_user = %s'
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (booked_user,))
            result = cursor.fetchall()
            result = [dict(zip([k[0] for k in cursor.description], row)) for row in result]
        self.close_conn()
        return result
    
    # GET LIST OF AVAILABLE FACILITIES
    def get_available_facilities(self):
        sql = 'SELECT * FROM facilities_details WHERE availability = 1'
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
            result = [dict(zip([k[0] for k in cursor.description], row)) for row in result]
        self.close_conn()
        return result

    # INSERT BOOKING INTO SQL DATABASE AND UPDATE FACILITY AVAILABILITY
    def insert_booking(self, fac_id, booked_user):
        sql_update_user = 'UPDATE facilities_details SET booked_user = %s WHERE fac_id = %s'
        sql_update_availability = 'UPDATE facilities_details SET availability = 0 WHERE fac_id = %s'
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(sql_update_user, (booked_user, fac_id))
                cursor.execute(sql_update_availability, (fac_id))
                self.conn.commit()
                print(f"Booking successful for {fac_id}! \nYou will be returned to the Main menu!")
                time.sleep(2)
                main_menu(booked_user)
            except pymysql.Error as e:
                self.conn.rollback()
                print(f"\nBooking failed. \nError: {e}\nYou will be returned to the Main menu \n")
                time.sleep(2)
                main_menu(booked_user)
        self.close_conn()
        


        #TODO: WTF IS SQL_UPDATE_AVAILABILITY1 AND SQL_UPDATE_USER1 FIX THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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


#END OF FUNCTION AAAAAAAAAAAAA





# DEFINING VARIABLES TO BE OUTPUT IN STARTUP MENU
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
#TODO: UPDATE REGISTER
def register():
    print('Registration menu:')
    register_name = input("Enter a username: \n")
    register_pwd = input("Enter a password: \n")
    obj_r = MysqlSearch()
    obj_r.insert_userinfo(register_name, register_pwd)


# STARTUP MENU
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


# DEFINING NECESSARY VARIABLES TO BE OUTPUT IN MAIN MENU
# (1) VIEW BOOKINGS
def check_bookings(username):
    print('Registration menu:')
    obj_c = MysqlSearch()
    bookings = obj_c.get_user_booking(username)
    tempuser=username
    if bookings:
        print("Your bookings:")
        for booking in bookings: #TODO: WHO THE FUCK MADE THIS FOR LOOP IN SUCH A CONFUSING WAY, FOR BOOKING IN BOOKING(S)?! THAT WILL CONFUSE ANY PROGAMMERS READING THIS SHIT!!! SHIT CODE FIX THIS.
            fac_id = booking['fac_id']
            print(f'Facility id booked: {fac_id}')
            time.sleep(0.2)
        input('Press [ENTER] to continue \n')

        
       # CANCEL BOOKING FEATURE
        kylefarr = str(input("Do you want to cancel any bookings? [Y/N]: "))
        #TODO: kylefarr?! ARE YOU KIDDING ME TELL ME WHO CODED THIS MONSTROSITY, THIS IS NOT READABLE FOR A AVERAGE HUMAN PROGAMMER IF ITS ONLY REFERED TO AS CHOICE1, COMPLETELY UNPROFESSIONAL BEHAVIOUR I EXPECTED FROM A GROUP OF PAID EXPERT COMPUTER SCIENCE PROGAMMERS; UNBELIVEABLE. HAVE THIS FIXED IMMEDIETLY AND MEET ME AT MY OFFICE AT THIS INSTANCE BEFORE THIS CODE GETS PARSED AND PUSHED TO GITHUB. 
        if kylefarr=="Y":
            cancellation = str(input("Please enter the id of the facility you wish to cancel your booking for: "))


            obj_c.cancel_booking(tempuser,cancellation)

            print(f"You have cancelled the booking for {cancellation}. Returning to Main Menu...")
            time.sleep(3)
            main_menu(tempuser)
        else:
            print("You will be returned to the Main menu") 
            time.sleep(3)
            main_menu(tempuser)
            
    else:
        print("No bookings found.\nYou will be returned to the Main menu \n")
        input('Press [ENTER] to continue \n')
        main_menu(username)

# (2) MAKE A BOOKING
def make_booking(username):
    obj_m = MysqlSearch()
    result2 = obj_m.get_available_facilities() #TODO: change result2 to smtg else
    print('Available facilities:')
    #TODO: Print available facilities
    fac_id_input = str(input("Enter the id of the facility you want to book: \n"))

    
    if any(facility['fac_id'] == fac_id_input for facility in result2):
        confirmation = input("Are you sure you want to book this facility? [Y/N]: \n")
        if confirmation == 'Y':
            obj_b = MysqlSearch()
            obj_b.insert_booking(fac_id_input, username)
            
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

    print(f"Welcome {username}!:")
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
'''

if __name__ == "__main__": # Ensure that certain code is only executed when the script is run directly
    startup_menu()
