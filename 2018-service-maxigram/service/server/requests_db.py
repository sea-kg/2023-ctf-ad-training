from psycopg2 import connect
from config import database, db_user, db_password, db_host, db_port, server_addr


queries = { 'change_user_status':
                '''UPDATE users SET (status)=(
                SELECT id_status FROM statuses WHERE status='{status}')
                WHERE username='{modifiable_user}';''',
            'add_message': 
                '''INSERT INTO messages (id_sender, id_room, dt, message)
                VALUES ((SELECT id_user FROM users WHERE username='{username}'),
                (SELECT id_room FROM rooms WHERE room_name='{room}'),
                '{dt}', '{message}');''',
            'add_user':
                '''INSERT INTO users (username, password, status, id_settings) 
                VALUES ('{username}', '{password}', {mac}, 1);''',
            'add_user_to_room':
                '''INSERT INTO users_rooms (id_room, id_user) VALUES 
                ((SELECT id_room FROM rooms WHERE room_name='{room_name}'),
                (SELECT id_user FROM users WHERE username='{username}'));''',
            'add_to_the_general_group':
                '''INSERT INTO users_rooms (id_room, id_user) VALUES 
                ((SELECT id_room FROM rooms WHERE room_name='general'),
                (SELECT id_user FROM users WHERE username='{username}'));''',
            'add_to_the_group':
                '''INSERT INTO users_rooms (id_room, id_user) VALUES 
                ((SELECT id_room FROM rooms WHERE room_name='{room_name}'),
                (SELECT id_user FROM users WHERE username='{username}'));''',
            'add_room':
                '''INSERT INTO rooms (room_name, room_type) VALUES 
                ('{room_name}', {room_type});''',
            'del_user':
                '''DELETE FROM users WHERE username='{del_username}';''',
            'del_user_messages':
                '''DELETE FROM messages WHERE id_sender IN
                (SELECT id_user FROM users WHERE username='{del_username}');''',
            'del_user_references':
                '''DELETE FROM users_rooms WHERE id_user IN
                (SELECT id_user FROM users WHERE username='{del_username}');''',
            'del_room':
                '''DELETE FROM rooms WHERE room_name='{room_name}';''',
            'del_room_messages':
                '''DELETE FROM messages WHERE id_room IN
                (SELECT id_room FROM rooms WHERE room_name='{room_name}');''',
            'del_room_references':
                '''DELETE FROM users_rooms WHERE id_room IN
                (SELECT id_room FROM rooms WHERE room_name='{room_name}');''',
            'get_themes':
                '''SELECT * FROM settings;''',
            'get_rooms':
                '''SELECT * FROM rooms''',
            'get_users_rooms': 
                '''SELECT room_name FROM rooms WHERE id_room IN
                (SELECT id_room FROM users_rooms WHERE id_user IN
                (SELECT id_user FROM users WHERE username='{username}'));''',
            'get_user_status':
                '''SELECT status FROM statuses WHERE 
                id_status=(SELECT status FROM users WHERE username='{username}');''',
            'get_room_rights':
                '''SELECT plebeian_writing, vassal_writing FROM room_type
                WHERE id_type=(SELECT room_type FROM rooms WHERE room_name='{room}');''',
            'get_users': 
                '''SELECT username FROM users;''',
            'get_user': 
                '''SELECT username, password FROM users 
                WHERE username='{username}';''',
            'get_message':
                '''SELECT message FROM messages WHERE dt='{dt}';''',
            'get_messages': 
                '''SELECT a.message, b.username, c.room_name
                FROM (SELECT message, id_sender, id_room FROM messages) AS a
                FULL OUTER JOIN
                (SELECT username, id_user FROM users) AS b ON b.id_user=a.id_sender
                FULL OUTER JOIN
                (SELECT id_room, room_name FROM rooms) AS c ON a.id_room=c.id_room;''',
            'get_users_history': 
                '''SELECT a.dt, a.message, b.username, c.room_name
                FROM
                (SELECT message, id_sender, id_room, dt FROM messages) AS a
                FULL OUTER JOIN
                (SELECT username, id_user FROM users) AS b ON b.id_user=a.id_sender
                FULL OUTER JOIN
                (SELECT id_room, room_name FROM rooms) AS c ON a.id_room=c.id_room
                WHERE c.id_room IN
                (SELECT users_rooms.id_room FROM users_rooms
                INNER JOIN
                users ON users_rooms.id_user=users.id_user AND users.id_user IN 
                (SELECT users.id_user FROM users WHERE username='{username}'));'''}


def get_connection_and_cursor(database, user, password, host, port):
    connection_to_db = connect(database=database, user=db_user,
        password=db_password, host=db_host, port=db_port)
    cursor = connection_to_db.cursor()
    return connection_to_db, cursor


def request_to_db(cursor, query, data=dict(), commit=False, connection=None):
    cursor.execute(query.format(**data))
    if commit:
        connection.commit()
    else:
        return cursor.fetchall()
