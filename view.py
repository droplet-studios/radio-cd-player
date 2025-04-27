import datetime

class View():
    def stopped(self):
        time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f'{time} Stopped', end='\r')

    def radio(self, station):
        print(f'Playing station {station}', end='\r')

    def cd(self, time, position, track, total_track):
        print(f'{time} ({position}%) \t {track}/{total_track}', end='\r')