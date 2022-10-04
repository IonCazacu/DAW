SELECT
	headline,
	message,
	mark
FROM
	user_review
WHERE
	id_user = :id_user
	AND id_movie = :id_movie;
	
UPDATE
	user_review
SET
	headline = :headline,
	message = :message,
	mark = :mark
WHERE
	id_user = :id_user
	AND id_movie = :id_movie;

INSERT INTO user_review (id_user, id_movie, headline, message, mark, send)
		VALUES(:id_user, :id_movie, :headline, :message, :mark, DATE('now'));