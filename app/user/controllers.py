from flask_login import LoginManager, login_user, logout_user, current_user
from app import login_manager
from app.models import User, UserEntry

UserDoesNotExistError = Exception("User does not exist.")
InvalidUserError = Exception("Incorrect username or password.")

def get_user_entry(params):
	user_entry = UserEntry.objects(**params)
	if len(user_entry) != 1:
		return None
	return user_entry[0]

@login_manager.user_loader
def load_user(user_id):
	try:
		user_entry = get_user_entry({'id': user_id})

		if user_entry is None:
			# Throw an error
			raise UserDoesNotExistError
		user = User(str(user_entry.id), user_entry.username)
		return user
	except Exception as e:
		raise e

# views calls this in views.login()
def login(username, password):
	# Create the user
	user = get_user_entry({'id': user_id})
	if user is None or not user.check_password(password):
		raise UserDoesNotExistError
	uid = user.id
	user = load_user(uid)
	if user:
		# User should stay logged in for one week.
		login_user(user, remember = True, duration = timedelta(days=CONFIG["SESSION_LENGTH"]))
	else:
		raise UserDoesNotExistError

def logout():
	logout_user()