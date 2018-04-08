DROP TABLE IF EXISTS users;
CREATE TABLE users(
	user_id integer,
	login varchar(10) NOT NULL,
	password varchar(20) NOT NULL,
	payroll integer CHECK (payroll >= 0),
	PRIMARY KEY (user_id),
	UNIQUE (login)
);

DROP TABLE IF EXISTS players;
CREATE TABLE players(
	player_id varchar(10),
	player_name varchar(30) NOT NULL,
	position varchar(2) CHECK (position = 'OF' OR position = '1B' OR position = '2B' OR position = 'SS' OR position = '3B' OR position = 'P' or position = 'C'),
	price integer CHECK (price > 0),
	PRIMARY KEY (player_id),
	UNIQUE (player_name)
);

DROP TABLE IF EXISTS batters;
CREATE TABLE batters(
	player_id varchar(10),
	atbats integer CHECK (atbats >= 0),
	average real CHECK (average >= 0),
	hits integer CHECK (hits >= 0),
	b_walks integer CHECK (b_walks >= 0),
	runs integer CHECK (runs >= 0),
	rbi integer CHECK (rbi >= 0),
	homeruns integer CHECK (homeruns >= 0),
	PRIMARY KEY (player_id),
	FOREIGN KEY (player_id) REFERENCES players ON DELETE CASCADE
);

DROP TABLE IF EXISTS pitchers;
CREATE TABLE pitchers(
	player_id varchar(10),
	innings integer CHECK (innings >= 0),
	era real CHECK (era >= 0),
	p_walks integer CHECK (p_walks >= 0),
	strikeouts integer CHECK (strikeouts >= 0),
	wins integer CHECK (wins >= 0),
	losses integer CHECK (losses >= 0),
	saves integer CHECK (saves >= 0),
	PRIMARY KEY (player_id),
	FOREIGN KEY (player_id) REFERENCES players ON DELETE CASCADE
);

DROP TABLE IF EXISTS owns;
CREATE TABLE owns(
	user_id integer,
	player_id varchar(10),
	PRIMARY KEY (user_id, player_id),
	FOREIGN KEY (user_id) REFERENCES users ON DELETE CASCADE,
	FOREIGN KEY (player_id) REFERENCES players ON DELETE CASCADE
);

DROP TABLE IF EXISTS leagues;
CREATE TABLE leagues(
	league_id integer,
	user_id integer NOT NULL,
	league_name varchar(30),
	max_payroll integer CHECK (max_payroll >= 0),
	atbats_weight real,
	average_weight real,
	hits_weight real,
	b_walks_weight real,
	runs_weight real,
	rbi_weight real,
	homeruns_weight real,
	innings_weight real,
	era_weight real,
	p_walks_weight real,
	strikeouts_weight real,
	wins_weight real,
	losses_weight real,
	saves_weight real,
	PRIMARY KEY (league_id),
	FOREIGN KEY (user_id) REFERENCES users ON DELETE NO ACTION,
	UNIQUE (league_name)
);

DROP TABLE IF EXISTS plays;
CREATE TABLE plays(
	user_id integer,
	league_id integer,
	PRIMARY KEY (user_id, league_id),
	FOREIGN KEY (user_id) REFERENCES users ON DELETE CASCADE,
	FOREIGN KEY (league_id) REFERENCES leagues ON DELETE CASCADE
);

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions(
	transaction_id integer,
	user_id integer NOT NULL,
	player_id varchar(10) NOT NULL,
	timestamp varchar(20),
	type varchar(5) CHECK (type = 'CLAIM' OR type = 'WAIVE'),
	PRIMARY KEY (transaction_id),
	FOREIGN KEY (user_id, player_id) REFERENCES owns ON DELETE CASCADE
);