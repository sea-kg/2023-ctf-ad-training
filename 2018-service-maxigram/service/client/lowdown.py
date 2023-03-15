from socket import socket
from json import dumps, loads, decoder
from threading import Thread
from re import findall
from tkinter import *
from widgets import MyCheckbutton


username = None
password = None
sock = socket()


def parse_data(data):
    try:
        return loads(data)
    except decoder.JSONDecodeError:
        return [loads(f'{{{message}}}') for message in findall(r'[^{}]+', data)]


def connect_to_server(frame, addr, sock, username, password):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        sock.send(dumps({'username': username, 'password': password}).encode())
        data = parse_data(sock.recv(1024).decode())
        if isinstance(data, list):
            for message in data:
                if 'rooms' in message:
                    info(frame.master.info_frame.messages, '*****select a room*****')
                    return message['rooms']
                elif 'info' in message:
                    frame.label_answer['text'] = message.get('info')
        elif isinstance(data, dict):
            if 'rooms' in data:
                return data.get('rooms')
            elif 'info' in data:
                frame.label_answer['text'] = data.get('info')
    except (ConnectionRefusedError, BrokenPipeError):
        frame.label_answer['text'] = 'server is not available'


def get_message(sock, frame):
    while True:
        try:
            data = parse_data(sock.recv(4096).decode())
            if 'room' in data:
                listbox = frame.master.chat_frames[data.get('room')].messages
                info(listbox, '[{username}]: {message}'.format(
                    username=data.get('username'),
                    message=data.get('message')))
            elif 'info' in data:
                info(frame.master.info_frame.messages, '*****{}*****'.format(data.get('info')))
            elif 'users' in data:
                frame.master.addroom_frame.users = data.get('users')
                frame.master.addroom_frame.show_frame()
            elif 'history' in data:
                for message in data.get('history'):
                    listbox = frame.master.chat_frames[message.get('room')].messages
                    info(listbox, '[{username}]: {message}'.format(
                        username=message.get('username'),
                        message=message.get('message')))
                info(frame.master.info_frame.messages, '*****history received*****')
            elif 'themes' in data:
                frame.master.themes_frame.list_themes = data.get('themes')
                frame.master.themes_frame.create_radiobuttons()
                frame.master.themes_frame.show_frame()
        except (OSError, AttributeError):
            break


def messages_thread(sock, frame):
    thread = Thread(target=get_message, args=(sock, frame), daemon=True)
    thread.start()


def send_message(sock, enter, username, room, frame):
    try:
        sock.send(dumps(
            {
                'message': enter.get(),
                'username': username,
                'room': room
            }).encode())
    except BrokenPipeError:
        info(frame.info_frame.messages, '*****server is not available*****')


def add_room_history(sock, username, master):
    try:
        sock.send(dumps(
            {
                'username': username,
                'history': True
            }).encode())
    except BrokenPipeError:
        info(master.info_frame.messages, '*****server is not available*****')


def add_users(sock, username, master):
    try:
        sock.send(dumps(
            {
                'username': username,
                'get_users': True
            }).encode())
    except BrokenPipeError:
        info(master.info_frame.messages, '*****server is not available*****')


def create_chat_frames(rooms, listbox, master, ChatFrame):
    for room in rooms:
        listbox.insert(END, room)
        master.chat_frames[room] = ChatFrame()


def info(listbox, data):
    listbox.insert(END, data)
    listbox.yview(END)


def create_user(frame, sock, addr):
    username = frame.entry_username.get().lower()
    password = frame.entry_password.get()
    confirm_password = frame.entry_confirm_password.get()
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        if password == confirm_password and len(frame.entry_password.get()) > 0:
            sock.send(dumps(
                {
                    'username': username,
                    'password': password,
                    'create_user': True
                }).encode())
            data = parse_data(sock.recv(1024).decode())
            if isinstance(data, list):
                for message in data:
                    frame.label_answer['text'] = message.get('info')
            else:
                frame.label_answer['text'] = data.get('info')
        else:
            frame.label_answer['text'] = 'incorrect input'
    except (ConnectionRefusedError, BrokenPipeError):
        frame.label_answer['text'] = 'server is not available'


def create_room(addroom_frame, info_frame, sock, addr, username):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        room_name = addroom_frame.enter_room_name.get()
        room_type = addroom_frame.enter_type.get()
        users = addroom_frame.get_users()
        if room_name.isalnum() and room_type.isdigit() and 0 < int(room_type) < 4 and users:
            sock.send(dumps(
                {
                    'username': username,
                    'users': users,
                    'room_name': room_name,
                    'room_type': room_type,
                    'create_room': True
                }).encode())
        else:
            info(info_frame.messages, '****incorrect input*****')
        addroom_frame.enter_room_name.delete(0, END)
        addroom_frame.enter_type.delete(0, END)
        addroom_frame.hide_var_checkbuttons()
    except (ConnectionRefusedError, BrokenPipeError):
        info(info_frame.messages, '****server is not available*****')


def delete_room(delroom_frame, info_frame, sock, addr, username):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        room_name = delroom_frame.entry.get()
        if room_name.isalnum():
            sock.send(dumps(
                {
                    'username': username,
                    'room_name': room_name,
                    'delete_room': True
                }).encode())
        else:
            info(info_frame.messages, '****incorrect input*****')
        delroom_frame.entry.delete(0, END)
    except (ConnectionRefusedError, BrokenPipeError):
        info(info_frame.messages, '****server is not available*****')


def change_status(changestatus_frame, info_frame, sock, addr, username):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        modifiable_user = changestatus_frame.entry_username.get()
        status = changestatus_frame.var.get()
        if modifiable_user.isalnum() and status != 'None':
            sock.send(dumps(
                {
                    'username': username,
                    'modifiable_user': modifiable_user,
                    'status': status,
                    'change_user': True
                }).encode())
        else:
            info(info_frame.messages, '****incorrect input*****')
        changestatus_frame.entry_username.delete(0, END)
        changestatus_frame.var.set(None)
    except (ConnectionRefusedError, BrokenPipeError):
        info(info_frame.messages, '****server is not available*****')


def delete_user(deluser_frame, info_frame, sock, addr, username):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        del_username = deluser_frame.entry.get()
        if del_username.isalnum():
            sock.send(dumps(
                {
                    'username': username,
                    'del_username': del_username,
                    'delete_user': True
                }).encode())
        else:
            info(info_frame.messages, '****incorrect input*****')
        deluser_frame.entry.delete(0, END)
    except (ConnectionRefusedError, BrokenPipeError):
        info(info_frame.messages, '****server is not available*****')


def disconnect_from_server(sock, addr, username, frame):
    try: 
        sock.connect(addr)
    except OSError:
        pass
    try:
        sock.send(dumps({'username': username, 'disconnect': True}).encode())
    except (ConnectionRefusedError, BrokenPipeError):
        info(frame.info_frame.messages, '****server is not available*****')


def get_choiced_theme(themes_frame, info_frame, sock, addr, username,
    main_color, sand_color, bd):
    choice = themes_frame.var.get()
    if choice != 'None':
        main_color = themes_frame.list_themes[choice-1][1]
        sand_color = themes_frame.list_themes[choice-1][2]
        bd = themes_frame.list_themes[choice-1][3]
    return main_color, sand_color, bd


def get_themes(frame, sock, addr, username):
    try:
        sock.send(dumps({'username': username, 'get_themes': True}).encode())
    except BrokenPipeError:
        info(frame.master.info_frame.messages, '*****server is not available*****')
