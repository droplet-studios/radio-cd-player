import datetime
import time
import serial
import io

class View():
    def __init__(self, cd_status, cd_event, radio_status, radio_event, cont_event):
        self.display = serial.Serial('/dev/LCD', 9600, timeout=1)

        self.cd_status = cd_status
        self.cd_event = cd_event
        self.radio_status = radio_status
        self.radio_event = radio_event
        self.cont_event = cont_event # controller event

        self.event_start = 0
        self.event = None
        self.MAX_EVENT_LEN = 3
    
    def on_event(self, event, data=None):
        self.event_start = time.perf_counter()
        self.event = event
        self.event_data = data

    def off(self):
        line_1 = 'Off'
        line_2 = datetime.datetime.now().strftime("%H:%M:%S")
        self.make_final_view(line_1, line_2)

    def cd(self, state, time=0, tot_time=0, track=0, tot_track=0):
        line_1 = 'CD' # first line always includes this

        # set special icons to display
        if state is self.cd_status.PLAYING:
            icon = '(playing)'
        elif state is self.cd_status.PAUSED:
            icon = '(paused)'
        elif state is self.cd_status.FAST_FORWARD:
            icon = '(fast forward)'
        elif state is self.cd_status.REWIND:
            icon = '(rewind)'

        if state is self.cd_status.NO_DISC:
            line_2 = 'No disc'
        elif state is self.cd_status.NO_DRIVE:
            line_2 = 'No drive'
        elif state is self.cd_status.OPENING:
            line_2 = 'Opening...'
        elif state is self.cd_status.STOPPED:
            line_2 = '' # no status message to display when stopped
        else:
            line_1 = line_1 + icon + f'{track}/{tot_track}'
            line_2 = f'{time}/{tot_time}'

        self.make_final_view(line_1, line_2)

    def radio(self, state, station):
        line_1 = 'Radio'
        if state is self.radio_status.NO_NET:
            line_2 = 'No network'
        elif state is self.radio_status.STOPPED:
            line_2 = ''
        else:
            if station is not None:
                line_2 = station
            else:
                line_2 = ''
        self.make_final_view(line_1, line_2)
    
    def make_final_view(self, line_1, line_2):
        if self.event is not None:
            if time.perf_counter() < self.event_start + self.MAX_EVENT_LEN:
                if self.event is self.cd_event.EJECT:
                    line_2 = 'Disc ejected'
                elif self.event is self.radio_event.NO_PRESET:
                    line_2 = 'No preset'
                elif self.event is self.cont_event.VOL:
                    line_2 = f'Volume {self.event_data}'
                elif self.event is self.cont_event.CONFIG:
                    line_2 = self.event_data
            else:
                self.event = None

        # calculate spaces after first line so line 2 starts on second line of display
        space_count = 20 - len(line_1)
        space_string = ' ' * space_count

        self.display.write(b'\xfe\x58')
        self.display.write(line_1.encode())
        self.display.write(space_string.encode())
        self.display.write(line_2.encode())