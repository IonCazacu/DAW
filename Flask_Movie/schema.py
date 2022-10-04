from contextlib import closing
import sqlite3


with closing(sqlite3.connect('site.db')) as conn, closing(conn.cursor()) as cur:
	cur.executescript('''
		CREATE TABLE IF NOT EXISTS user (
		id_user INTEGER PRIMARY KEY AUTOINCREMENT,
		id_gender INTEGER,
		username VARCHAR(20) NOT NULL UNIQUE,
		email VARCHAR(130) NOT NULL UNIQUE,
		password VARCHAR(256) NOT NULL,
		date_of_birth DATE,
		created DATE NOT NULL DEFAULT (DATE('now')),
		image VARCHAR(100) NOT NULL DEFAULT '/static/profile/None.jpg',
		admin INTEGER(1) NOT NULL DEFAULT 0,
		blocked INTEGER(1) NOT NULL DEFAULT 0,
		online INTEGER(1) NOT NULL DEFAULT 0,
		FOREIGN KEY(id_gender) REFERENCES gender(id_gender)
		);
		
		CREATE TABLE IF NOT EXISTS user_watchlist (
		id_user INTEGER NOT NULL,
		id_movie INTEGER NOT NULL,
		FOREIGN KEY(id_user) REFERENCES user(id_user),
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie)
		);

		CREATE TABLE IF NOT EXISTS user_review (
		id_user INTEGER NOT NULL,
		id_movie INTEGER NOT NULL,
		headline VARCHAR(60) UNIQUE,
		message TEXT UNIQUE,
		mark INTEGER,
		send DATE DEFAULT (DATE('now'))
		FOREIGN KEY(id_user) REFERENCES user(id_user),
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie)
		);
		
		CREATE TABLE IF NOT EXISTS gender (
		id_gender INTEGER PRIMARY KEY AUTOINCREMENT,
		gender VARCHAR(6) NOT NULL UNIQUE
		);
		
		CREATE TABLE IF NOT EXISTS person (
		id_person INTEGER PRIMARY KEY AUTOINCREMENT,
		id_gender INTEGER NOT NULL,
		name VARCHAR(130) NOT NULL UNIQUE,
		known_for_department VARCHAR(30),
		biography TEXT,
		birthday DATE,
		deathday DATE,
		place_of_birth VARCHAR(100),
		profile_path VARCHAR(30),
		FOREIGN KEY(id_gender) REFERENCES gender(id_gender)
		);
		
		CREATE TABLE IF NOT EXISTS department (
		id_department INTEGER PRIMARY KEY AUTOINCREMENT,
		department VARCHAR(30) NOT NULL UNIQUE
		);
		
		CREATE TABLE IF NOT EXISTS movie_cast (
		id_movie INTEGER NOT NULL,
		id_person INTEGER NOT NULL,
		id_department INTEGER NOT NULL,
		character VARCHAR(130) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(id_person) REFERENCES person(id_person),
		FOREIGN KEY(id_department) REFERENCES department(id_department)
		);
		
		CREATE TABLE IF NOT EXISTS movie_crew (
		id_movie INTEGER NOT NULL,
		id_person INTEGER NOT NULL,
		id_department INTEGER NOT NULL,
		job VARCHAR(130) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(id_person) REFERENCES person(id_person),
		FOREIGN KEY(id_department) REFERENCES department(id_department)
		);
		
		CREATE TABLE IF NOT EXISTS images (
		id_image INTEGER PRIMARY KEY AUTOINCREMENT,
		id_movie INTEGER NOT NULL,
		image VARCHAR(30) NOT NULL,
		title VARCHAR(130) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie)
		);
		
		CREATE TABLE IF NOT EXISTS videos (
		id_image INTEGER PRIMARY KEY AUTOINCREMENT,
		id_movie INTEGER NOT NULL,
		video VARCHAR(30) NOT NULL,
		title VARCHAR(130) NOT NULL,
		video_time VARCHAR(10) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie)
		);
		
		CREATE TABLE IF NOT EXISTS movie (
		id_movie INTEGER PRIMARY KEY AUTOINCREMENT,
		title VARCHAR(130) NOT NULL UNIQUE,
		release_date DATE NOT NULL,
		runtime VARCHAR(6) NOT NULL,
		overview TEXT NOT NULL,
		tagline TEXT NOT NULL,
		budget INTEGER NOT NULL,
		revenue INTEGER NOT NULL,
		status VARCHAR(30) NOT NULL,
		poster VARCHAR(30) NOT NULL,
		backdrop VARCHAR(30) NOT NULL,
		video VARCHAR(30),
		added DATE NOT NULL DEFAULT (DATE('now')),
		active INTEGER(1) NOT NULL DEFAULT 0
		);
		
		CREATE TABLE IF NOT EXISTS genre (
		id_genre INTEGER PRIMARY KEY AUTOINCREMENT,
		genre VARCHAR(30) NOT NULL UNIQUE,
		image_path VARCHAR(30)
		);
		
		CREATE TABLE IF NOT EXISTS movie_genre (
		id_movie INTEGER NOT NULL,
		id_genre INTEGER NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(id_genre) REFERENCES genre(id_genre)
		);
		
		CREATE TABLE IF NOT EXISTS language (
		language_code VARCHAR(10) PRIMARY KEY,
		language VARCHAR(30) NOT NULL UNIQUE
		);
		
		CREATE TABLE IF NOT EXISTS movie_language (
		id_movie INTEGER NOT NULL,
		language_code VARCHAR(10) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(language_code) REFERENCES language(language_code)
		);
		
		CREATE TABLE IF NOT EXISTS company (
		id_company INTEGER PRIMARY KEY AUTOINCREMENT,
		company VARCHAR(30) NOT NULL UNIQUE
		);
		
		CREATE TABLE IF NOT EXISTS movie_company (
		id_movie INTEGER NOT NULL,
		id_company INTEGER NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(id_company) REFERENCES company(id_company)
		);
		
		CREATE TABLE IF NOT EXISTS country (
		country_code VARCHAR(10) PRIMARY KEY,
		country VARCHAR(30) NOT NULL UNIQUE
		);
		
		CREATE TABLE IF NOT EXISTS movie_country (
		id_movie INTEGER NOT NULL,
		country_code VARCHAR(10) NOT NULL,
		FOREIGN KEY(id_movie) REFERENCES movie(id_movie),
		FOREIGN KEY(country_code) REFERENCES country(country_code)
		);
	''')
	conn.commit()