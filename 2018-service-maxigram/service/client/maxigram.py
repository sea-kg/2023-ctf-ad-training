#! /usr/bin/python3

from config import server_addr
from lowdown import *
from widgets import *
from re import sub


class AddroomFrame(MyFrame):
    def show_frame(self):
        self.checkbuttons.clear()

        for user in self.users:
            var = BooleanVar()
            var.set(0)
            self.checkbuttons.append({'var': var,
                                      'check': MyCheckbutton(self, main_color=main_color,
                                                             sand_color=sand_color, bd=bd, anchor=W, text=user,
                                                             variable=var, width=32)})

        self.upper = 0

        self.users_label.grid(row=0, column=0)

        if len(self.checkbuttons) > 15:
            self.up.grid(row=16, column=1)
            self.down.grid(row=16, column=2)
            self.lower = 14
            for i in range(15):
                self.checkbuttons[i]['check'].grid(row=i + 1, column=0)
        else:
            for i in range(1, len(self.checkbuttons) + 1):
                self.checkbuttons[i - 1]['check'].grid(row=i, column=0)
            self.lower = len(self.checkbuttons) - 1

        self.room_name.grid(row=0, column=3)
        self.enter_room_name.grid(row=1, column=3)
        self.label_type.grid(row=2, column=3)
        self.enter_type.grid(row=3, column=3)
        self.submit.grid(row=4, column=3)

    def add_room(self, event):
        create_room(self, self.master.info_frame, sock, server_addr, username)

    def get_users(self):
        users = list()
        for user in self.checkbuttons:
            if user['var'].get() == 1:
                users.append(user['check']['text'])
        return users

    def hide_var_checkbuttons(self):
        for user in self.checkbuttons:
            user['var'].set(0)

    def scroll_up(self, event):
        if self.upper != 0:
            self.checkbuttons[self.lower]['check'].grid_forget()
            self.lower -= 1
            self.upper -= 1
            count = 0
            for i in range(self.upper, self.lower + 1):
                self.checkbuttons[i]['check'].grid(row=count + 1, column=0)
                count += 1

    def scroll_down(self, event):
        if self.lower != len(self.checkbuttons) - 1:
            self.checkbuttons[self.upper]['check'].grid_forget()
            self.upper += 1
            self.lower += 1
            count = 0
            for i in range(self.upper, self.lower + 1):
                self.checkbuttons[i]['check'].grid(row=count + 1, column=0)
                count += 1

    def __init__(self, *args, **kwargs):
        super(AddroomFrame, self).__init__()
        global username, sock, server_addr

        self.checkbuttons = list()

        self.users = list()

        self.up = MyButton(self, text='up', width=2)
        self.up.bind('<Button-1>', self.scroll_up)

        self.down = MyButton(self, text='down', width=2)
        self.down.bind('<Button-1>', self.scroll_down)

        self.users_label = MyLabel(self, text='choose users:')

        self.room_name = MyLabel(self, text='enter room name:')
        self.enter_room_name = MyEntry(self)

        self.label_type = MyLabel(self, text='enter room type:')
        self.enter_type = MyEntry(self)

        self.submit = MyButton(self, text='submit')
        self.submit.bind('<Button-1>', self.add_room)


class DelroomFrame(MyFrame):
    def del_room(self, event):
        delete_room(self, self.master.info_frame, sock, server_addr, username)

    def __init__(self, *args, **kwargs):
        super(DelroomFrame, self).__init__()
        global username, sock, server_addr

        self.label = MyLabel(self, text='enter room name:')
        self.label.pack()

        self.entry = MyEntry(self)
        self.entry.pack()

        self.submit = MyButton(self, text='submit')
        self.submit.pack()
        self.submit.bind('<Button-1>', self.del_room)


class ChangestatusFrame(MyFrame):
    def ch_status(self, event):
        change_status(self,
                      self.master.info_frame, sock, server_addr, username)

    def __init__(self, *args, **kwargs):
        super(ChangestatusFrame, self).__init__()
        global username, sock, server_addr

        self.label_username = MyLabel(self, text='enter username:')
        self.label_username.pack()

        self.entry_username = MyEntry(self)
        self.entry_username.pack()

        self.label_status = MyLabel(self, text='select status:')
        self.label_status.pack()

        self.var = StringVar()
        self.var.set(None)
        self.statuses = {status: MyRadiobutton(self, text=status,
                                               variable=self.var, value=status, main_color=main_color,
                                               sand_color=sand_color, bd=bd)
                         for status in ['plebeian', 'vassal', 'emperor']}

        for status in self.statuses:
            self.statuses[status].pack()

        self.submit = MyButton(self, text='submit')
        self.submit.pack()
        self.submit.bind('<Button-1>', self.ch_status)


