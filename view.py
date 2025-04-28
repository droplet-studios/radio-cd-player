import datetime
import tkinter

class View():
    def __init__(self):
        self.root = tkinter.Tk()
        self.label0 = tkinter.Label()
        self.label1 = tkinter.Label()

    def current_state(self, state):
        self.label0 = tkinter.Label(self.root, text=state)
        self.label0.pack()

    def special(self, msg):
        self.label1 = tkinter.Label(self.root, text=msg)
        self.label1.pack()

    def stopped(self):
        time = datetime.datetime.now().strftime("%H:%M:%S")
        #print(f'{time} Stopped', end='\r')
        self.label1 = tkinter.Label(self.root, text=f'{time} Stopped')
        self.label1.pack()

    def radio(self, station):
        #print(f'Playing station {station}', end='\r')
        self.label1 = tkinter.Label(self.root, text=f'Playing station {station}')
        self.label1.pack()

    def cd(self, time, position, track, total_track):
        #print(f'{time} ({position}%) \t {track}/{total_track}', end='\r')
        self.label1 = tkinter.Label(self.root, text=f'{time} ({position}%) \t {track}/{total_track}')
        self.label1.pack()