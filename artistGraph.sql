DROP TABLE IF EXISTS PROFILE;

CREATE TABLE PROFILE
(
	id_sc integer primary key,
	name text,
	press text,
	booking text,
	management text,
	personal text,
	official text,
	twitter text,
	tumblr text,
	bandcamp text,
	youtube text,
	instagram text,
	facebook text,
	merch text,
	city text,
	state text,
	country text
);

DROP TABLE IF EXISTS EDGE;

CREATE TABLE EDGE
(
	type text,
	weight integer,
	follower_id integer,
	followee_id integer
);
