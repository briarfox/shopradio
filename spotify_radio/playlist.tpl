<h1>Please Select A Playlist</h1>

<div align='center'>
%for playlist in playlists:
<a href="/select_playlist?id={{playlist['id']}}">{{playlist['name']}}</a>
<br>
%end