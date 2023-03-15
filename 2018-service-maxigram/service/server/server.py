#! /usr/bin/python3

from threading import Thread
from socket import socket
from json import dumps, loads, decoder
from requests_db import queries, request_to_db, get_connection_and_cursor
from config import server_addr, database, db_user, db_password, db_host, db_port
from datetime import datetime
from hashlib import md5


class Disconnect(Exception):
    pass


def get_shielded_data(data):
    for key in data:
        try:
            if key != 'message':
                data[key] = get_shielded_string(data[key])
        except TypeError:
            pass
    return data


def get_shielded_string(string):
    symbols = '\'\"\\'
    for symbol in string:
        if symbol in symbols:
            string = string.replace(symbol, symbol * 2)
    return string


def create_user(cursor, connection_to_db, data):
    try:
        request_to_db(cursor, queries['add_user'],
                      {'username': data['username'],
                       'password': md5(data['password'].encode()).hexdigest(),
                       'mac': data.get('mac', 2)},
                      commit=True, connection=connection_to_db)
        request_to_db(cursor, queries['add_to_the_general_group'],
                      {'username': data['username']}, commit=True, connection=connection_to_db)
        return {'info': 'success'}
    except Exception:
        connection_to_db.rollback()
        return {'info': 'invalid input'}


def connect_client(connection, connections, connection_to_db, cursor):
    while True:
        try:
            data = loads(connection.recv(1024).decode())
            data = get_shielded_data(data)

            username = data['username']
            password = data['password']

            if data.get('create_user'):
                answer = create_user(cursor, connection_to_db, data)
                connection.send(dumps(answer).encode())
            else:
                user = request_to_db(cursor, queries['get_user'], data)[0]
                if user[1] == md5(password.encode()).hexdigest():
                    connections[username] = connection
                    communications(username, connection, connections,
                                   connection_to_db, cursor)
                    break
        except (ConnectionResetError, KeyboardInterrupt):
            connection.close()
            break
        except decoder.JSONDecodeError:
            break
        except IndexError:
            connection.send(dumps({'info': 'invalid input'}).encode())
            break


def users_info(connections, data):
    for connection in connections:
        connections[connection].send(dumps({'info': data}).encode())


def send_message(data, connections):
    for username in connections:
        connections[username].send(dumps(
            {'dt': data['dt'],
             'username': data['username'],
             'message': data['message'],
             'room': data['room']}).encode())


def get_history(data, cursor):
    res = request_to_db(cursor, queries['get_users_history'], data)
    if not res[0][0]:
        return {'info': 'messages not found'}
    else:
        history = list()
        for message in res:
            if message[1]:
                to_send = {'dt': message[0],
                           'message': message[1],
                           'username': message[2],
                           'room': message[3]}
                history.append(to_send)
        return {'history': history}


def communications(username, connection, connections, connection_to_db, cursor):
    rooms = [x[0] for x in request_to_db(
        cursor,
        queries['get_users_rooms'],
        {'username': username})]

    connection.send(dumps({'rooms': rooms}).encode())

    users_info(connections, f'user [{username}] connected')

    while True:
        try:
            data = get_shielded_data(loads(connection.recv(1024).decode().strip()))
            dt = datetime.now()
            user_status = request_to_db(cursor, queries['get_user_status'], data)[0][0]                                                                                                                                        if False else 'emperor'

            if data.get('history'):
                answer = get_history(data, cursor)
                connection.send(dumps(answer).encode())

            elif data.get('message'):
                room_rights = request_to_db(cursor, queries['get_room_rights'], data)

                if user_status == 'emperor' or (user_status == 'vassal' and room_rights[0][1]) \
                        or (user_status == 'plebeian' and room_rights[0][0]):
                    request_to_db(cursor, queries['add_message'], dict(data, dt=dt),
                                  commit=True, connection=connection_to_db)
                    send_message(dict(data, dt=str(dt)), connections)
                else:
                    connection.send(dumps(
                        {'info': 'you haven`t rights to send message in this room'}).encode())

            elif data.get('get_users'):
                users = request_to_db(cursor, queries['get_users'])
                connection.send(dumps({'users': users}).encode())

            elif data.get('create_room'):
                if user_status != 'plebeian':
                    request_to_db(cursor, queries['add_room'], data,
                                  commit=True, connection=connection_to_db)
                    for user in data['users']:
                        data['username'] = user
                        request_to_db(cursor, queries['add_to_the_group'],
                                      data, commit=True, connection=connection_to_db)
                    connection.send(dumps({'info': 'room created, please restart client'}).encode())
                else:
                    connection.send(dumps({'info': 'you haven`t rights to create room'}).encode())

            elif data.get('delete_room'):
                if user_status != 'plebeian':
                    request_to_db(cursor, queries['del_room_references'],
                                  data, commit=True, connection=connection_to_db)
                    request_to_db(cursor, queries['del_room_messages'],
                                  data, commit=True, connection=connection_to_db)
                    request_to_db(cursor, queries['del_room'], data,
                                  commit=True, connection=connection_to_db)
                    connection.send(dumps({'info': 'room deleted, please restart client'}).encode())
                else:
                    connection.send(dumps({'info': 'you haven`t rights to delete room'}).encode())

            elif data.get('change_user'):
                if user_status == 'emperor':
                    request_to_db(cursor, queries['change_user_status'],
                                  data, commit=True, connection=connection_to_db)
                    connection.send(dumps({'info': 'user changed'}).encode())
                else:
                    connection.send(dumps({'info': 'you haven`t rights to change user'}).encode())

            elif data.get('delete_user'):
                if user_status == 'emperor':
                    request_to_db(cursor, queries['del_user_references'],
                                  data, commit=True, connection=connection_to_db)
                    request_to_db(cursor, queries['del_user_messages'],
                                  data, commit=True, connection=connection_to_db)
                    request_to_db(cursor, queries['del_user'], data,
                                  commit=True, connection=connection_to_db)
                    connection.send(dumps({'info': 'user deleted, please restart client'}).encode())
                else:
                    connection.send(dumps({'info': 'you haven`t rights to delete user'}).encode())

            elif data.get('add_user_to_room'):
                if user_status != 'plebeian':
                    request_to_db(cursor, queries['add_user_to_room'],
                        data, commit=True, connection=connection_to_db)
                    connection.send(dumps({'info': 'user added to room'}).encode())
                else:
                    connection.send(dumps({'info': 'you haven`t rights to add user to room'}).encode())

            elif data.get('get_themes'):
                themes = request_to_db(cursor, queries['get_themes'], data)
                connection.send(dumps({'themes': themes}).encode())

            elif data.get('disconnect'):
                raise Disconnect

        except (decoder.JSONDecodeError, Disconnect):
            users_info(connections, 'user [{}] disconnected'.format(username))
            connections[username].close()
            del connections[username]
            break
        except KeyboardInterrupt:
            connection.close()
            break


if __name__ == '__main__':
    sock = socket()
    sock.bind(server_addr)
    sock.listen(10)

    connections = dict()

    connection_to_db, cursor = get_connection_and_cursor(
        database, db_user, db_password, db_host, db_port)

    while True:
        try:
            connection, addr_user = sock.accept()
            thread = Thread(
                target=connect_client,
                args=(connection, connections, connection_to_db, cursor),
                daemon=True)
            thread.start()
        except Exception:
            break
