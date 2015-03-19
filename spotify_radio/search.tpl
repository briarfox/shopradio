%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
    <title>Shop Radio</title>
</head>

% include('header.tpl')
<table align="center" border=1>
<tr><td colspan="2"><h3 align="center">Artists</h3><ul align="center"></td></tr>
	%for album in res['artists']:
	%try:
    %img = album['img']
    %except:
    %img = ' '
    %end
    <tr><td><img src="{{img}}" height="64" width="64"></td><td> <a href="/albums?id={{album['id']}}">{{album['name']}}</a></td></tr>
    %end
     
<tr><td colspan="2"><h3 align="center">Albums</h3><ul align="center"></td></tr>
	%for album in res['albums']:
    %try:
    %img = album['img']
    %except:
    %img = ' '
    %end
    <tr><td><img src="{{img}}" height="64" width="64"></td><td> <a href="/tracks?id={{album['id']}}">{{album['name']}}</a></td></tr>
    %end

<tr><td colspan="2"><h3 align="center">Tracks</h3><ul align="center"></td></tr>
	%for album in res['tracks']:
    <tr><td>{{album['artist']}}</td><td><a href="/add?id={{album['id']}}">{{album['name']}}</a></td></tr>
    %end
</table>
  </body>      