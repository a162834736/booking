import MySQLdb
from tkinter import *
from tkinter import messagebox
 
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
        
        # 使用cursor()方法获取操作游标
		cursor = self.conn.cursor()
 
        # 使用execute()方法执行SQL语句
		cursor.execute(sql)
 
        # 使用fetchall()方法获取全部数据
		result = cursor.fetchall()
        
        # 将数据用字典形式存储于result
		result = [dict(zip([k[0] for k in cursor.description],row)) for row in result]
 
        # 关闭连接
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
				messagebox.showerror('Warning',message = 'Register failed.')
			elif self.a in ulist:
				messagebox.showerror('Warning',message = 'User already existed.')
			else:
				# 提交事务
				self.conn.commit()
 
				messagebox.showinfo(title = '.',message = 'Register sucessful')
			cursor.close()
			self.close_conn()
		except:
            # 限制提交
			self.conn.rollback()
 
def cancel():
	# delete the username and password user keyed in
	user.set('')
	passwd.set('')
 
# define the function for register button
def register():
	register_name = entry_user.get()
	register_pwd = entry_passwd.get()
	obj_r = MysqlSearch()
	obj_r.insert_userinfo(register_name,register_pwd)
 
def login():
	# 获取用户名和密码
	obj = MysqlSearch()
	result = obj.get_userinfo()
	name = entry_user.get()
	pwd = entry_passwd.get()
	ulist = []
	plist = []
	for item in result:
		ulist.append(item['username'])
		plist.append(item['password'])
	deter = True
	for i in range(len(ulist)):
		while True:
			if name == ulist[i] and pwd == plist[i]:
				messagebox.showinfo(title = '.',message = 'Login successfully.')# 登陆成功则执行begin函数
				deter = False
				break
			else:
				break
	while deter:
		messagebox.showerror('Warning',message='Username or password wrong.')
		break
 
 
# 创建应用程序窗口
win_login = Tk()
win_login.title('Student venue booking system')
 
# 禁止拉伸窗口
win_login.resizable(width = False, height = False)
win_login.geometry('600x300+382+183')
 
# 在窗口上创建标签组件
Label(win_login,text='Username',font = ('微软雅黑'),justify=RIGHT,width=80).place(x=190,y=50,width=95,height=40)
Label(win_login,text='Password',font = ('微软雅黑'),justify=RIGHT,width=80).place(x=190,y=100,width=95,height=40)
 
# 创建字符串变量和文本框组件，同时设置关联的变量
# 用户名
user = StringVar(win_login,value='')
entry_user = Entry(win_login,width=80,textvariable=user)
entry_user.place(x=310,y=50,width=80,height=40)
 
# 密码
passwd = StringVar(win_login,value='')
entry_passwd = Entry(win_login,show='*',width=80,textvariable=passwd)
entry_passwd.place(x=310,y=100,width=80,height=40)
 
# 按钮
Button(win_login,text='Login',font = ('微软雅黑'),command=login).place(x=150,y=150,width=80,height=50)
Button(win_login,text='Register',font = ('微软雅黑'),command=register).place(x=260,y=150,width=80,height=50)
Button(win_login,text='Cancel',font = ('微软雅黑'),command=cancel).place(x=370,y=150,width=80,height=50)
 
# 启动消息循环
win_login.mainloop()