class DeluserFrame(MyFrame):
    def del_user(self, event):
        delete_user(self, self.master.info_frame, sock, server_addr, username)

    def __init__(self, *args, **kwargs):
        super(DeluserFrame, self).__init__()
        global username, sock, server_addr

        self.label = MyLabel(self, text='enter username:')
        self.label.pack()

        self.entry = MyEntry(self)
        self.entry.pack()

        self.submit = MyButton(self, text='submit')
        self.submit.pack()
        self.submit.bind('<Button-1>', self.del_user)


class ThemesFrame(MyFrame):
    def change_config(self, main_color, sand_color, bd):
        with open('config.py') as file:
            text = file.read()
        text = sub(r'main_color = \'[#\w]+\'',
                   'main_color = \'' + main_color + '\'', text)
        text = sub(r'sand_color = \'[#\w]+\'',
                   'sand_color = \'' + sand_color + '\'', text)
        text = sub(r'bd = \d+', 'bd = ' + str(bd), text)
        with open('config.py', 'w') as file:
            file.write(text)

    def show_frame(self):
        try:
            self.master.send_message_frame.place_forget()
            self.master.delroom_frame.place_forget()
            self.master.changestatus_frame.place_forget()
            self.master.deluser_frame.place_forget()
            self.master.addroom_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        self.master.themes_frame.place(x=465, y=150)

    def create_radiobuttons(self):
        for theme in self.themes:
            self.themes[theme].pack_forget()

        self.submit.pack_forget()

        self.var = IntVar()
        self.var.set(None)
        self.themes = {theme[0]: MyRadiobutton(self, text=theme[0],
                                               variable=self.var, value=theme[0], main_color=main_color,
                                               sand_color=sand_color, bd=bd)
                       for theme in self.master.themes_frame.list_themes}

        for theme in self.themes:
            self.themes[theme].pack()

        self.submit.pack()

    def save(self, event):
        global main_color, sand_color, bd, count, main_window

        main_color, sand_color, bd = get_choiced_theme(self,
                                                       self.master.info_frame, sock, server_addr, username,
                                                       main_color, sand_color, bd)

        self.change_config(main_color, sand_color, bd)
        self.master.change_theme(main_color, sand_color, bd)

    def __init__(self, *args, **kwargs):
        super(ThemesFrame, self).__init__()
        global username, sock, server_addr

        self.label = MyLabel(self, text='choice theme:')
        self.label.pack()

        self.themes = dict()
        self.list_themes = list()

        self.submit = MyButton(self, text='submit')
        self.submit.bind('<Button-1>', self.save)


class MenuFrame(MyFrame):
    def show_addroom_frame(self, event):
        try:
            self.master.send_message_frame.place_forget()
            self.master.delroom_frame.place_forget()
            self.master.changestatus_frame.place_forget()
            self.master.deluser_frame.place_forget()
            self.master.themes_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        self.master.addroom_frame.place(x=220, y=60)
        add_users(sock, username, self.master)

    def show_delroom_frame(self, event):
        try:
            self.master.send_message_frame.place_forget()
            self.master.addroom_frame.place_forget()
            self.master.changestatus_frame.place_forget()
            self.master.deluser_frame.place_forget()
            self.master.themes_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        self.master.delroom_frame.place(x=425, y=180)

    def show_changestatus_frame(self, event):
        try:
            self.master.send_message_frame.place_forget()
            self.master.addroom_frame.place_forget()
            self.master.delroom_frame.place_forget()
            self.master.deluser_frame.place_forget()
            self.master.themes_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        self.master.changestatus_frame.place(x=425, y=180)

    def show_deluser_frame(self, event):
        try:
            self.master.send_message_frame.place_forget()
            self.master.addroom_frame.place_forget()
            self.master.delroom_frame.place_forget()
            self.master.changestatus_frame.place_forget()
            self.master.themes_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        self.master.deluser_frame.place(x=425, y=180)

    def disconnect(self, event):
        global sock, username, server_addr
        try:
            self.master.send_message_frame.place_forget()
            self.master.addroom_frame.place_forget()
            self.master.delroom_frame.place_forget()
            self.master.changestatus_frame.place_forget()
            self.master.deluser_frame.place_forget()
            self.master.rooms_frame.place_forget()
            self.master.rooms_frame.rooms.delete(0, END)
            self.master.info_frame.place_forget()
            self.master.menu_frame.place_forget()
            self.master.themes_frame.place_forget()
            self.master.chat_frames[self.master.rooms_frame.selected_room].place_forget()
        except KeyError:
            pass
        disconnect_from_server(sock, server_addr, username, self.master)
        sock.close()
        sock = socket()
        self.master.signin_frame.place(x=320, y=250)
        self.master.bind('<Return>', self.master.signin_frame.signin)

    def add_themes(self, event):
        global sock, server_addr, username

        get_themes(self, sock, server_addr, username)

    def __init__(self, *args, **kwargs):
        super(MenuFrame, self).__init__()

        self.add_room = MyButton(self, text='add room')
        self.add_room.grid(row=0, column=0)
        self.add_room.bind('<Button-1>', self.show_addroom_frame)

        self.delete_room = MyButton(self, text='delete room')
        self.delete_room.grid(row=0, column=1)
        self.delete_room.bind('<Button-1>', self.show_delroom_frame)

        self.change_status = MyButton(self, text='change user')
        self.change_status.grid(row=0, column=3)
        self.change_status.bind('<Button-1>', self.show_changestatus_frame)

        self.delete_user = MyButton(self, text='delete user')
        self.delete_user.grid(row=0, column=4)
        self.delete_user.bind('<Button-1>', self.show_deluser_frame)

        self.themes = MyButton(self, text='themes')
        self.themes.grid(row=0, column=5)
        self.themes.bind('<Button-1>', self.add_themes)

        self.disconnect_from_the_server = MyButton(self, text='disconnect')
        self.disconnect_from_the_server.grid(row=0, column=6)
        self.disconnect_from_the_server.bind('<Button-1>', self.disconnect)


