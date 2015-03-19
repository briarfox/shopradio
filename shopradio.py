import bottle
import grooveshark
import subprocess
import threading
import datetime
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
        while True:
            if self.playlist:
                song = self.playlist.pop(0)
                self.playing = song
                subprocess.call(['vlc','-I','dummy','--one-instance','--play-and-exit', song.stream.url])
                self.playing = False
            
    def play(self):
        t1 = threading.Thread(target=self.play_thread)
        t1.start()

    def add_song(self,song_id,user):
        song = self.client.get_song_by_id(song_id)
        song.submitter = user
        self.playlist.append(song)
        
        
gs_radio = GS_Radio()
gs_radio.play()
app = bottle.Bottle()
@app.route('/')
def index():
    if bottle.request.get_cookie('user'):
        return bottle.template('index',playing=gs_radio.playing,playlist=gs_radio.playlist)
    else:
        return bottle.template('new_user')
    
@app.route('/images/<filename:re:.*\.jpg>')
def send_image(filename):
    print os.path.dirname(os.path.realpath(__file__))+'\images'
    return bottle.static_file(filename, root=os.path.dirname(os.path.realpath(__file__))+'\images')

@app.post('/search')
def search():
    print bottle.request.forms.get('search_item')
    res = gs_radio.search(bottle.request.forms.get('search_item'))
    return bottle.template('search', res=res)

@app.get('/add')
def add_song():
     song_id = bottle.request.query.get('song_id')
     gs_radio.add_song(song_id,bottle.request.get_cookie('user')
)
     bottle.redirect("/")

@app.post('/new_user')
def add_user():
    bottle.response.set_cookie("user", bottle.request.forms.get('username'),expires = datetime.datetime.now()+relativedelta(years=1))
    bottle.redirect("/")
     

    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
