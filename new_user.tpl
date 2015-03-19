<head>
	<title>Shop Radio</title>
</head>

	% include('header.tpl')
	<h1 align='center'>Please choose a username.</h1>
	<form action="/new_user" method="post" align="center">
        Username: <input name="username" type="text" />
        <input value="Submit" type="submit" />
    </form>

</body>