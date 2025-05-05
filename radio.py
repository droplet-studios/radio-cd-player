from enum import Enum

class Status(Enum):
    NO_NET = -1
    STOPPED = 0
    PLAYING = 1

class Events(Enum):
    NO_PRESET = -2
    NO_OPEN = -1
    STOPPED = 0

class Radio():
    def __init__(self):
        self.observers = []

        self.state = Status.STOPPED

    def attach(self, observer):
        self.observers.append(observer)
    def notify(self, event):
        for observer in self.observers:
            observer.update(event)

    def stop(self):
        pass