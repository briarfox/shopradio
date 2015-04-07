import bottle
import grooveshark
import subprocess
import threading
import datetime
import json
import time
import random
from dateutil.relativedelta import relativedelta
import os,sys
class GS_Radio(object):
    def __init__(self):
        self.client = grooveshark.Client()
        self.client.init()
        #self.client.init()
        self.playlist = []
        self.playing = False
        

    def search(self, song_name):
        return self.client.search(song_name, type='Songs')

    def play_thread(self):
        playing = False
        start_time = datetime.datetime.now() - relativedelta(seconds=31)
        while True:
            
            if self.playlist:
                print 'RUNNING PLAYLIST CHECK'
                self.playlist.sort(key=lambda song: song.rank, reverse=True)
                song_rank = self.playlist[0].rank
                tracks = []
                
                for song_num in range(len(self.playlist)):
                    if self.playlist[song_num].rank == song_rank:
                        tracks.append(song_num)
                
                if len(tracks)>1:
                    print 'tracks greater then 1'
                    track_id = tracks[random.randint(0,len(tracks)-1)]
                else:
                    track_id = tracks[0]
                
                
                song = self.playlist.pop(track_id)
                self.playing = song
                subprocess.call(['vlc','-I','dummy','--one-instance','--play-and-exit','--audio-filter','normalizer',song.stream.url])
                self.playing = False
            elif start_time + relativedelta(seconds=30) <= datetime.datetime.now():
                subprocess.call(['vlc','-I','dummy','--one-instance','--play-and-exit', 'data/checklist.wav'])
                start_time = datetime.datetime.now()
            
    def play(self):
        t1 = threading.Thread(target=self.play_thread)
        t1.start()

    def add_song(self,song_id,user):
        song = self.client.get_song_by_id(song_id)
        song.submitter = user
        song.rank = 0
        #song.random = random.randint(0,3)
        self.playlist.append(song)
        self.playlist.sort(key=lambda song: song.rank, reverse=True)

    def rank_song(self,song_id,vote):
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
    bottle.response.set_cookie("votes",json.dumps(votes),max_age = 60*60)

@app.route('/')
def index():

    if bottle.request.get_cookie('user'):
        votes = bottle.request.get_cookie('votes') or u'{"votes": []}'
        return bottle.template('index',playing=gs_radio.playing,playlist=gs_radio.playlist, votes=json.loads(votes))
    else:
        return bottle.template('new_user')
    
@app.route('/images/<filename:re:.*\.jpg>')
def send_image(filename):
    print os.path.dirname(os.path.realpath(__file__))+'/images'
    return bottle.static_file(filename, root=os.path.dirname(os.path.realpath(__file__))+'/images')

@app.post('/search')
def search():
    print bottle.request.forms.get('search_item')
    res = gs_radio.search(bottle.request.forms.get('search_item'))
    return bottle.template('search', res=res)

@app.get('/add')
def add_song():
    try:
        song_id = bottle.request.query.get('song_id')
        add_voted(song_id)
        gs_radio.add_song(song_id,bottle.request.get_cookie('user'))
    except:
        pass
    bottle.redirect("/")

@app.post('/new_user')
def add_user():
    bottle.response.set_cookie("user", bottle.request.forms.get('username'),expires = datetime.datetime.now()+relativedelta(years=1))
    bottle.redirect("/")

@app.get('/rank')
def rank():
    song_id = bottle.request.query.id
    vote = bottle.request.query.vote
    add_voted(song_id)
    gs_radio.rank_song(song_id,vote)
    bottle.redirect('/')

     

    
if __name__ == '__main__':
    app.run(host=sys.argv[1],port=sys.argv[2])
