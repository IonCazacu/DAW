SELECT
	release_date,
	runtime,
	overview,
	budget,
	revenue,
	status,
	poster,
	backdrop,
	video,
	GROUP_CONCAT(DISTINCT genre.genre) genre,
	GROUP_CONCAT(DISTINCT images.image) image,
	(
		SELECT
			GROUP_CONCAT(company.company, ', ')
		FROM
			company
		NATURAL JOIN movie_company
	WHERE
		movie_company.id_movie = movie.id_movie) company, (
		SELECT
			GROUP_CONCAT(country.country, ', ')
		FROM
			country
		NATURAL JOIN movie_country
	WHERE
		movie_country.id_movie = movie.id_movie) country, (
		SELECT
			GROUP_CONCAT(language.language, ', ')
		FROM
			language
		NATURAL JOIN movie_language
	WHERE
		movie_language.id_movie = movie.id_movie)
	language, (
		SELECT
			GROUP_CONCAT(keyword.keyword)
		FROM
			keyword
		NATURAL JOIN movie_keyword
	WHERE
		movie_keyword.id_movie = movie.id_movie) keyword, (
		SELECT
			IFNULL(AVG(user_review.mark), 0)
		FROM
			user_review
		WHERE
			user_review.id_movie = movie.id_movie) mark, (
			SELECT
				COUNT(user_review.id_movie)
			FROM
				user_review
			WHERE
				user_review.id_movie = movie.id_movie
				AND user_review.mark IS NOT NULL) ratings
		FROM
			movie
		NATURAL JOIN movie_genre
		NATURAL JOIN genre
		NATURAL JOIN images
	WHERE
		id_movie = :id_movie
	LIMIT 1;

SELECT
	user.username,
	user.image,
	headline,
	message,
	mark,
	send
FROM
	user_review
	NATURAL JOIN user
WHERE
	user_review.id_movie = :id_movie
ORDER BY random()
LIMIT 1;

SELECT
	id_person,
	name,
	movie_crew.job,
	profile_path
FROM
	person
	NATURAL JOIN movie_crew
WHERE
	movie_crew.id_movie = :id_movie
	AND movie_crew.job == 'Director';
	
SELECT
	id_person,
	name,
	movie_crew.job,
	profile_path
FROM
	person
	NATURAL JOIN movie_crew
WHERE
	movie_crew.id_movie = :id_movie
	AND movie_crew.job == 'Writer';
	
SELECT
	id_person,
	name,
	movie_cast.character,
	profile_path
FROM
	person
	NATURAL JOIN movie_cast
WHERE
	movie_cast.id_movie = :id_movie
LIMIT 9;

SELECT
	movie.id_movie,
	title,
	(
		SELECT
			IFNULL(AVG(user_review.mark), 0)
		FROM
			user_review
		WHERE
			user_review.id_movie = movie.id_movie) mark
	FROM
		movie
	WHERE
		active = 1;
		
SELECT
	id_movie,
	title,
	release_date,
	(
		SELECT
			IFNULL(AVG(user_review.mark), 0)
		FROM
			user_review
		WHERE
			user_review.id_movie = movie.id_movie) mark
	FROM
		movie
	WHERE
		strftime ('%Y', release_date) = strftime ('%Y', DATE('now', 'localtime'))
		AND strftime ('%m-%d', release_date) >= strftime ('%m-%d', DATE('now', 'localtime'))
	ORDER BY
		release_date
	LIMIT 5;