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
		added = DATE('now');
	
SELECT
	user_watchlist.id_movie,
	title,
	poster,
	(
		SELECT
			IFNULL(AVG(user_review.mark), 0)
		FROM
			user_review
		WHERE
			user_review.id_movie = user_watchlist.id_movie) mark
	FROM
		user_watchlist
	NATURAL JOIN movie
WHERE
	user_watchlist.id_user = :id_user;