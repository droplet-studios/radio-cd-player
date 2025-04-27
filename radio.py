import vlc
import time
import datetime
import pickle

class Config():
    def __init__(self, radio):
        self.radio = radio
        self.load_state()
    def load_state(self):
            try:
                with open('radio_saved_state.pkl', 'rb') as file:
                    self.presets = pickle.load(file)
                    self.last_station = pickle.load(file)
                    self.volume = pickle.load(file)
                    #self.log('Successfully loaded previous configuration')
            except (EOFError, FileNotFoundError):
                self.presets = [None for i in range(6)]
                self.last_station = 0
                self.volume = 10 # move volume config to controller class
                #self.log('Could not load previous configuration, using defaults')
                self.save_state()
            self.radio.import_presets(self.presets)
    def save_state(self):
        with open('radio_saved_state.pkl', 'wb') as file:
            pickle.dump(self.presets, file)
            pickle.dump(self.last_station, file)
            pickle.dump(self.volume, file)
        #self.log('Saved configuration state')
    def set_preset(self, url, name, num):
        new_preset = Preset(url, name, num, False)
        self.presets[num] = new_preset
        self.radio.import_presets(self.presets)
        #self.log(f'Updated preset at index {num} to {url}')
        self.save_state()
    def set_last_station(self, num):
        self.last_station = num
        #self.log(f'Updated last station to index {num}')
        self.save_state()
    def check_net(self): # make own class? or move
        pass
    # should this be put somewhere else? Perhaps config class
    def log(self, message): # move
        with open('log.txt', 'a') as logfile:
            logfile.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {message}\n')

class Preset():
    def __init__(self, url, name, num, selected):
        self.url = url
        self.name = name
        self.num = num
        self.selected = selected

class PresetNotSet(Exception):
    def __init__(self, message='PresetNotSet: There is no preset set for the specified index'):
        self.message = message
        super().__init__(message)

class Radio():
    def __init__(self):
        self.instance = vlc.Instance()
        self.presets = []
        self.player = self.instance.media_player_new()
        self.current = 0 # contains index of current station being played
    def import_presets(self, list):
        for item in list:
            if item != None:
                self.presets.append(self.instance.media_new(item.url))
            else:
                self.presets.append(None)
        return list
    def start(self, preset):
        if self.presets[preset] == None:
            raise PresetNotSet
        else:
            self.current = preset
            self.player.set_media(self.presets[preset])
            self.player.play()
    def stop(self):
        self.player.stop()