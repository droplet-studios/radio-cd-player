import vlc
import time
import os

class CDPlayer():
    def __init__(self):
        self.initialise_player()
        self.initialise_events()
        self.track = 0

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
    def player_playing(self, event):
        print('Playing...')
    def player_paused(self, event):
        print('Paused')
    def player_stopped(self, event):
        print('Stopped')
    def player_end_reached(self, event):
        print('End reached')
    def list_player_track_changed(self, event):
        self.track += 1
        print(f'Track: {self.track}')
    """
        def list_end_reached(self, event):
        print('List end reached')
    """

    def play_pause(self):
        if self.listplayer.is_playing():
            self.listplayer.pause()
        else:
            self.listplayer.play()
    def next_track(self):
        self.listplayer.next()
    def prev_track(self):
        self.listplayer.previous()
    def stop(self):
        self.listplayer.stop()

cd = CDPlayer()
while True:
    if input() == 'p':
        cd.play_pause()
    elif input() == 'n':
        cd.next_track()
    elif input() == 'b':
        cd.prev_track()
    elif input() == 's':
        cd.stop()
"""
cd.listplayer.next()
for i in range(22):
    while cd.listplayer.get_state() == vlc.State._enum_names_[1]:
        print('opening')
        time.sleep(0.5)
    for i in range(25):
        print(f'{i}: {cd.listplayer.get_state()}')
        time.sleep(0.5)
    cd.listplayer.next()
"""

"""
print(cd.player.get_time())
cd.listplayer.next()
time.sleep(10)
print(cd.player.get_position())
"""