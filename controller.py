import cd
import radio
import view

from enum import Enum
import datetime

class Mode(Enum):
    OFF = 0
    RADIO = 1
    CD = 2

class Events(Enum):
    VOL = 0

class Logger():
    def log(self, event):
        with open('log.txt', 'a') as logfile:
            logfile.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {event}\n')

class Controller():
    def __init__(self):
        self.cd_player = cd.CDPlayer()
        self.radio = radio.Radio()
        self.view = view.View(cd.Status, cd.Events, radio.Status, radio.Events)

        self.logger = Logger()

        self.cd_player.attach(self)
        self.radio.attach(self)
        self.device.attach(self)

        self.mode = Mode.OFF

    def update(self, event):
        if event is cd.Events.STOPPED:
            self.mode = Mode.OFF
            # stopped event doesn't need to be sent to view (because just changes mode to off)
        elif event is cd.Events.EJECT:
            self.mode = Mode.OFF
            self.view.on_event(event) # send event to view
        #self.logger.log()
        
    """
    # each function corresponds to physical button
    def start_radio(self): # switched mode to radio
        if self.mode != 'radio':
            try:
                self.cd.stop()
            except:
                print('No CD player instance to stop; continuing...')
            try:
                self.radio.start(self.radio_config.last_station)
                self.mode = 'radio'
            except PresetNotSet:
                print('Preset not set')
                self.special = 'Preset not set'

    # how to generate functions without writing same thing?
    def preset_one(self):
        if self.radio.player.is_playing():
            print('Setting preset to 1')
            self.radio_config.set_last_station(0)
            try:
                self.radio.start(0)
            except PresetNotSet:
                print('Preset not set')
                self.special = 'Preset not set'
    """
    def play_pause(self): # switches mode to cd
        if self.mode is not Mode.CD:
            self.radio.stop()
            self.mode = Mode.CD
        self.cd_player.play_pause()

    def skip_forward(self):
        if self.mode is Mode.CD:
            self.cd_player.next_track()

    def skip_backwards(self):
        if self.mode is Mode.CD:
            self.cd_player.prev_track()

    # change later to not have built-in loop
    def fast_forward(self):
        if self.mode is Mode.CD:
            for i in range(1000):
                self.cd_player.seek_pressed(1)
    
    def rewind(self):
        if self.mode is Mode.CD:
            for i in range(1000):
                self.cd_player.seek_pressed(-1)
    
    def stop(self):
        if self.mode is Mode.RADIO:
            self.radio.stop()
        elif self.mode is Mode.CD:
            self.cd_player.stop()
        self.mode = Mode.OFF

    def eject(self):
        if self.mode is Mode.CD:
            self.mode = Mode.OFF
        self.cd_player.eject()

    def update_view(self):
        while True:
            if self.mode is Mode.OFF:
                self.view.off()
            elif self.mode is Mode.CD:
                state = self.cd_player.state
                time = self.format_time(self.cd_player.get_current_time())
                tot_time = self.format_time(self.cd_player.get_current_len())
                track = self.cd_player.cur_track
                tot_track = self.cd_player.cd.total_tracks_num
                self.view.cd(state, time, tot_time, track, tot_track)
            elif self.mode is Mode.RADIO:
                pass

    def format_time(self, time): # move to controller?
        """
        Formats time given in seconds to mm:ss format
        """
        minutes = int(time // 60)
        seconds = int(time - (minutes * 60))
        res = f'{minutes}:{seconds}'
        return res
if __name__ == '__main__':
    controller = Controller()