class RoomsFrame(MyFrame):
    def select_room(self, event, *args, **kwargs):
        global sock, username
        try:
            self.selected_room = self.rooms.get(self.rooms.curselection()[0])
            if self.selected_room:
                self.master.send_message_frame.place(x=220, y=480)
                self.master.bind('<Return>',
                                 self.master.send_message_frame.printer)
                self.master.addroom_frame.place_forget()
                self.master.delroom_frame.place_forget()
                self.master.changestatus_frame.place_forget()
                self.master.deluser_frame.place_forget()
                self.master.show_chat_frame()
                self.master.themes_frame.place_forget()
        except IndexError:
            pass

    def __init__(self, *args, **kwargs):
        super(RoomsFrame, self).__init__()

        self.selected_room = None

        self.label = MyLabel(self, text='rooms')
        self.label.pack(side=TOP)

        self.rooms = MyListbox(self, height=30, width=24)
        self.rooms.pack(side=LEFT)
        self.rooms.bind('<<ListboxSelect>>', self.select_room)

        self.scrollbar = MyScrollbar(self, command=self.rooms.yview)
        self.rooms.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)


class ChatFrame(MyFrame):
    def __init__(self, *args, **kwargs):
        super(ChatFrame, self).__init__()

        label = MyLabel(self, text='messages')
        label.pack(side=TOP)

        self.messages = MyListbox(self, height=20, width=70)
        self.messages.pack(side=LEFT)

        self.scrollbar = MyScrollbar(self, command=self.messages.yview)
        self.messages.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)


class InfoFrame(MyFrame):
    def __init__(self, *args, **kwargs):
        super(InfoFrame, self).__init__()

        label = MyLabel(self, text='general info')
        label.pack(side=TOP)

        self.messages = MyListbox(self, height=2, width=70)
        self.messages.pack(side=LEFT)

        self.scrollbar = MyScrollbar(self, command=self.messages.yview)
        self.messages.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)


class SendMessageFrame(MyFrame):
    def but_bind(self, *args, **kwargs):
        self.button_send_message.bind('<Button-1>', self.printer)
        self.master.bind('<Return>', self.printer)

    def printer(self, event):
        if len(self.entry.get()) < 61:
            if self.entry.get() != '':
                global sock, server_addr, username
                send_message(sock, self.entry, username,
                             self.master.rooms_frame.selected_room, self.master)
                self.entry.delete(0, END)
        else:
            info(self.master.info_frame.messages, '*****message up to 60 characters*****')

    def __init__(self, *args, **kwargs):
        super(SendMessageFrame, self).__init__()

        self.label = MyLabel(self, text='enter the message:')
        self.label.pack()

        self.entry = MyEntry(self, width=70)
        self.entry.pack()

        self.button_send_message = MyButton(self, text='send message')
        self.button_send_message.pack()


