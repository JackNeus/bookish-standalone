template = '''
<html>
	<head></head>
	<body></body>
	<script type="text/javascript">
		// Set variables in local storage.
		%s
		window.location = "vis_%s.html";
	</script>
</html>
'''

localStorageTemplate = "localStorage.setItem('%s', '%s');"