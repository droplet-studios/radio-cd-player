import vlc
import time
import os

class CDPlayer():
    def __init__(self):
        self.initialise_player()
        self.initialise_events()
        self.track = 0
        self.track_length = 0
        self.state = 'stopped'

    def initialise_player(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.medialist = self.instance.media_list_new()
        self.listplayer = self.instance.media_list_player_new()
        self.listplayer.set_media_player(self.player)
        self.medialist.add_media('cdda:///dev/sr1')
        self.listplayer.set_media_list(self.medialist)
    def initialise_events(self):
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerOpening, self.player_opening)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.player_playing)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPaused, self.player_paused)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerStopped, self.player_stopped)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.player_end_reached)
        self.listplayer.event_manager().event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.list_player_track_changed)
        #self.medialist.event_manager().event_attach(vlc.EventType.MediaListEndReached, self.list_end_reached)

    def player_opening(self, event):
        print('Opening...')
        self.state = 'opening'
    def player_playing(self, event):
        print('Playing...')
        self.state = 'playing'
    def player_paused(self, event):
        print('Paused')
        self.state = 'paused'
    def player_stopped(self, event):
        print('Stopped')
        self.state = 'stopped'
    def player_end_reached(self, event):
        print('End reached')
        self.track += 1
    def list_player_track_changed(self, event):
        print(f'Track: {self.track}')
        self.track_length = self.get_track_length()
        print(self.track_length)
        
    def get_track_length(self):
        if self.state == 'playing':
            time.sleep(1)
            total = self.get_current_time() / self.get_current_position()
            return total
    def get_current_time(self):
        return self.player.get_time() / 1000
    def get_current_position(self):
        return self.player.get_position()

    def play_pause(self):
        if self.player.is_playing():
            self.listplayer.pause()
        else:
            self.listplayer.play()
    def next_track(self):
        if not self.state == 'playing':
            print('start')
            self.play_pause()
        self.listplayer.next()
        self.track += 1
    def prev_track(self):
        if not self.state == 'playing':
            self.play_pause()
        self.listplayer.previous()
        self.track -= 1
    def stop(self):
        self.listplayer.stop()

cd = CDPlayer()
cd.play_pause()
while True:
    print(f'Track {cd.track}: {cd.get_current_time()} / {cd.track_length} ({cd.get_current_position() * 100}%)', end='\r')
    time.sleep(1)
"""
while True:
    print(cd.player.get_state())
    if input() == 'p':
        cd.play_pause()
    elif input() == 'n':
        cd.next_track()
    elif input() == 'b':
        cd.prev_track()
    elif input() == 's':
        cd.stop()
"""