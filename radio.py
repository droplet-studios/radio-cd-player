from enum import Enum
import requests
import threading
import pickle
import time
import vlc

class Status(Enum):
    NO_NET = -1
    STOPPED = 0
    PLAYING = 1

class Events(Enum):
    NO_DEFAULT = -4
    UNEX_STOP = -3
    NET_LOST = -2
    NO_PRESET = -1

class Preset():
    def __init__(self, url, name, num, selected):
        self.url = url
        self.name = name
        self.num = num
        self.selected = selected

class Radio():
    def __init__(self):
        self.observers = []

        self.init_vlc()
        self.state = Status.STOPPED

        threading.Thread(target=self.status_check).start() # start network checks in background

        self.presets = [] # Preset objects
        self.vlc_presets = [] # VLC media objects
        self.last_station = 0

        self.load_state()

    def attach(self, observer):
        self.observers.append(observer)
    def notify(self, event, details=None):
        print(event)
        for observer in self.observers:
            observer.update(event, details)

    def status_check(self): # does threading work?
        """
        Network and player status check runs as a continuous loop in background (because VLC doesn't)
        """
        while True:
            # is player still playing?
            if self.player.get_state() == 6 and self.state is Status.PLAYING: # when VLC status is not reflected in this program's state (6 is vlc code for 'Ended' state)
                self.notify(Events.UNEX_STOP, self.last_station)
                self.stop() # stop manually

            # is network still connected?
            try:
                requests.get('https://google.com/', timeout=5)
                if self.state is not Status.PLAYING:
                    self.state = Status.STOPPED # reset to normal state if coming from no network connection
            except Exception as err:
                if self.state is not Status.NO_NET:
                    self.notify(Events.NET_LOST)
                self.stop()
                self.state = Status.NO_NET

            time.sleep(1)

    def init_vlc(self):
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()

    def import_presets(self):
        """
        Takes list of Preset objects and converts into list of VLC media object
        """
        self.vlc_presets = [] # reset vlc preset list
        for item in self.presets:
            if item != None:
                self.vlc_presets.append(self.instance.media_new(item.url))
            else:
                self.vlc_presets.append(None)
    def load_state(self):
            try:
                with open('radio_saved_state.pkl', 'rb') as file:
                    self.presets = pickle.load(file)
                    self.last_station = pickle.load(file)
            except (EOFError, FileNotFoundError):
                # set default values when no saved state
                self.notify(Events.NO_DEFAULT)
                self.presets = [None for i in range(5)] # five total presets
                self.last_station = 0
                self.save_state()
            self.import_presets()
    def save_state(self):
        """
        Updates saved list of presets and last played preset
        """
        with open('radio_saved_state.pkl', 'wb') as file:
            pickle.dump(self.presets, file)
            pickle.dump(self.last_station, file)
        #self.log('Saved configuration state')
    def set_preset(self, url, name, num):
        """
        Adds new preset to list of presets and calls save_state() to save it
        """
        new_preset = Preset(url, name, num, False)
        self.presets[num] = new_preset
        self.import_presets()
        #self.log(f'Updated preset at index {num} to {url}')
        self.save_state()
    def set_last_station(self, num):
        """
        Updates the last played station variable and calls save_state() to save it
        """
        self.last_station = num
        self.player.set_media(self.vlc_presets[self.last_station])
        #self.log(f'Updated last station to index {num}')
        self.save_state()
    
    def start(self, preset=None):
        if not preset: # when no index specified on function call, use last played
            preset = self.last_station
        if self.presets[preset] == None: # when preset not saved at specified index
            self.notify(Events.NO_PRESET)
        elif self.state is not Status.NO_NET: # when there is network connection, go ahead and play
            self.player.stop() # this allows to reset open stream and re-open (when necessary)
            self.set_last_station(preset)
            self.player.play()
            self.state = Status.PLAYING

            # handle cases where VLC inexplicably hangs on opening stream
            start = time.perf_counter()
            while self.player.get_state() == 1: # when state is 'opening' (represented by 1)
                if time.perf_counter() > start + 5: # wait 5 seconds of opening, then close stream
                    self.stop()
                    self.notify(Events.UNEX_STOP, self.last_station)

    def stop(self):
        self.player.stop()
        self.state = Status.STOPPED

if __name__ == '__main__':
    radio = Radio()
    radio.set_preset('http://ice-1.streamhoster.com:80/lv_wqed--893', 'WQED', 0)
    radio.start(0)
    time.sleep(20)