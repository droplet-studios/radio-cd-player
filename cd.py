import vlc
import pycdio
import cdio
import re
from enum import Enum
import sys

DRIVE_PATH = '/dev/sr0'

class Status(Enum):
    NO_DRIVE = -2
    NO_DISC = -1
    STOPPED = 0
    OPENING = 1
    PLAYING = 2
    PAUSED = 3
    FAST_FORWARD = 4
    REWIND = 5

class Events(Enum):
    NO_DRIVE = -1
    STOPPED = 0
    EJECT = 1

class CD():
    def __init__(self, drive):
        self.drive = drive
        self.total_tracks_len = self.get_total_tracks()
        self.total_tracks_num = len(self.total_tracks_len) - 1

    def get_total_tracks(self):
        track_num = self.drive.get_num_tracks() # get total number of tracks
        track_msf = []
        for i in range(1, track_num+2):
            track_msf.append(self.drive.get_track(i).get_msf()) # get min, sec, frames of each track
        track_len = [0] # include placeholder for opening track 0
        # because each msf is a string, separate out to calculate integer seconds
        for i in range(len(track_msf) - 1):
            len_current = re.split(r':', track_msf[i])
            len_next = re.split(r':', track_msf[i+1])
            min = int(len_next[0]) - int(len_current[0])
            sec = int(len_next[1]) - int(len_current[1])
            total = (min * 60) + sec # make into seconds
            track_len.append(total)
        return track_len

class CDPlayer():
    def __init__(self):
        self.observers = []

        # initial disc checks
        if self.init_drive():
            self.check_disc()

        self.cur_track = 0

    # for communication with controller
    def attach(self, observer):
        self.observers.append(observer)
    def notify(self, event):
        for observer in self.observers:
            observer.update(event)

    def init_drive(self):
        try:
            self.drive = cdio.Device(source=DRIVE_PATH, driver_id=pycdio.DRIVER_UNKNOWN)
            return True
        except:
            self.state = Status.NO_DRIVE
            self.notify(Events.NO_DRIVE)
            return False

    def check_disc(self):
        try:
            self.drive.get_num_tracks() # this will raise an exception if there is no disc
            self.init_cd()
            self.state = Status.STOPPED
            return True
        except:
            self.state = Status.NO_DISC
            return False

    def init_cd(self):
        self.cd = CD(self.drive) # contains track num/length info
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.medialist = self.instance.media_list_new()
        self.listplayer = self.instance.media_list_player_new()
        self.listplayer.set_media_player(self.player)
        self.medialist.add_media('cdda://' + DRIVE_PATH)
        self.listplayer.set_media_list(self.medialist)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.player_end_reached)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerOpening, self.player_opening)
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerPlaying, self.player_playing)
    def player_end_reached(self, event):
        print(self.cur_track, self.cd.total_tracks_num)
        if self.cur_track < self.cd.total_tracks_num:
            self.cur_track += 1
        else:
            # vlc already stops playback when end reached, so unnecessary to call stop() again
            self.state = Status.STOPPED
            self.notify(Events.STOPPED)
            self.cur_track = 0
    def player_opening(self, event):
        self.state = Status.OPENING
    def player_playing(self, event):
        self.state = Status.PLAYING

    def get_current_time(self):
        """
        Calculates the current time position, in seconds
        """
        cur_time = int(self.player.get_time() / 1000) # round to nearest second
        return cur_time
    def get_current_len(self):
        """
        Calculates the total length of the current track
        """
        return self.cd.total_tracks_len[self.cur_track]
    def get_current_position(self):
        """
        Calculates the current position, as a percentage
        """
        cur_pos = int(self.player.get_position() * 100) # round to nearest 0.01
        return cur_pos
    
    def play_pause(self):
        if self.state is Status.NO_DISC:
            self.init_drive() # cdio requires reinitialisation after disc change
            self.check_disc()
        if self.state is Status.PLAYING:
            self.state = Status.PAUSED
            self.listplayer.pause()
        elif self.state is Status.PAUSED or self.state is Status.STOPPED:
            self.state = Status.PLAYING
            self.listplayer.play()
    def next_track(self):
        if self.state is Status.PAUSED:
            self.play_pause()
        if self.state is Status.PLAYING:
            self.listplayer.next()
            if self.cur_track < self.cd.total_tracks_num:
                self.cur_track += 1
            else:
                self.stop()
    def prev_track(self):
        if self.state is Status.PAUSED:
            self.play_pause()
        if self.state is Status.PLAYING:
            self.listplayer.previous() 
            if self.cur_track > 0:
                self.cur_track -= 1
            else:
                #self.cur_track = self.cd.total_tracks_num
                pass
    def seek_pressed(self, direction): # this function should be run repeatedly for effect
        if self.state is Status.PAUSED:
            self.play_pause()
        if self.state is Status.PLAYING:
            if self.cur_track != 0: # no seeking within opening track
                if direction == 'forward':
                    k = 1 # forward
                    self.state = Status.FAST_FORWARD
                else:
                    k = -1 # rewind
                    self.state = Status.REWIND
                new_pos = self.get_current_position() 
                if new_pos < 0.99 and new_pos > 0.01: # stop seek when start or end of track reached
                    new_pos += (k * 0.002 / self.cd.total_tracks_len[self.cur_track]) # calculate time delta proportional to track length
                    self.player.set_position(new_pos)
                self.state = Status.PLAYING
    def stop(self):
        if self.state is not Status.NO_DISC and self.state is not Status.NO_DRIVE:
            self.listplayer.stop()
            self.cur_track = 0 # reset track count when stop playing
            self.state = Status.STOPPED
            #if notification: self.notify(Events.STOPPED) # do this unless eject (then separate event)
    def eject(self):
        if self.state is not Status.NO_DRIVE:
            self.stop()
            self.drive.eject_media_drive()
            self.notify(Events.EJECT)
            self.state = Status.NO_DISC