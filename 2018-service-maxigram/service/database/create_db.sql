DROP DATABASE IF EXISTS maxigram;
CREATE DATABASE maxigram;
\connect maxigram;
CREATE TABLE IF NOT EXISTS settings(
	id_settings serial PRIMARY KEY,
	bg varchar(7) NOT NULL,
	fg varchar(7) NOT NULL,
	bd int NOT NULL
);
CREATE TABLE IF NOT EXISTS statuses(
	id_status serial PRIMARY KEY,
	status varchar(8) NOT NULL
		CONSTRAINT val_stat CHECK (status='plebeian' OR status='vassal' OR status='emperor'),
	add_room boolean NOT NULL,
	delete_room boolean NOT NULL,
	change_user boolean NOT NULL,
	delete_user boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS users(
	id_user serial PRIMARY KEY,
	username varchar(32) UNIQUE NOT NULL,
	password varchar(32) NOT NULL,
	status int REFERENCES statuses(id_status),
	id_settings int REFERENCES settings(id_settings)
);
CREATE TABLE IF NOT EXISTS room_type(
	id_type serial PRIMARY KEY,
	plebeian_writing boolean NOT NULL,
	vassal_writing boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS rooms(
	id_room serial PRIMARY KEY,
	room_name varchar(40) UNIQUE NOT NULL,
	room_type int REFERENCES room_type(id_type)
);
CREATE TABLE IF NOT EXISTS users_rooms(
	id_reference serial PRIMARY KEY,
	id_room int REFERENCES rooms(id_room),
	id_user int REFERENCES users(id_user)
);
CREATE TABLE IF NOT EXISTS messages(
	id_message serial PRIMARY KEY,
	id_sender int REFERENCES users(id_user),
	id_room int REFERENCES rooms(id_room),
	dt varchar(60) NOT NULL,
	message text NOT NULL
);
INSERT INTO statuses (status, add_room, delete_room, change_user, delete_user)
VALUES ('emperor', TRUE, TRUE, TRUE, TRUE);
INSERT INTO statuses (status, add_room, delete_room, change_user, delete_user)
VALUES ('vassal', TRUE, TRUE, FALSE, FALSE);
INSERT INTO statuses (status, add_room, delete_room, change_user, delete_user)
VALUES ('plebeian', FALSE, FALSE, FALSE, FALSE);
INSERT INTO room_type (plebeian_writing, vassal_writing) values (TRUE, TRUE);
INSERT INTO room_type (plebeian_writing, vassal_writing) values (FALSE, TRUE);
INSERT INTO room_type (plebeian_writing, vassal_writing) values (FALSE, FALSE);
INSERT INTO rooms (room_name, room_type) VALUES ('general', 1);
INSERT INTO settings (bg, fg, bd) VALUES ('black', '#00FF00', 3);
INSERT INTO settings (bg, fg, bd) VALUES ('#8b8f94', 'black', 3);
INSERT INTO settings (bg, fg, bd) VALUES ('#301026', 'white', 5);
INSERT INTO settings (bg, fg, bd) VALUES ('#035e8c', '#a9cc0e ', 5);
INSERT INTO settings (bg, fg, bd) VALUES ('black', 'red', 5);
INSERT INTO settings (bg, fg, bd) VALUES ('#005078', '#bde7fc', 1);
INSERT INTO users (username, password, status, id_settings) 
VALUES ('shaman', 'fca44c330f5fc4d4034d83f83da7dd57', 1, 1);
INSERT INTO users_rooms (id_user, id_room) VALUES (1, 1);

CREATE ROLE max WITH PASSWORD 'zaq1@WSX';
ALTER ROLE max LOGIN;
ALTER ROLE max SUPERUSER;
