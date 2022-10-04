from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from Flask_Movie.models import User
from contextlib import closing
import sqlite3


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=8, max=20), Regexp(regex=r'^[a-zA-Z][a-zA-Z0-9_]{8,20}$', message='Username must start with letters {a-zA-Z} followed up by alphabets, numbers or an underscore')])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	
	def validate_username(self, username):
		user = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			user = cur.execute('SELECT username FROM user WHERE username=?', (username.data,)).fetchone()
		if user:
			raise ValidationError('That username is taken. Please choose a different one')
	
	def validate_email(self, email):
		user = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			user = cur.execute('SELECT email FROM user WHERE email=?', (email.data,)).fetchone()
		if user:
			raise ValidationError('That email is taken. Please choose a different one')
	
	
class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Sign In')
	
	def validate_email(self, email):
		user = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			user = cur.execute('SELECT email FROM user WHERE email=?', (email.data,)).fetchone()
		if user is None:
			raise ValidationError('Could not find your Spacebox Account')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=8, max=20), Regexp(regex=r'^[a-zA-Z][a-zA-Z0-9_]{8,20}$', message='Username must start with letters {a-zA-Z} followed up by alphabets, numbers or an underscore')])
	email = StringField('Email', validators=[DataRequired(), Email()])
	image = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
	submit = SubmitField('Update')
	
	def validate_username(self, username):
		if username.data != current_user.username:
			user = tuple()
			with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
				user = cur.execute('SELECT username FROM user WHERE username=?', (username.data,)).fetchone()
			if user:
				raise ValidationError('That username is taken. Please choose a different one')
	
	def validate_email(self, email):
		if email.data != current_user.email:
			user = tuple()
			with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
				user = cur.execute('SELECT email FROM user WHERE email=?', (email.data,)).fetchone()
			if user:
				raise ValidationError('That email is taken. Please choose a different one')


class ReviewForm(FlaskForm):
	headline = StringField(validators=[DataRequired(), Length(min=20, max=60)])
	message = TextAreaField(validators=[DataRequired(), Length(min=300, max=600)])
	submit = SubmitField('Submit')
	
	def validate_headline(self, headline):
		found = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			found = cur.execute('SELECT headline FROM user_review WHERE headline=?', (headline.data,)).fetchone()
		if found:
			raise ValidationError('Plagiarised headline. Please rephrase your headline')
	
	def validate_message(self, message):
		found = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			found = cur.execute('SELECT message FROM user_review WHERE message=?', (message.data,)).fetchone()
		if found:
			raise ValidationError('Plagiarised message. Please rephrase your message')
			

class RatingForm(FlaskForm):
	mark = RadioField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])
	submit = SubmitField('Submit')