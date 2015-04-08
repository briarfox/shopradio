import bottle
import grooveshark
import subprocess
import threading
import datetime
import json
import random
from dateutil.relativedelta import relativedelta
import os
import sys
import logging
import logging.config


if len(sys.argv) > 3:
    flag = sys.argv[3]
    if flag == '--debug':
        LOGGING_LEVEL = logging.DEBUG
    elif flag == '--info':
        LOGGING_LEVEL = logging.INFO
    elif flag == '--warning':
        LOGGING_LEVEL = logging.WARNING
else:
    LOGGING_LEVEL = logging.CRITICAL

logging.config.fileConfig('config.ini')
defaultlog = logging.getLogger()
defaultlog.setLevel(LOGGING_LEVEL)

# logger
log = logging.getLogger('_shopradio_')
log.info('APPLICATION START')


class GS_Radio(object):

    def __init__(self):
        self.client = grooveshark.Client()
        self.client.init()

        # self.client.init()
        self.log = logging.getLogger('_GS_Radio_')
        self.tlog = logging.getLogger('_PlayThread_')
        self.log.info('Creating GS_Radio object')
        self.playlist = []
        self.playing = False

    def search(self, song_name):
        res = self.client.search(song_name, type='Songs')
        self.log.debug('Searched for: ', song_name)
        return res

    def play_thread(self):
        self.tlog.warning('Started play_Thread')
        start_time = datetime.datetime.now() - relativedelta(seconds=31)
        while True:
            if self.playlist:
                self.tlog.debug('Playlist Found, checking playlist')
                self.playlist.sort(key=lambda song: song.rank, reverse=True)
                song_rank = self.playlist[0].rank
                tracks = []
                for song_num in range(len(self.playlist)):
                    if self.playlist[song_num].rank == song_rank:
                        tracks.append(song_num)
                if len(tracks) > 1:
                    self.tlog.debug('More then 1 track found.')
                    track_id = tracks[random.randint(0, len(tracks) - 1)]
                else:
                    self.tlog.warning('Only 1 track found')
                    track_id = tracks[0]
                self.tlog.debug('Playing %d, out of %s' %
                                (track_id + 1, len(self.playlist)))
                song = self.playlist.pop(track_id)
                self.playing = song
                self.tlog.info('VLC Launched')
                try:
                    rtn = subprocess.check_call(['vlc', '-I', 'dummy', '--one-instance', '--play-and-exit', '--audio-filter', 'normalizer', song.stream.url])
                    self.tlog.info('VLC returned %d' % rtn)
                except:
                    self.tlog.exception('VLC Failed to return')
                self.tlog.info('VLC finished')
                self.playing = False
            elif start_time + relativedelta(seconds=30) <= datetime.datetime.now():
                self.tlog.info('No Tracks Found, playing placeholder.')
                subprocess.call(
                    ['vlc', '-I', 'dummy', '--one-instance', '--play-and-exit', 'data/checklist.wav'])
                start_time = datetime.datetime.now()

    def play(self):
        self.log.debug('Starting Play thread.')
        t1 = threading.Thread(target=self.play_thread)
        t1.start()
        self.log.debug('Play thread started')

    def add_song(self, song_id, user):
        self.log.debug('Trying to add song')
        try:
            song = self.client.get_song_by_id(song_id)
            self.log.debug('Added song %s' % song_id)

            song.submitter = user
            song.rank = 0
            # song.random = random.randint(0,3)
            self.playlist.append(song)
            self.playlist.sort(key=lambda song: song.rank, reverse=True)
            return 0
        except:
            self.log.exception('Failed to add song %s' % song_id)
            return 1

    def rank_song(self, song_id, vote):
        for song in self.playlist:
            if song.id == song_id:
                print 'found'
                if vote == 'up':
                    song.rank += 1
                elif vote == 'down':
                    song.rank -= 1
                self.playlist.sort(key=lambda song: song.rank, reverse=True)
                break

gs_radio = GS_Radio()
gs_radio.play()
app = bottle.Bottle()


def add_voted(song_id):
    votes = json.loads(bottle.request.get_cookie('votes') or u'{"votes": []}')
    votes['votes'].append(song_id)
    bottle.response.set_cookie("votes", json.dumps(votes), max_age=60 * 60)


@app.route('/')
def index():

    if bottle.request.get_cookie('user'):
        votes = bottle.request.get_cookie('votes') or u'{"votes": []}'
        return bottle.template('index', playing=gs_radio.playing, playlist=gs_radio.playlist, votes=json.loads(votes))
    else:
        return bottle.template('new_user')


@app.route('/images/<filename:re:.*\.jpg>')
def send_image(filename):
    return bottle.static_file(filename, root=os.path.dirname(os.path.realpath(__file__)) + '/images')


@app.post('/search')
def search():
    log.debug('Search for %s' % bottle.request.forms.get('search_item'))
    res = gs_radio.search(bottle.request.forms.get('search_item'))
    return bottle.template('search', res=res)


@app.get('/add')
def add_song():
    song_id = bottle.request.query.get('song_id')
    log.debug('Adding song %s' % song_id)
    add_voted(song_id)
    log.debug('adding cookie vote %s' % song_id)
    status = gs_radio.add_song(song_id, bottle.request.get_cookie('user'))
    # try:
    #    gs_radio.add_song(song_id,bottle.request.get_cookie('user'))
    # except Exception,e:
    #    log.error('song failed to add %s Exception: %s' % (song_id,e))
    if status == 1:
        return bottle.template('error')
    else:
        bottle.redirect("/")


@app.post('/new_user')
def add_user():
    log.info('New User added %s' % bottle.request.forms.get('username'))
    bottle.response.set_cookie("user", bottle.request.forms.get(
        'username'), expires=datetime.datetime.now() + relativedelta(years=1))
    bottle.redirect("/")


@app.get('/rank')
def rank():
    song_id = bottle.request.query.id
    vote = bottle.request.query.vote
    add_voted(song_id)
    log.debug('Song %s ranked %s' % (song_id, vote))
    gs_radio.rank_song(song_id, vote)
    bottle.redirect('/')


if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
    sys
