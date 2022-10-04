SELECT
	id_movie,
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
	NATURAL JOIN movie_genre
	NATURAL JOIN genre
WHERE
	genre.id_genre = :id_genre
	AND genre.genre = :genre;

SELECT
	id_genre,
	genre,
	COUNT(movie_genre.id_movie)
FROM
	genre
	NATURAL JOIN movie_genre
GROUP BY
	genre;