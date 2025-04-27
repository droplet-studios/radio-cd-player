import vlc
from time import sleep

class Radio():
    def __init__(self):
        self.instance = vlc.Instance()
        self.presets = []
        self.player = self.instance.media_player_new()
        for item in self.import_presets():
            self.presets.append(self.instance.media_new(item))
    def import_presets(self):
        # this should return list of presets from state file (each preset is its own object?)
        list = ['https://wgbh-live.streamguys1.com/WCRB.mp3']
        self.last_played = 0 # this should be dynamic
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
    radio = Radio()
    radio.start()
    while True:
        print(radio.player.get_state()) # State.Ended when can't open stream, but only when opening (is there any way to raise exception?)
        sleep(2)