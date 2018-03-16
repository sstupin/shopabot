CREATE TABLE IF NOT EXISTS users (
	user_id  			integer NOT NULL,
	first_name			varchar(100),
	last_name			varchar(100),
	username			varchar(100),
	role				integer,
	last_access_time	timestamp,
	first_access_time	timestamp,
	PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS lists (
	id		SERIAL PRIMARY KEY,
	list	varchar(100),
	user_id	integer
);

CREATE TABLE IF NOT EXISTS products (
	id				SERIAL PRIMARY KEY,
	product			varchar(255) NOT NULL,
	crc32			integer
);

CREATE TABLE IF NOT EXISTS products_in_lists (
	list_id		integer,
	product_id	integer
);

CREATE UNIQUE INDEX IF NOT EXISTS products_in_lists_idx ON products_in_lists (
	list_id,
	product_id
);
