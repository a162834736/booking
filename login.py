import MySQLdb
import os
import time
os.system('cls')

# connect to the database
class MysqlSearch(object):
	def __init__(self):
		self.get_conn()
 
	# get connection
	def get_conn(self):
		try:
			self.conn = MySQLdb.connect(
				host='45.76.177.52',
				user='root',
				passwd='ausmat',
				db='ausmat',
				charset='utf8'
				)
		except MySQLdb.Error as e:
			print('Error: %s' % e)
	
	# close connection
	def close_conn(self):
		try:
			if self.conn:
				self.conn.close()
		except MySQLdb.Error as e:
			print('Error: %s' % e)
 
	# get user info
	def get_userinfo(self):
		sql = 'SELECT * FROM user'
        
        # Use the cursor() method to get the operation cursor
		cursor = self.conn.cursor()
 
        # Execute SQL statements using the execute() method
		cursor.execute(sql)
 
        # Use the fetchall() method to get all data
		result = cursor.fetchall()
        
        # Store the data in result in dictionary form
		result = [dict(zip([k[0] for k in cursor.description],row)) for row in result]
 
        # Close the connection
		cursor.close()
		self.close_conn()
		return result
 
	# register
	def insert_userinfo(self,a,b):
		
		self.a = a
		self.b = b
		
		sql = 'SELECT * FROM user'
		cursor = self.conn.cursor()
		cursor.execute(sql)
		result = cursor.fetchall()
		result = [dict(zip([k[0] for k in cursor.description],row)) for row in result]
		ulist = []

		for item in result:
			ulist.append(item['username'])
		
		try:
			# sql = 'INSERT INTO user(username,password) VALUES(%s,%s)'
			cursor = self.conn.cursor()
			cursor.execute('INSERT INTO user(username,password) VALUES(%s,%s)',(self.a,self.b))
			if self.a == '' or self.b == '':
				self.conn.rollback()
				print("Registration failed. You will be returned to the main menu \n")
				time.sleep(1)
				start()

			elif self.a in ulist:
				print("User already exists! \n")
				time.sleep(0.3)
				print("You will be returned to the main menu \n")
				time.sleep(1)
				start()

			else:
				# Commit transaction
				self.conn.commit()
 
				print("Registration sucessfully.You will be returned to the main menu \n")
				time.sleep(1)
				start()
                
			cursor.close()
			self.close_conn()
		except:
            # Limit submission
			self.conn.rollback()
 
def cancel():
	# delete the username and password user keyed in
	name.set('')
	pwd.set('')
 
# define the function for register button
def register():
	register_name = input("Enter a username: \n")
	register_pwd = input("Enter a password: \n")
	obj_r = MysqlSearch()
	obj_r.insert_userinfo(register_name,register_pwd)
 
def login():
	# Get Username and Password	
	obj = MysqlSearch()
	result = obj.get_userinfo()
	name = input("Enter your username: \n")
	pwd = input("Enter your password: \n")
	ulist = []
	plist = []
	for item in result:
		ulist.append(item['username'])
		plist.append(item['password'])
	deter = True

	for i in range(len(ulist)):
		while True:
			if name == ulist[i] and pwd == plist[i]:
				print("Login successfully.")# If the login is successful, the begin function will be executed
				deter = False
				break
			else:
				break
	while deter:
		print("Username or password wrong.")
		time.sleep(0.3)
		print("Will back to main menu in 1 second.")
		time.sleep(1)
		start()


def start():
    print("Main Menu: \nEnter \"1\" for Login Menu \nEnter \"2\" for Registration Menu") 
    aa=int(input())
    if aa==1:
        login()
    elif aa==2:

        register()
start()