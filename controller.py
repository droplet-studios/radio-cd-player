import radio
import cd
import view

import sys
import threading
import time

class PresetNotSet(Exception):
    def __init__(self, message='PresetNotSet: There is no preset set for the specified index'):
        self.message = message
        super().__init__(message)

class NoDisc(Exception):
    def __init__(self, message='NoDisc: There is no disc in the drive'):
        self.message = message
        super().__init__(message)

class Controller():
    def __init__(self):
        self.mode = 'off'
        self.radio = radio.Radio() # only need one instance of radio
        self.radio_config = radio.Config(self.radio)
        self.drive = cd.Drive()
        self.view = view.View()
        
        self.special = ''
        self.special_msg_timeout = 3

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

    def play_pause(self): # switches mode to cd
        if self.mode != 'cd':
            self.radio.stop()
            if self.drive.check_disc() == 'disc':
                self.cd = cd.CDPlayer()
                self.mode = 'cd'
                self.cd.play_pause()
            else:
                self.special = 'No disc'
        else: # mode is 'cd' only when a disc is already playing
            self.cd.play_pause()

    def skip_forward(self):
        if self.mode == 'cd':
            self.cd.next_track()

    def skip_backwards(self):
        if self.mode == 'cd':
            self.cd.prev_track()

    # change later to not have built-in loop
    def fast_forward(self):
        if self.mode == 'cd':
            for i in range(1000):
                self.cd.seek_pressed(1)
    
    def rewind(self):
        if self.mode == 'cd':
            for i in range(1000):
                self.cd.seek_pressed(-1)
    
    def stop(self):
        if self.mode == 'radio':
            self.radio.stop()
        elif self.mode == 'cd':
            self.cd.stop()
        self.mode = 'off'

    def eject(self):
        if self.mode == 'cd':
            self.stop()
            self.mode = 'off'
        self.drive.eject()
        self.special = 'Disc ejected'

    def controls(self): # replace with real button bindings
        while True:
            res = input()
            if res == 'r':
                self.start_radio()
            elif res == 'p1':
                self.preset_one()
            elif res == 'p':
                self.play_pause()
            elif res == 'n':
                self.skip_forward()
            elif res == 'b':
                self.skip_backwards()
            elif res == 'ff':
                self.fast_forward()
            elif res == 'rw':
                self.rewind()
            elif res == 's':
                self.stop()
            elif res == 'e':
                self.eject()
            elif res == 'q':
                sys.exit()

    def update_view(self):
        while True:
            self.view.label0.destroy()
            self.view.label1.destroy()

            self.view.current_state(self.mode)

            if self.special != '':
                if self.special_msg_timeout > 0:
                    self.view.special(self.special)
                    self.special_msg_timeout -= 1
                else:
                    self.special = ''
                    self.special_msg_timeout = 3
            elif self.mode == 'off':
                self.view.stopped()
            elif self.mode == 'radio':
                cur = self.radio.current
                self.view.radio(self.radio.presets[cur].name)
            elif self.mode == 'cd':
                cur_time = self.cd.get_current_time()
                pos = self.cd.get_current_position()
                track = self.cd.track
                tot = self.cd.total_tracks_num
                self.view.cd(cur_time, pos, track, tot)
            time.sleep(1)

# use multithreading to run controls() and update_view() concurrently
# this might not be necessary if gpiozero functions are non-blocking
if __name__ == '__main__':
    cont = Controller()
    controls = threading.Thread(target=cont.controls)
    upd_view = threading.Thread(target=cont.update_view)
    threads = [controls, upd_view]
    for thread in threads:
        thread.start()
    cont.view.root.mainloop()