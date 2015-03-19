<head>
	<title>Shop Radio</title>
	<META HTTP-EQUIV="refresh" CONTENT="60">
</head>
<style>
th,td {
    padding: 5px;
    text-align: center;
}

</style>

	% include('header.tpl')
    %if playing:

    %end
    <div align='center'>
    <form action="/search" method="post" align="center">
        Search: <input name="search_item" type="text" />
        <input value="Search" type="submit" />
    </form>
    </div>
    %if playing:
        <p align=center>Now Playing:<b><br>{{playing.artist}}<br>{{playing.name}}<br>{{playing.submitter}}</b></p>
    %end
    <table align='center' padding='5'>
        <tr><td>Atrist</td><td>Song</td><td>Submitter</td><td>Votes</td><td>Vote Up</td><td>Vote Down</td></tr>
        %if playlist:
            %for song in playlist:

                %if song.id in votes['votes']:
                    <tr><td>{{song.artist}}</td><td>{{song.name}}</td><td>{{song.submitter}}</td><td>{{song.rank}}</td><td> - </td><td> - </td></tr>

                %else:
                    <tr><td>{{song.artist}}</td><td>{{song.name}}</td><td>{{song.submitter}}</td><td>{{song.rank}}</td><td><a href="/rank?id={{song.id}}&vote=up"><img src="/images/beer.jpg"></a></td><td><a href="/rank?id={{song.id}}&vote=down"><img src="/images/finger.jpg"></a></td></tr>
                    
                %end
            %end
            
        %end
    </table>
  
</body>