from flask import render_template, url_for, flash, redirect, request, session, abort, jsonify
from Flask_Movie import app, bcrypt
from Flask_Movie.forms import RegistrationForm, LoginForm, UpdateAccountForm, ReviewForm, RatingForm
from Flask_Movie.models import load_user
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from secrets import token_hex
from PIL import Image
from contextlib import closing
import sqlite3
import os


@app.context_processor
def inject_now():
	return {'now': datetime.utcnow()}


@app.template_filter()
def custom_split(string: str) -> list:
	return string.split(',') if string is not None else None


@app.template_filter()
def custom_date(date: str, f: str):
	formats = {'low': '%Y', 'mid': '%b %d', 'high': '%b %d, %Y'}
	return datetime.strptime(date, '%Y-%m-%d').strftime(formats[f])


def add_to_session(title: str, url: str, idx: int, poster: str):
	title_poster = dict()
	title_poster[title] = (url, idx, poster)
	
	if session.get('titles') is None:
		session['titles'] = []
	
	recently_viewed = session['titles']
	if title_poster not in recently_viewed:
		recently_viewed.append(title_poster)
	
	session['titles'] = recently_viewed


@app.route('/')
@app.route('/home')
def home():
	results, watchlist = list(), list()
	with open(f'{app.root_path}/static/sql/home.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		queries = f.read()
		query_list = queries.split(';')
		
		results = [cur.execute(query).fetchall() for query in query_list]
		
		if current_user.is_authenticated:
			watchlist = cur.execute('SELECT user_watchlist.id_movie, title, poster, (SELECT IFNULL(AVG(user_review.mark), 0) FROM \
				user_review WHERE user_review.id_movie=user_watchlist.id_movie) mark FROM user_watchlist NATURAL JOIN movie WHERE \
				user_watchlist.id_user=? LIMIT 9', (current_user.id_user,)).fetchall()
		
	return render_template('home.html', title='Movies & Shows', results=results, watchlist=watchlist)


@app.route('/about/movie/<int:id_movie>-<string:title>', methods=['GET', 'POST'])
def movie(id_movie, title):
	results, found = list(), tuple()
	with open(f'{app.root_path}/static/sql/movie.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		url_accessed_directly = cur.execute('SELECT * FROM movie WHERE id_movie=? AND title=?', (id_movie, title,)).fetchone()
		if not url_accessed_directly:
			abort(404)
		
		queries = f.read()
		query_list = queries.split(';')
		results = [cur.execute(query, {'id_movie': id_movie}).fetchall() for query in query_list]
		
		if current_user.is_authenticated:
			found = cur.execute('SELECT headline, message, mark FROM user_review WHERE id_user=? AND \
				id_movie=?', (current_user.id_user, id_movie,)).fetchone()
	
	add_to_session(title, 'movie', id_movie, results[0][0][6])
	
	form = ReviewForm()
	if form.validate_on_submit():
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			cur.execute('INSERT INTO user_review (id_user, id_movie, headline, message) \
				VALUES(?, ?, ?, ?)', (current_user.id_user, id_movie, form.headline.data, form.message.data))
			conn.commit()
		return redirect(url_for('movie', id_movie=id_movie, title=title))
	return render_template('movie.html', id_movie=id_movie, title=title, form=form, found=found, results=results)
	

@app.route('/about/person/<int:id_person>-<string:title>')
def person(id_person, title):
	results = list()
	with open(f'{app.root_path}/static/sql/person.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		url_accessed_directly = cur.execute('SELECT * FROM person WHERE id_person = ? AND name = ?', (id_person, title,)).fetchone()
		if not url_accessed_directly:
			abort(404)
			
		queries = f.read()
		query_list = queries.split(';')
		results = [cur.execute(query, {'id_person': id_person}).fetchall() for query in query_list]
	
	add_to_session(title, 'person', id_person, results[0][0][7])
	
	return render_template('person.html', id_person=id_person, title=title, results=results)
	
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			cur.execute('INSERT INTO user(username, email, password) VALUES(?, ?, ?)', (form.username.data, form.email.data, hashed_password))
			conn.commit()
		flash('Your account has been created! You are now able to log in!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		found = tuple()
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			found = cur.execute('SELECT id_user FROM user WHERE email=?', (form.email.data,)).fetchone()
		user = load_user(found[0])
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page or url_for('home'))
		else:
			flash('The email and password you entered did not match our records. Please double-check and try again.', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_image):
	_, i_ext = os.path.splitext(form_image.filename)
	image = token_hex(8) + i_ext
	image_path = os.path.join(app.root_path, 'static/profile', image)

	out_size = (125, 125)
	i = Image.open(form_image)
	i.thumbnail(out_size)
	i.save(image_path)

	return f'/static/profile/{image}'


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.image.data:
			image_file = save_picture(form.image.data)
			current_user.image = image_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			cur.execute('UPDATE user SET username=?, email=?, image=? WHERE id_user=?', (form.username.data, form.email.data, \
				current_user.image, current_user.id_user))
			conn.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form = UpdateAccountForm(username=current_user.username, email=current_user.email)
	image = url_for('static', filename=current_user.image)
	return render_template('account.html', title='Account', image=image, form=form)


@app.route('/movie/<int:id_movie>-<string:title>/trailer')
def trailer(id_movie, title):
	movie = tuple()
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		url_accessed_directly = cur.execute('SELECT * FROM movie WHERE id_movie=? AND title=?', (id_movie, title,)).fetchone()
		if not url_accessed_directly:
			abort(404)
			
		movie = cur.execute('SELECT strftime("%Y", release_date) year, overview, poster, video, GROUP_CONCAT(genre.genre, ", ") genre FROM \
			movie NATURAL JOIN movie_genre NATURAL JOIN genre WHERE id_movie=?', (id_movie,)).fetchone()
		
	return render_template('trailer.html', id_movie=id_movie, title=title, movie=movie)
	

@app.route('/feature/genre')
def feature_genre():
	genres = list()
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		genres = cur.execute('SELECT id_genre, genre, image_path FROM genre ORDER BY genre ASC').fetchall()
	
	return render_template('feature_genre.html', title='Browse Movies and Shows by Genre', genres=genres)
	

@app.route('/search/genre/<int:id_genre>-<string:genre>')
def search_genre(id_genre, genre):
	results = list()
	with open(f'{app.root_path}/static/sql/genre.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		url_accessed_directly = cur.execute('SELECT * FROM movie NATURAL JOIN movie_genre NATURAL JOIN genre WHERE genre.id_genre = ? AND \
			genre.genre = ?', (id_genre, genre,)).fetchone()
		if not url_accessed_directly:
			abort(404)
			
		queries = f.read()
		query_list = queries.split(';')
		results = [cur.execute(query, {'id_genre': id_genre, 'genre': genre}).fetchall() for query in query_list]
	
	return render_template('search_genre.html', title=genre, results=results)
	
	
# -------------------------------------------------------------------------------------------------------------------------------
	

@app.route('/watchlist/<int:id_movie>', methods=['GET', 'POST'])
@login_required
def watchlist(id_movie):
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		cur.execute('INSERT INTO user_watchlist(id_user, id_movie) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM user_watchlist WHERE \
			id_user=? AND id_movie=?)', (current_user.id_user, id_movie, current_user.id_user, id_movie))
		conn.commit()
	
	return redirect(url_for('login'))


@app.route('/watchlist/<int:id_movie>/remove', methods=['GET', 'POST'])
@login_required
def remove_from_watchlist(id_movie):
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		cur.execute('DELETE FROM user_watchlist WHERE id_user=? AND id_movie=?', (current_user.id_user, id_movie,))
		conn.commit()
		
	return redirect(url_for('home'))


@app.route('/clear_session')
def clear_session():
	session.pop('titles', None)
	
	return jsonify(success=True)
	# return redirect(url_for('home'))


# -------------------------------------------------------------------------------------------------------------------------------


@app.route('/review/<int:id_movie>-<string:title>', methods=['GET', 'POST'])
@login_required
def review(id_movie, title):
	query_list, found = list(), tuple()
	with open(f'{app.root_path}/static/sql/review.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		queries = f.read()
		query_list = queries.split(';')
		
		found = cur.execute(query_list[0], {'id_user': current_user.id_user, 'id_movie': id_movie}).fetchone()
			
	form = ReviewForm()
	if form.validate_on_submit():
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			if found:
				cur.execute(query_list[2], {'headline': form.headline.data, 'message': form.message.data, 'id_user': current_user.id_user, \
																		'id_movie': id_movie, 'mark': form.mark.data})
			else:
				cur.execute(query_list[3], {'id_user': current_user.id_user, 'id_movie': id_movie, 'headline': form.headline.data, \
																		'message': form.message.data, 'mark': form.mark.data})
			conn.commit()
		return redirect(url_for('about_movie', id_movie=id_movie, title=title))
	elif request.method == 'GET' and found:
		form = ReviewForm(mark=found[2], headline=found[0], message=found[1])
	return render_template('review.html', id_movie=id_movie, title=title, form=form)
	

@app.route('/what-to-watch/<string:body>')
def movies(body):
	
	if not [it for it in ['added-today', 'from-your-watchlist'] if it == body]:
		abort(400)
	
	query_list_idx = {'added-today': (0, 'Added today'), 'from-your-watchlist': (1, 'From your Watchlist')}
										
	if query_list_idx[body][0] == 1 and not current_user.is_authenticated:
		return redirect(url_for('login'))
				
	result = list()
	with open(f'{app.root_path}/static/sql/movies.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		queries = f.read()
		query_list = queries.split(';')
		
		if query_list_idx[body][0] == 1:
			result = cur.execute(query_list[query_list_idx[body][0]], {'id_user': current_user.id_user}).fetchall()
		else:
			result = cur.execute(query_list[query_list_idx[body][0]]).fetchall()
	
	return render_template('movies.html', title='Pick What to Watch', result=result)


@app.route('/more-to-discover/famous-birthdays')
def persons():
	
	result = list()	
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		
		result = cur.execute('SELECT id_person, name, known_for_department, profile_path FROM person WHERE \
			strftime ("%m-%d", birthday) = strftime ("%m-%d", DATE("now"))').fetchall()
	
	return render_template('persons.html', title='Famous Birthdays', result=result)
	
	
@app.route('/movie/<int:id_movie>-<string:title>/reviews', methods=['GET', 'POST'])
def reviews(id_movie, title):
	reviews, movie, found = list(), tuple(), tuple()
	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		reviews = cur.execute('SELECT user.username, user.image, headline, message, mark, send FROM user_review NATURAL JOIN user NATURAL JOIN \
			movie WHERE user_review.id_movie=?', (id_movie,)).fetchall()
		
		movie = cur.execute('SELECT strftime("%Y", movie.release_date) year, movie.poster FROM movie WHERE id_movie=?', (id_movie,)).fetchone()
		
		if current_user.is_authenticated:
			found = cur.execute('SELECT headline, message, mark FROM user_review WHERE id_user=? AND \
				id_movie=?', (current_user.id_user, id_movie)).fetchone()
	
	add_to_session(title, 'movie', id_movie, movie[1])

	form = ReviewForm()
	if form.validate_on_submit():
		with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
			cur.execute('INSERT INTO user_review (id_user, id_movie, headline, message) \
				VALUES(?, ?, ?, ?)', (current_user.id_user, id_movie, form.headline.data, form.message.data))
			conn.commit()
		return redirect(url_for('reviews', id_movie=id_movie, title=title))
	return render_template('reviews.html', id_movie=id_movie, title=title, form=form, found=found, movie=movie, reviews=reviews)
	

# @app.route('/movie/<int:id_movie>-<string:title>/cast_and_crew')
# def cast_and_crew(id_movie, title):
# 	casts = list()
# 	with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
# 		casts = cur.execute('SELECT GROUP_CONCAT(DISTINCT id_person), GROUP_CONCAT(DISTINCT name), GROUP_CONCAT(DISTINCT profile_path), \
# 			GROUP_CONCAT(DISTINCT CJ) CJ, department FROM (SELECT id_person, name, profile_path, movie_cast.character AS CJ, \
# 			department.department AS department FROM person NATURAL JOIN movie_cast NATURAL JOIN movie NATURAL JOIN department WHERE \
# 			movie.id_movie = ? UNION ALL SELECT id_person, name, profile_path, movie_crew.job AS CJ, department.department AS department \
# 			FROM person NATURAL JOIN movie_crew NATURAL JOIN movie NATURAL JOIN department WHERE movie.id_movie = ?) GROUP BY \
# 			department', (id_movie, id_movie)).fetchall()
	
# 	return render_template('cast_and_crew.html', id_movie=id_movie, title=title, casts=casts)


# -------------------------------------------------------------------------------------------------------------------------------
	

@app.route('/user/<int:id_user>/profile')
@login_required
def user(id_user):
	results = list()
	with open(f'{app.root_path}/static/sql/user.sql') as f, closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
		queries = f.read()
		query_list = queries.split(';')
		
		results = [cur.execute(query, {'id_user': current_user.id_user}).fetchall() for query in query_list]
	
	return render_template('user.html', title=f"{current_user.username}'s Profile", results=results, data=[21, 7, 312, 123, 20])