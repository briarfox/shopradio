%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<head>
    <title>Shop Radio</title>
</head>
<body>
<p><h3><a href="/">Shop Radio</a></h3></p>
<h3>Artists</h3><ul>
	%for album in res['artists']:
	%try:
    %img = album['img']
    %except:
    %img = ' '
    %end
    <li><img src="{{img}}" height="64" width="64"> <a href="/albums?id={{album['id']}}">{{album['name']}}</a></li>
    %end
</ul>     
<h3>Albums</h3><ul>
	%for album in res['albums']:
    %try:
    %img = album['img']
    %except:
    %img = ' '
    %end
    <li><img src="{{img}}" height="64" width="64"> <a href="/tracks?id={{album['id']}}">{{album['name']}}</a></li>
    %end
</ul>
<h3>Tracks</h3><ul>
	%for album in res['tracks']:
    <li>{{album['artist']}} - <a href="/add?id={{album['id']}}">{{album['name']}}</a></li>
    %end
</ul>
  </body>      