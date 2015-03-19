%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
    <title>Shop Radio</title>
</head>

% include('header.tpl')
<table align="center" border=1>

<tr><td colspan='3'><h3 align="center">Results</h3><ul align="center"></td></tr>
	%for album in res:
    <tr><td align='center'>{{album.artist}}</td><td align='center'>{{album.album}}</td> <td align='center'><a href='/add?song_id={{album.id}}'>{{album.name}}</a></td></tr>
    %end
</table>
  </body>      