import vlc
import time
import datetime
import pickle

class Controller():
    def __init__(self):
        self.config = Config()
        self.radio = Radio()

class Config():
    def __init__(self):
        self.load_state()
    def load_state(self):
        try:
            with open('saved_state.pkl', 'rb') as file:
                self.presets = pickle.load(file)
                self.last_station = pickle.load(file)
                #self.mode = pickle.load(file)
                self.volume = pickle.load(file)
            self.log('Successfully loaded previous configuration')
        except FileNotFoundError or EOFError:
            self.presets = [None for i in range(6)]
            self.last_station = 0
            self.volume = 10
            self.log('Could not load previous configuration, using defaults')
    def save_state(self, presets, mode, volume):
        with open('saved_state.pkl', 'wb') as file:
            pickle.dump(presets, file)
            #pickle.dump(mode, file)
            pickle.dump(volume, file)
        self.log('Saved configuration state')
    def check_net(self):
        pass
    def log(self, message):
        with open('log.txt', 'a') as logfile:
            logfile.write(f'[{datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S")}] {message}\n')

class Preset():
    def __init__(self, url, name, num, selected):
        self.url = url
        self.name = name
        self.num = num
        self.selected = selected

class Radio():
    def __init__(self):
        self.instance = vlc.Instance()
        self.presets = []
        self.player = self.instance.media_player_new()
        
    def import_presets(self, list):
        # this should return list of presets from state file (each preset is its own object?)
        #list = ['https://wgbh-live.streamguys1.com/WCRB.mp3']
        #self.last_played = 0 # this should be dynamic
        for item in list:
            if item != None:
                self.presets.append(self.instance.media_new(item.url))
            else:
                self.presets.append(None)
        return list
    def update_last_played(self, index):
        # this should update state file to reflect last played
        pass
    def start(self, preset=None):
        if preset == None:
            preset = self.last_played
        else:
            # set new last played
            self.last_played = preset
            self.update_last_played(preset)
        self.player.set_media(self.presets[preset])
        self.player.play()
    def stop(self):
        self.player.stop()

if __name__ == '__main__':
    """
    radio = Radio()
    radio.start()
    for i in range(10):
        print(radio.player.get_state()) # State.Ended when can't open stream, but only when opening (is there any way to raise exception?)
        time.sleep(2)
    radio.stop()
    """
