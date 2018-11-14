from flask_login import current_user
from flask_nav import Nav
from flask_nav.elements import Navbar, View

nav = Nav()

@nav.navigation()
def navbar():
	navbar_elements = []
	print(current_user)
	if current_user.is_authenticated:
		navbar_elements.extend([
			View('My Jobs', 'jobs.jobs'),
			View('Schedule Job', 'jobs.schedule'),
			View('Logout', 'user.logout')
		])
	else:
		print("HERE!")
		navbar_elements.extend([
			View('Login', 'user.login')
		])

	return Navbar(
		"bookish",
		*navbar_elements
	)