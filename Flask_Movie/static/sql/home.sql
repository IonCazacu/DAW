SELECT
	movie.id_movie,
	title,
	backdrop
	FROM
		movie
	WHERE
		active = 1;
	
SELECT
	movie.id_movie,
	title,
	poster,
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
		added == DATE('now', 'localtime')
	LIMIT 9;

SELECT
	id_movie,
	title,
	release_date,
	video
FROM
	movie
WHERE
	strftime ('%Y', release_date) = strftime ('%Y', DATE('now', 'localtime'))
	AND strftime ('%m-%d', release_date) >= strftime ('%m-%d', DATE('now', 'localtime'));
	
SELECT
	id_person,
	name,
	(strftime ('%Y',
			'now') - strftime ('%Y',
			birthday)) - (strftime ('%m-%d',
			'now') < strftime ('%m-%d',
			birthday))
	age,
	strftime ('%Y',
		birthday) birth_year,
	strftime ('%Y',
		deathday) death_year,
	profile_path
FROM
	person
WHERE
	strftime ('%m-%d', birthday) = strftime ('%m-%d', DATE('now', 'localtime'))
LIMIT 9;

SELECT
	id_movie,
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
		mark >= 0
	ORDER BY
		mark DESC
	LIMIT 10;