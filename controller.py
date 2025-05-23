import cd
import radio
from radio import Preset # needs to be in namespace when presets are unpickled in radio module
import view

from enum import Enum
import datetime
import time
import threading

class Mode(Enum):
    OFF = 0
    RADIO = 1
    CD = 2

class Events(Enum):
    VOL = 0

class Controller():
    def __init__(self):
        self.cd_player = cd.CDPlayer()
        self.radio = radio.Radio()
        self.view = view.View(cd.Status, cd.Events, radio.Status, radio.Events)

        self.cd_player.attach(self)
        self.radio.attach(self)

        self.mode = Mode.OFF

    def update(self, event, details=None):
        if event is cd.Events.NO_DRIVE:
            self.log('No disc drive found')
        if event is cd.Events.STOPPED:
            self.mode = Mode.OFF
            # stopped event doesn't need to be sent to view (because just changes mode to off)
        elif event is cd.Events.EJECT:
            self.view.on_event(event) # send event to view
            self.mode = Mode.OFF
        elif event is radio.Events.NO_DEFAULT:
            self.log('Using default presets')
        elif event is radio.Events.UNEX_STOP:
            self.view.on_event(event) # send event to view
            self.mode = Mode.OFF
            self.log(f'Preset {details} stopped unexpectedly')
        elif event is radio.Events.NET_LOST:
            self.log('Network disconnected')
        elif event is radio.Events.NO_PRESET:
            self.view.on_event(event)
        
    def log(self, event):
        with open('log.txt', 'a') as logfile:
            logfile.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {event}\n')

    # each function corresponds to physical button
    def start_radio(self): # switched mode to radio
        if self.mode is not Mode.RADIO:
            self.cd_player.stop()
            self.mode = Mode.RADIO
        self.radio.start()

    # how to generate functions without writing same thing?
    def preset_one(self):
        if self.mode is Mode.RADIO:
            self.radio.start(0)

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
                if self.cd_player.state is not cd.Status.NO_DISC and self.cd_player.state is not cd.Status.NO_DRIVE:
                    cur_time = self.format_time(self.cd_player.get_current_time())
                    tot_time = self.format_time(self.cd_player.get_current_len())
                    track = self.cd_player.cur_track
                    tot_track = self.cd_player.cd.total_tracks_num
                    self.view.cd(state, cur_time, tot_time, track, tot_track)
                else:
                    self.view.cd(state) # when no disc or no drive, then other variables don't exist because disc not initialised
            elif self.mode is Mode.RADIO:
                print(self.radio.player.get_state())
                state = self.radio.state
                station = self.radio.presets[self.radio.last_station].name
                self.view.radio(state, station)
            time.sleep(1)
    def format_time(self, time): # move to controller?
        """
        Formats time given in seconds to mm:ss format
        """
        minutes = int(time // 60)
        seconds = int(time - (minutes * 60))
        minutes = str(minutes)
        seconds = str(seconds)
        if len(minutes) == 1:
            minutes = '0' + minutes # for single digit case, add placeholder zero
        if len(seconds) == 1:
            seconds = '0' + seconds
        res = f'{minutes}:{seconds}'
        return res
    
    def controls(self):
        while True:
            res = input()
            if res == 'r':
                controller.start_radio()
            elif res == 'p1':
                controller.preset_one()
            elif res == 'p':
                controller.play_pause()
            elif res == 'n':
                controller.skip_forward()
            elif res == 'b':
                controller.skip_backwards()
            elif res == 'ff':
                controller.fast_forward()
            elif res == 'rw':
                controller.rewind()
            elif res == 's':
                controller.stop()
            elif res == 'e':
                controller.eject()

if __name__ == '__main__':
    controller = Controller()
    controls = threading.Thread(target=controller.controls)
    upd_view = threading.Thread(target=controller.update_view)
 
    threads = [controls, upd_view]
 
    for thread in threads:
        thread.start()
    