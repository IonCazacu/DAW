SELECT
	gender.gender,
	known_for_department,
	biography,
	birthday,
	deathday,
	(strftime ('%Y',
			IFNULL(deathday, 'now')) - strftime ('%Y',
			birthday)) - (strftime ('%m-%d',
			IFNULL(deathday, 'now')) < strftime ('%m-%d',
			birthday)) AS age,
	place_of_birth,
	profile_path
FROM
	person
	NATURAL JOIN gender
WHERE
	id_person = :id_person
LIMIT 1;
	
SELECT
	id_movie,
	title,
	year,
	poster,
	GROUP_CONCAT(cj) AS who,
	id_person
FROM (
	SELECT
		m1.id_movie,
		m1.title,
		strftime ('%Y',
			m1.release_date) AS year,
		m1.poster,
		mc.character AS cj,
		p.id_person
	FROM
		movie m1
	NATURAL JOIN movie_cast mc
	NATURAL JOIN person p
UNION ALL
SELECT
	m2.id_movie,
	m2.title,
	strftime ('%Y',
		m2.release_date) AS year,
	m2.poster,
	mc.job AS cj,
	p.id_person
FROM
	movie m2
	NATURAL JOIN movie_crew mc
	NATURAL JOIN person p) sub
WHERE
	sub.id_person = :id_person
GROUP BY
	title;