from bs4 import BeautifulSoup
from requests import Session, get
import cchardet
import lxml
from contextlib import closing
import sqlite3
from tmdbv3api import TMDb, Movie, Person


tmdb = TMDb()
tmdb.api_key = '7811c9fef18ab7043deb7c975270c28c'
tmdb.debug = True

tmdb_img_w1280 = 'https://image.tmdb.org/t/p/w1280'
tmdb_img_w342 = 'https://image.tmdb.org/t/p/w342'
tmdb_img_w185 = 'https://image.tmdb.org/t/p/w185'
youtube_url = 'https://www.youtube.com/watch?v='

movie = Movie()
# popular = movie.popular(1)  # 10
# popular_details = [movie.details(_.id) for _ in popular]


def catch(func, handle=lambda e: e, *args, **kwargs):
	try:
		return func(*args, **kwargs)
	except Exception as e:
		print(e)
		return handle(e)


def save_image(image_url: str, folder: str, idx: int):
	image_data = get(image_url).content
	with open(f'/Users/cazacuion/Desktop/flasker/flaskmovie/static/{folder}/{idx}.jpg', 'wb') as handler:
		handler.write(image_data)
		

def insert_movie(movie: dict):
	
	with closing(sqlite3.connect('/Users/cazacuion/Desktop/flasker/site.db')) as conn, closing(conn.cursor()) as cur:
			
		cur.execute('INSERT INTO movie(id_movie, title, release_date, runtime, overview, budget, revenue, status, poster, backdrop, \
			video) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (movie.id, movie.title, movie.release_date, movie.runtime, movie.overview, \
				movie.budget, movie.revenue, movie.status, f'/static/posters/{movie.id}.jpg', f'/static/backdrops/{movie.id}.jpg', \
				movie.trailers.youtube[0].source))
		
		save_image(tmdb_img_w342 + movie.poster_path, 'posters', movie.id)
		save_image(tmdb_img_w1280 + movie.backdrop_path, 'backdrops', movie.id)
		
		[cur.execute('INSERT OR IGNORE INTO company(id_company, company) VALUES(?, ?)', (it.id, it.name)) for it in \
		movie.production_companies]
		
		[cur.execute('INSERT INTO movie_company(id_movie, id_company) VALUES(?, ?)', (movie.id, it.id)) for it in \
		movie.production_companies]
		
		[cur.execute('INSERT OR IGNORE INTO country(country_code, country) VALUES(?, ?)', (it.iso_3166_1, it.name)) for it in \
		movie.production_countries]
		
		[cur.execute('INSERT INTO movie_country(id_movie, country_code) VALUES(?, ?)', (movie.id, it.iso_3166_1)) for it in \
		movie.production_countries]
		
		[cur.execute('INSERT OR IGNORE INTO language(language_code, language) VALUES(?, ?)', (it.iso_639_1, it.english_name)) for it in \
		movie.spoken_languages]
		
		[cur.execute('INSERT INTO movie_language(id_movie, language_code) VALUES(?, ?)', (movie.id, it.iso_639_1)) for it in \
		movie.spoken_languages]
		
		[cur.execute('INSERT INTO movie_genre(id_movie, id_genre) VALUES(?, (SELECT id_genre FROM genre WHERE genre=(?)))', (movie.id, \
			it.name)) for it in movie.genres]
		
		[cur.execute('INSERT OR IGNORE INTO keyword(id_keyword, keyword) VALUES(?, ?)', (it.id, it.name)) for it in \
		movie.keywords.keywords]
		
		[cur.execute('INSERT INTO movie_keyword(id_movie, id_keyword) VALUES(?, ?)', (movie.id, it.id)) for it in \
		movie.keywords.keywords]
		
		p = Person()
		movie_cast = [p.details(it.id) for it in movie.casts.cast]
		movie_crew = [p.details(it.id) for it in movie.casts.crew]
		movie_cast.extend(movie_crew)
		
		[cur.execute('INSERT OR IGNORE INTO person(id_person, id_gender, name, known_for_department, biography, birthday, deathday, \
			place_of_birth, profile_path) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (it.id, it.gender, it.name, it.known_for_department, \
				it.biography, it.birthday, it.deathday, it.place_of_birth, \
				f'/static/persons/{it.id if it.profile_path is not None else "None"}.jpg')) for it in movie_cast]
		
		[save_image(tmdb_img_w185 + it.profile_path, 'persons', it.id) for it in movie_cast if it.profile_path is not None]
		
		[cur.execute('INSERT INTO movie_cast(id_movie, id_person, id_department, character) VALUES(?, ?, (SELECT id_department FROM \
			department WHERE department=(?)), ?)', (movie.id, it.id, it.known_for_department, it.character)) for it in movie.casts.cast]
		
		[cur.execute('INSERT INTO movie_crew(id_movie, id_person, id_department, job) VALUES(?, ?, (SELECT id_department FROM \
			department WHERE department=(?)), ?)', (movie.id, it.id, it.known_for_department, it.job)) for it in movie.casts.crew]
		
		conn.commit()

		
# [catch(lambda : insert_movie(movie)) for movie in popular_details]

f = movie.search('See How They Run')
d = movie.details(f[0].id)

catch(lambda : insert_movie(d))