from datetime import datetime
from Flask_Movie import login_manager
from flask_login import UserMixin
from contextlib import closing
import sqlite3


class User(UserMixin):
	def __init__(self, id_user, username, email, password, created, image):
		super(User, self).__init__()
		self.id_user = id_user
		self.username = username
		self.email = email
		self.password = password
		self.created = created
		self.image = image
		self.authenticated = False
		 
	def is_active(self):
		 return self.is_active()
	
	def is_anonymous(self):
		 return False
	
	def is_authenticated(self):
		 return self.authenticated
	
	def is_active(self):
		 return True
	
	def get_id(self):
		 return self.id_user
		 

@login_manager.user_loader
def load_user(id_user):
	user = tuple()
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		user = cur.execute('SELECT * FROM user WHERE id_user=?', (id_user,)).fetchone()
	if user is None:
		return None
	return User(int(user[0]), user[2], user[3], user[4], user[6], user[7])