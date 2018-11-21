from datetime import timedelta
from flask import current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from app import login_manager
from app.models import User, UserEntry

class UserDoesNotExistError(Exception):
	pass
class UsernameTakenError(Exception):
	pass
class InvalidUserError(Exception):
	pass
class InvalidPasswordError(Exception):
	pass
class AuthorizationError(Exception):
	pass

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
			raise UserDoesNotExistError()
		user = User(str(user_entry.id), user_entry.username, user_entry.is_admin)
		return user
	except Exception as e:
		raise e

# views calls this in views.login()
def login(username, password):
	# Create the user
	user = get_user_entry({'username': username})

	if user is None or not user.check_password(password):
		raise UserDoesNotExistError()
	uid = user.id
	user = load_user(uid)
	if user:
		# User should stay logged in for one week.
		login_user(user, 
			remember = True, 
			duration = timedelta(days=current_app.config["SESSION_LENGTH"]))
	else:
		raise UserDoesNotExistError()

def logout():
	logout_user()

def change_password(user, current_password, password):
	user = get_user_entry({'username': user})
	
	if user is None:
		raise UserDoesNotExistError()
	if not user.check_password(current_password):
		raise InvalidPasswordError()
	user.set_password(password)

def add_user(username, password):
	if not current_user.is_admin:
		raise AuthorizationError()

	user = get_user_entry({'username': username})
	if user:
		raise UsernameTakenError()
	new_user = UserEntry(username)
	new_user.set_password(password)
	new_user.save()
	return new_user