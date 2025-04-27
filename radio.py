import vlc
import time
import datetime
import pickle

class Controller():
    def __init__(self):
        self.mode = 'off'
        self.radio = Radio()
        self.config = Config(self.radio)
    # each function corresponds to physical button
    def start_radio(self):
        self.mode = 'radio'
        try:
            self.radio.start(self.config.last_station)
        except PresetNotSet:
            print('Preset not set')
        #print(type(self.radio.player.get_state()))
    # how to generate functions without writing same thing?
    def preset_one(self):
        if self.radio.player.is_playing():
            print('Setting preset to 1')
            self.config.set_last_station(0)
            try:
                self.radio.start(0)
            except PresetNotSet:
                print('Preset not set')
    def stop(self):
        if self.mode == 'radio':
            self.radio.stop()

class Config():
    def __init__(self, radio):
        self.radio = radio
        self.load_state()
    def load_state(self):
            with open('saved_state.pkl', 'rb') as file:
                try:
                    self.presets = pickle.load(file)
                    self.last_station = pickle.load(file)
                    self.volume = pickle.load(file)
                    self.log('Successfully loaded previous configuration')
                except (EOFError, FileNotFoundError):
                    self.presets = [None for i in range(6)]
                    self.last_station = 0
                    self.volume = 10
                    self.log('Could not load previous configuration, using defaults')
                    self.save_state()
            self.radio.import_presets(self.presets)
    def save_state(self):
        with open('saved_state.pkl', 'wb') as file:
            pickle.dump(self.presets, file)
            pickle.dump(self.last_station, file)
            pickle.dump(self.volume, file)
        self.log('Saved configuration state')
    def set_preset(self, url, name, num):
        new_preset = Preset(url, name, num, False)
        self.presets[num] = new_preset
        self.radio.import_presets(self.presets)
        self.log(f'Updated preset at index {num} to {url}')
        self.save_state()
    def set_last_station(self, num):
        self.last_station = num
        self.log(f'Updated last station to index {num}')
        self.save_state()
    def check_net(self):
        pass
    # should this be put somewhere else? Perhaps config class
    def log(self, message):
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
            self.player.set_media(self.presets[preset])
            self.player.play()
    def stop(self):
        self.player.stop()

if __name__ == '__main__':
    """
    radio = Radio()
    config = Config(radio)
    #config.set_preset('https://wgbh-live.streamguys1.com/WCRB.mp3', 'WCRB', 0)
    radio.start(1)
    time.sleep(10)
    radio.stop()
    """
    cont = Controller()
    cont.start_radio()
    time.sleep(3)
    cont.preset_one()
    time.sleep(10)
