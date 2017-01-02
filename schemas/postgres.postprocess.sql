-- enrich people table with birthdays and deceased dates
-- 

-- 
-- add columns
-- 
ALTER TABLE people ADD COLUMN born text;
ALTER TABLE people ADD COLUMN died text;

-- 
-- populate born
-- 
UPDATE people p 
SET born = b.biography_date 
FROM biographies b 
WHERE p.idpeople = b.idpeople AND biography_type = 'born';

-- 
-- populate died
-- 
UPDATE people p 
SET died = b.biography_date 
FROM biographies b 
WHERE p.idpeople = b.idpeople AND biography_type = 'died';




-- enrich people_x_productions table with age at time of production
-- 

-- 
-- add column
-- 
ALTER TABLE people_x_productions ADD COLUMN age_at_production integer;

-- 
-- populate age_at_production
-- 
UPDATE people_x_productions x1 
SET age_at_production = (
	SELECT (
		CASE 
		WHEN (pr.year::integer - pe.born::integer) < 0 THEN NULL 
		WHEN (pr.year::integer - pe.born::integer) > 120 THEN NULL 
		ELSE (pr.year::integer - pe.born::integer) 
		END) AS age_at_production 
	FROM people_x_productions x2 
	LEFT JOIN people pe ON x2.idpeople = pe.idpeople 
	LEFT JOIN productions pr ON x2.idproductions =  pr.idproductions
	WHERE x1.idpeople_x_productions = x2.idpeople_x_productions
);




-- enrich productions table with ratings and business data
-- 

-- 
-- add columns
-- 
ALTER TABLE productions ADD COLUMN rating double precision;
ALTER TABLE productions ADD COLUMN votes integer;
ALTER TABLE productions ADD COLUMN budget bigint;
ALTER TABLE productions ADD COLUMN box_office_gross bigint;
ALTER TABLE productions ADD COLUMN opening_weekend bigint;

-- 
-- populate rating & votes
-- 
UPDATE productions p 
SET rating = r.rating, votes = r.votes 
FROM productions_ratings r 
WHERE p.idproductions = r.idproductions;

-- 
-- populate budget
-- 
WITH budget AS (
	SELECT idproductions, MAX(amount) budget 
	FROM productions_business 
	WHERE business_type = 'budget' AND 
		currency = 'USD' AND 
		amount IS NOT NULL AND 
		amount > 0 AND 
		amount < 350000000
	GROUP BY idproductions
) 
UPDATE productions p
SET budget = budget.budget 
FROM budget 
WHERE p.idproductions = budget.idproductions;

-- 
-- populate box office gross & opening weekend box office take
-- 
UPDATE productions p
SET box_office_gross = (
	SELECT amount  
	FROM productions_business b 
	WHERE b.business_type = 'box office gross' AND 
		b.currency = 'USD' AND 
		LOWER(b.region) = 'worldwide' AND 
		amount IS NOT NULL AND 
		amount > 0 AND 
		amount <= 2800000000 AND 
		b.idproductions = p.idproductions 
	ORDER BY b.date DESC
	LIMIT 1
), opening_weekend = (
	SELECT amount  
	FROM productions_business b 
	WHERE b.business_type = 'opening weekend box office take' AND 
		b.currency = 'USD' AND 
		LOWER(b.region) = 'usa' AND 
		amount IS NOT NULL AND 
		amount > 0 AND 
		amount <= 250000000 AND 
		b.idproductions = p.idproductions 
	ORDER BY b.date DESC
	LIMIT 1
);




-- clean up productions table
-- 

-- 
-- filter for production type
-- 
DELETE 
FROM productions 
WHERE productions_type != 'movie/series';

-- 
-- remove column
-- 
ALTER TABLE productions DROP COLUMN productions_type CASCADE;
