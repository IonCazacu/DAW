SELECT
	user_watchlist.id_movie,
	title,
	poster
	FROM
		movie
	NATURAL JOIN user_watchlist
WHERE
	user_watchlist.id_user = :id_user
LIMIT 4;

SELECT
	id_movie,
	title,
	poster,
	mark
FROM
	movie
	NATURAL JOIN user_review
WHERE
	user_review.id_user = :id_user AND mark IS NOT NULL
LIMIT 4;