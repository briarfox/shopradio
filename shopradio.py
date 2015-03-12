import bottle
import requests
import webbrowser
import json
import os,sys
import requests
from ConfigParser import SafeConfigParser
from rauth import OAuth2Service, OAuth2Session
import pprint

#HOST='shopradio.houserbrosco.com'
class Spotify(object):
    def __init__(self):

        parser = SafeConfigParser()
        if not os.path.isfile('settings.conf'):
            with open('settings.conf','w') as f:
                f.write('[settings]\nhost_url = \nuser_id = \nplaylist = \nclient_id = \nclient_secret = \n')
            print 'Please update settings.conf'
            sys.exit(0)
        parser.read('settings.conf')

        self.host = parser.get('settings','host_url')
        self.uri = 'http://%s/spotify_auth' % self.host
        self.user = parser.get('settings','user_id')
        self.playlist = parser.get('settings','playlist')
        self.client_id=parser.get('settings','client_id')
        self.client_secret=parser.get('settings','client_secret')
        self.spotify = OAuth2Service(
                            client_id=self.client_id,
                            client_secret=self.client_secret,
                            name='spotify',
                            authorize_url='https://accounts.spotify.com/authorize',
                            access_token_url='https://accounts.spotify.com/api/token',
                            base_url='https://api.spotify.com/')

        params = {'scope': 'playlist-modify-private playlist-read-private playlist-modify-public',
          'response_type': 'code',
          'redirect_uri': self.uri}
        url = self.spotify.get_authorize_url(**params)

        # open a public URL, in this case, the webbrowser docs

        webbrowser.open(url)
    def _create_session(self):
        return OAuth2Session(self.client_id,self.client_secret,self.tokens['access_token'])

    def create_token(self,code):
        data = {'code': code,
            'redirect_uri': 'http://%s/spotify_auth'% self.host, 
            'grant_type': 'authorization_code'}
        response = self.spotify.get_raw_access_token(data=data)
        print response
        self.tokens =  json.loads(response.content)
        print self.tokens['refresh_token']
        self.session = self._create_session()
        self.refresh_token()
        #self.session = self.spotify.get_auth_session(data=data, decoder=json.loads)
        #print self.session.expires_in

    def refresh_token(self):
        data = {'client_id':self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.tokens['refresh_token']}

        response = self.spotify.get_access_token(data=data, decoder=json.loads)
        print response
        self.tokens['access_token'] =  response
        self.session = self._create_session()
        

    def add_song(self,ids):
        print ids
        params = {
            'uris':'spotify:track:%s' % ids,
            }
        headers = {'Accept': 'application/json','Content-Type': 'application/json'}
        
        res = self.session.post('https://api.spotify.com/v1/users/%s/playlists/%s/tracks' % (self.user,self.playlist),params=params,headers=headers)
        print res.content

    def _parse_search(self,res):
        output = {'artists':[],'albums':[],'tracks':[]}
        for album in res.json()['artists']['items']:
            try:
                img = album['images'][0]['url']
            except:
                img = ' '
            output['artists'].append({'name': album['name'], "id": album['id'],'img': img})

        for album in res.json()['albums']['items']:
            try:
                img = album['images'][2]['url']
            except:
                img = ' '
            output['albums'].append({'name': album['name'], "id": album['id'],'img': img})

        for album in res.json()['tracks']['items']:
            output['tracks'].append({'name': album['name'], "id": album['id'],'artist': album['artists'][0]['name']})

        return output  

    def _parse_artist(self,res):
        output = {'artists': [], 'albums': [], 'tracks': []}
        names=[]
        for album in res['items']:
            try:
                img = album['images'][0]['url']
            except:
                img = ' '
            if album['name'] not in names:
                names.append(album['name'])
                output['albums'].append({'name': album['name'], 'id': album['id'], 'img': img})
        return output

    def search(self,field):
        params={'q': field,
                'type': 'track,artist,album',
                }
        res = self.session.get('https://api.spotify.com/v1/search',params=params)
        return self._parse_search(res)
    
    def _parse_album(self,res):
        output = {'artists': [], 'albums': [], 'tracks': []}  
        for track in res['items']:
            output['tracks'].append({'name': track['name'], 'id': track['id'], 'artist': track['artists'][0]['name']})
        return output
    
    def get_album_tracks(self,id):
        res = self.session.get('https://api.spotify.com/v1/albums/{id}/tracks'.format(id=id))
        return self._parse_album(res.json())

    def get_artist_albums(self,id):
        res = self.session.get('https://api.spotify.com/v1/artists/{id}/albums'.format(id=id))
        return self._parse_artist(res.json())




spotify = Spotify()
app = bottle.Bottle()
@app.route('/')
def index():
    return '''
        <head><title>Shop Radio</title></head>
        <body>
        <h1>Shop Radio - Alpha</h1>
        <br>
        <form action="/search" method="post">
            Search: <input name="search_item" type="text" />
            <input value="Search" type="submit" />
        </form>
        </body>
    '''
    
    

@app.post('/search')
def search():
    res = spotify.search(bottle.request.forms.get('search_item'))
    return bottle.template('search', res=res)

@app.route('/tracks')
def tracks():
    album_id = bottle.request.query['id']
    res = spotify.get_album_tracks(album_id)
    return bottle.template('search',res=res)

@app.route('/albums')
def albums():
    artist_id = bottle.request.query['id']
    res = spotify.get_artist_albums(artist_id)
    return bottle.template('search',res=res)

@app.route('/add')
def add_song():
    spotify.add_song(bottle.request.query['id'])
    return 'song added'


@app.route('/spotify_auth')
def spotify_auth():
    code = bottle.request.query['code']
    spotify.create_token(code)
    return 'ok'

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)
