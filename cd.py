import vlc
import pycdio
import cdio

import time
import re

class Drive():
    def __init__(self):
            self.drive = cdio.Device(source='/dev/sr1', driver_id=pycdio.DRIVER_UNKNOWN)
            self.state = self.check_disc() # state is either 'disc' or 'nodisc'
    def check_disc(self):
        try:
            self.drive.get_num_tracks()
            self.state = 'disc'
        except:
            self.state = 'nodisc'
        return self.state
    def eject(self):
        self.drive.eject_media()
        self.state = 'nodisc'

class CDPlayer():
    def __init__(self):
        # vlc
        self.initialise_player()
        self.initialise_events()

        # pycdio
        self.drive = cdio.Device(source='/dev/sr1', driver_id=pycdio.DRIVER_UNKNOWN)
        self.total_tracks_len = self.get_total_tracks()
        self.total_tracks_num = len(self.total_tracks_len)
        self.track = 0
        #self.track_length = 0
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
        #self.listplayer.event_manager().event_attach(vlc.EventType.MediaListPlayerNextItemSet, self.list_player_track_changed)

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
        if self.track < self.total_tracks_num:
            self.track += 1
        else:
            self.stop() # stop playback when end reached
    #def list_player_track_changed(self, event):
    #    print(f'Track: {self.track}')
    #    self.track_length = self.get_track_length()
    #    print(self.track_length)

    def get_total_tracks(self):
        track_num = self.drive.get_num_tracks() # get total number of tracks
        track_msf = []
        for i in range(1, track_num+2):
            track_msf.append(self.drive.get_track(i).get_msf()) # get min, sec, frames of each track
        print(track_msf)
        track_len = []
        # because each msf is a string, separate out to calculate integer seconds
        for i in range(len(track_msf) - 1):
            len_current = re.split(r':', track_msf[i])
            len_next = re.split(r':', track_msf[i+1])
            min = int(len_next[0]) - int(len_current[0])
            sec = int(len_next[1]) - int(len_current[1])
            total = (min * 60) + sec # make into seconds
            track_len.append(total)
        print(track_len)
        return track_len
    #def get_track_length(self):
    #    if self.state == 'playing':
    #        time.sleep(1)
    #        total = self.get_current_time() / self.get_current_position()
    #        return total
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
        if self.track < self.total_tracks_num:
            self.track += 1
        else:
            self.tstop()
    def prev_track(self):
        if not self.state == 'playing':
            self.play_pause()
        self.listplayer.previous() 
        if self.track > 0:
            self.track -= 1
        else:
            self.track = self.total_tracks_num
    def seek_pressed(self, direction): # this function should be run repeatedly for effect
        if self.track != 0: # no seeking within opening track
            if direction == 'forward':
                k = 1 # forward
            else:
                k = -1 # rewind
            new_pos = self.get_current_position() 
            if new_pos < 0.99 and new_pos > 0.01: # stop seek when start or end of track reached
                new_pos += (k * 0.002 / self.total_tracks_len[self.track - 1]) # calculate time delta proportional to track length
                self.player.set_position(new_pos)
    def stop(self):
        self.listplayer.stop()
        self.track = 0 # reset track count when stop playing