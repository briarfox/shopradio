<head>
	<title>Shop Radio</title>
	<META HTTP-EQUIV="refresh" CONTENT="60">
</head>

	% include('header.tpl')

    <form action="/search" method="post" align="center">
        Search: <input name="search_item" type="text" />
        <input value="Search" type="submit" />
    </form>
    <br><br>
    <table align="center" cellpadding="5">
    	<tr><th colspan='2' align='center'>Recently Added</th></tr>
    	<tr><td align='center'><b>Artist</b></td><td align='center'><b>Song</b></td></tr>
	%for album in recent:
    <tr><td align='left'>{{album['artist']}}</td><td align='left'>{{album['song']}}</td><td>
    %end
</table>
  
</body>