class SignupFrame(MyFrame):
    def frame_bind(self, event, *args, **kwargs):
        self.button_signup.bind('<Button-1>', self.signup)
        self.master.bind('<Return>', self.signup)

    def signup(self, event, *args, **kwargs):
        global username, sock, server_addr

        create_user(self, sock, server_addr)

        if self.label_answer['text'] == 'success':
            self.signin(self)

    def signin(self, event, *args, **kwargs):
        self.master.signin_frame.entry_username.insert(0, self.entry_username.get())
        self.master.signin_frame.entry_password.insert(0, self.entry_password.get())

        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_confirm_password.delete(0, END)

        self.place_forget()
        self.master.signin_frame.place(x=320, y=250)
        self.master.signin_frame.frame_bind(self.master.signin_frame)

    def __init__(self, *args, **kwargs):
        super(SignupFrame, self).__init__()

        self.rooms_listbox = args[0].rooms_frame.rooms

        label_username = MyLabel(self, text='enter your username:')
        label_username.pack()

        self.entry_username = MyEntry(self)
        self.entry_username.pack()

        label_password = MyLabel(self, text='enter your password:')
        label_password.pack()

        self.entry_password = MyEntry(self, show='*')
        self.entry_password.pack()

        label_confirm_password = MyLabel(self, text='confirm your password:')
        label_confirm_password.pack()

        self.entry_confirm_password = MyEntry(self, show='*')
        self.entry_confirm_password.pack()

        self.button_signup = MyButton(self, text='signup')
        self.button_signup.pack()

        label_or = MyLabel(self, text='OR')
        label_or.pack()

        self.button_signin = MyButton(self, text='signin')
        self.button_signin.pack()

        self.label_answer = MyLabel(self, bg='black')
        self.label_answer.pack()

        self.button_signin.bind('<Button-1>', self.signin)


class SigninFrame(MyFrame):
    def frame_bind(self, event, *args, **kwargs):
        self.button_signin.bind('<Button-1>', self.signin)
        self.master.bind('<Return>', self.signin)

    def signin(self, event, *args, **kwargs):
        global username, sock, server_addr

        username = self.entry_username.get()
        password = self.entry_password.get()

        self.master.send_message_frame.but_bind()

        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)

        self.rooms = connect_to_server(self,
                                       server_addr, sock, username, password)
        if self.rooms:
            self.place_forget()

            create_chat_frames(self.rooms, self.rooms_listbox,
                               self.master, ChatFrame)
            self.master.show_frames()

            add_room_history(sock, username, self.master)

            messages_thread(sock, self.master.rooms_frame)

    def signup(self, event, *args, **kwargs):
        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)

        self.place_forget()
        self.master.signup_frame.place(x=320, y=250)
        self.master.signup_frame.frame_bind(self.master.signup_frame)

    def __init__(self, *args, **kwargs):
        super(SigninFrame, self).__init__()

        self.rooms_listbox = args[0].rooms_frame.rooms

        label_username = MyLabel(self, text='enter your username:')
        label_username.pack()

        self.entry_username = MyEntry(self)
        self.entry_username.pack()

        label_password = MyLabel(self, text='enter your password:')
        label_password.pack()

        self.entry_password = MyEntry(self, show='*')
        self.entry_password.pack()

        self.button_signin = MyButton(self, text='signin')
        self.button_signin.pack()

        label_or = MyLabel(self, text='OR')
        label_or.pack()

        self.button_signup = MyButton(self, text='signup')
        self.button_signup.pack()

        self.label_answer = MyLabel(self, bg='black')
        self.label_answer.pack()

        self.button_signin.bind('<Button-1>', self.signin)
        self.master.bind('<Return>', self.signin)
        self.button_signup.bind('<Button-1>', self.signup)


class MainWindow(MyTk):
    def show_frames(self):
        self.rooms_frame.place(x=6, y=0)
        self.info_frame.place(x=220, y=0)
        self.menu_frame.place(x=120, y=590)

    def show_chat_frame(self):
        for room in self.chat_frames:
            if room != self.rooms_frame.selected_room:
                self.chat_frames[room].place_forget()
        self.chat_frames[self.rooms_frame.selected_room].place(x=220, y=60)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.menu_frame = MenuFrame(self)

        self.delroom_frame = DelroomFrame(self)
        self.addroom_frame = AddroomFrame(self)

        self.themes_frame = ThemesFrame(self)
        self.deluser_frame = DeluserFrame(self)
        self.changestatus_frame = ChangestatusFrame(self)
        self.rooms_frame = RoomsFrame(self)
        self.chat_frames = dict()
        self.send_message_frame = SendMessageFrame(self)
        self.info_frame = InfoFrame()
        self.signup_frame = SignupFrame(self)

        self.signin_frame = SigninFrame(self)
        self.signin_frame.place(x=320, y=250)

        self.minsize(width=810, height=650)
        self.title('Maxigram')
        self.resizable(width=False, height=False)
        self.mainloop()


if __name__ == '__main__':
    main_window = MainWindow()
