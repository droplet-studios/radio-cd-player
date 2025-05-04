import datetime
import time

class View():
    def __init__(self, cd_status, cd_event, radio_status, radio_event):
        self.cd_status = cd_status
        self.cd_event = cd_event
        self.radio_status = radio_status
        self.radio_event = radio_event

        self.event_start = 0
        self.event = None
        self.MAX_EVENT_LEN = 3
    
    def on_event(self, event):
        self.event_start = time.perf_counter()
        self.event = event

    def off(self):
        line_1 = 'Off'
        line_2 = datetime.datetime.now().strftime("%H:%M:%S")
        self.make_final_view(line_1, line_2)

    def cd(self, state, time, tot_time, track, tot_track):
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
            line_2 = station
        self.make_final_view(line_1, line_2)
    
    def make_final_view(self, line_1, line_2):
        if self.event is not None:
            if time.perf_counter < self.event_start + self.MAX_EVENT_LEN:
                if self.event is self.cd_event.EJECT:
                    line_2 = 'Disc ejected'
                elif self.event is self.radio_event.NO_PRESET:
                    line_2 = 'No preset'
                elif self.event is self.radio_event.NO_OPEN:
                    line_2 = 'Cannot open'
            else:
                self.event = None
        res = f'{line_1}\n{line_2}'
        print(res, end='\r')
        return res