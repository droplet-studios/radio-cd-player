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
        self.vlc_state = self.player.get_state()

        self.state = Status.STOPPED
        self.prev_state = Status.STOPPED # store previous state when state changes to no net

        threading.Thread(target=self.status_check).start() # start network checks in background

        self.presets = [] # Preset objects
        self.vlc_presets = [] # VLC media objects
        self.last_station = 0

        self.load_state()

        self.set_preset('https://ipm.streamguys1.com/wfiu1-mp3', 'WFIU 1', 0)
        self.set_preset('https://ipm.streamguys1.com/wfiu2-mp3', 'WFIU 2', 1)
        self.set_preset('https://audio.wgbh.org/classical-mp3', 'WCRB', 2, True)
        self.set_preset('http://ice-1.streamhoster.com:80/lv_wqed--893', 'WQED', 3)
        self.set_preset('https://ais-sa3.cdnstream1.com/2556_128.mp3?uuid=hx96mnyx', 'WESA', 4)

        for preset in self.presets:
            print(f'{preset.url} {preset.name} {preset.num} {preset.selected}')

    def attach(self, observer):
        self.observers.append(observer)
    def notify(self, event, details=None):
        for observer in self.observers:
            observer.update(event, details)

    def status_check(self): # does threading work?
        """
        Network and player status check runs as a continuous loop in background (because VLC doesn't)
        """
        while True:
            # what is the VLC's current state?
            self.vlc_state = self.player.get_state()
            
            # is player still playing?
            if self.vlc_state == 6 and self.state is Status.PLAYING: # when VLC status is not reflected in this program's state (6 is vlc code for 'Ended' state)
                self.notify(Events.UNEX_STOP, self.last_station)
                self.stop() # stop manually

            # is network still connected?
            try:
                print(requests.get('https://google.com/', timeout=5))
                if self.state is Status.NO_NET: # run only right after reconnect
                    print(f'Prev: {self.prev_state}')
                    self.state = Status.STOPPED # reset state
                    if self.prev_state is Status.STOPPED:
                        pass # do nothing (because state is already STOPPED)
                    elif self.prev_state is Status.PLAYING:
                        self.start()
            except Exception as err:
                if self.state is not Status.NO_NET:
                    self.prev_state = self.state # save state before lost net connection
                    self.notify(Events.NET_LOST)
                self.stop()
                self.state = Status.NO_NET # change status because stop() sets state to STOPPED

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
    def set_preset(self, url, name, num, last_sel=False):
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
        if preset == None: # when no index specified on function call, use last played
            preset = self.last_station
            print('last st')
        if self.presets[preset] == None: # when preset not saved at specified index
            self.notify(Events.NO_PRESET)
        if self.state is not Status.NO_NET: # when there is network connection, go ahead and play
            self.player.stop() # this allows to reset open stream and re-open (when necessary)
            self.set_last_station(preset)
            self.player.play()
            self.state = Status.PLAYING
            print(f'radio start: {preset}')

            # handle cases where VLC inexplicably hangs on opening stream
            start = time.perf_counter()
            while self.vlc_state == 1: # when state is 'opening' (represented by 1)
                if time.perf_counter() > start + 5: # wait 5 seconds of opening, then close stream
                    self.stop()
                    self.notify(Events.UNEX_STOP, self.last_station)

    def stop(self):
        self.player.stop()
        self.state = Status.STOPPED

if __name__ == '__main__':
    radio = Radio()

    # run this to manually set presets (until I can make a web control interface)
    radio.set_preset('https://ipm.streamguys1.com/wfiu1-mp3', 'WFIU 1', 0)
    radio.set_preset('https://ipm.streamguys1.com/wfiu2-mp3', 'WFIU 2', 1)
    radio.set_preset('https://audio.wgbh.org/classical-mp3', 'WCRB', 2, True)
    radio.set_preset('http://ice-1.streamhoster.com:80/lv_wqed--893', 'WQED', 3)
    radio.set_preset('https://ais-sa3.cdnstream1.com/2556_128.mp3?uuid=hx96mnyx', 'WESA', 4)