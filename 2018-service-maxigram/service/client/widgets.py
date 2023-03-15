from tkinter import Tk, Frame, Button, Label, Listbox, Scrollbar, Entry, Checkbutton, Radiobutton
from config import main_color, sand_color, bd


class MyTk(Tk):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.configure(bg=main_color)

        for frame in self.winfo_children():
            frame.change_theme(main_color, sand_color, bd)


    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        Tk.__init__(self, screenName, baseName, className, useTk, sync, use)

        #self.minsize(width=800, height=600)
        self.title('Maxigram')
        self.configure(bg=main_color)
        self.resizable(width=False, height=False)


class MyFrame(Frame):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.configure(bg=main_color)

        for widget in self.winfo_children():
            widget.change_theme(main_color, sand_color, bd)

        if hasattr(self, 'checkbuttons'):
            for checkbutton in self.checkbuttons:
                checkbutton['check'].change_theme(main_color, sand_color, bd)


    def __init__(self, master=None, cnf={}, **kw):
        Frame.__init__(self, master, cnf, **kw)

        self.configure(bg=main_color)


class MyButton(Button):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.config(bd=bd, bg=main_color, fg=sand_color,
                    activeforeground=main_color, activebackground=sand_color)


    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)

        self.config(bd=bd, bg=main_color, fg=sand_color,
                    activeforeground=main_color, activebackground=sand_color)


class MyLabel(Label):
    def change_theme(self, main_color, sand_color, *args, **kwargs):
        self.config(bg=main_color, fg=sand_color, bd=bd)


    def __init__(self, master=None, cnf={}, **kw):
        Label.__init__(self, master, cnf, **kw)

        self.config(bg=main_color, fg=sand_color)


class MyListbox(Listbox):
    def change_theme(self, main_color, sand_color, *args, **kwargs):
        self.config(bg=main_color, fg=sand_color, selectbackground=sand_color)


    def __init__(self, master, cnf={}, **kw):
        Listbox.__init__(self, master, cnf, **kw)

        self.config(bg=main_color, fg=sand_color, selectbackground=sand_color)


class MyScrollbar(Scrollbar):
    def change_theme(self, main_color, sand_color, *args, **kwargs):
        self.config(bg=main_color, activebackground=sand_color)


    def __init__(self, master=None, cnf={}, **kw):
        Scrollbar.__init__(self, master, cnf, **kw)

        self.config(bg=main_color, activebackground=sand_color)


class MyEntry(Entry):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.config(bd=bd, insertbackground=sand_color, bg=main_color, fg=sand_color)


    def __init__(self, master=None, cnf={}, **kw):
        Entry.__init__(self, master, cnf, **kw)

        self.config(bd=bd, insertbackground=sand_color, bg=main_color, fg=sand_color)


class MyCheckbutton(Checkbutton):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.config(activebackground=sand_color, activeforeground=main_color, 
            bd=bd, bg=main_color, fg=sand_color, selectcolor=main_color)


    def __init__(self, master=None, cnf={}, main_color=main_color, sand_color=sand_color, bd=bd, **kw):
        Checkbutton.__init__(self, master, cnf, **kw)

        self.config(activebackground=sand_color, activeforeground=main_color, 
            bd=bd, bg=main_color, fg=sand_color, onvalue=1, offvalue=0, selectcolor=main_color)


class MyRadiobutton(Radiobutton):
    def change_theme(self, main_color, sand_color, bd, *args, **kwargs):
        self.config(bd=bd, bg=main_color, fg=sand_color, activebackground=sand_color,
            activeforeground=main_color, selectcolor=main_color)


    def __init__(self, master=None, cnf={}, main_color=main_color, sand_color=sand_color, bd=bd, **kw):
        Radiobutton.__init__(self, master, cnf, **kw)

        self.config(bd=bd, bg=main_color, fg=sand_color, activebackground=sand_color,
            activeforeground=main_color, selectcolor=main_color, width=7, anchor='w')
