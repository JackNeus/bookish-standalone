from flask import current_app, flash, make_response, request, redirect, render_template, url_for
from flask_login import current_user
from app import login_manager
from app.user.forms import LoginForm, ChangePasswordForm, AddUserForm
from app.user import bp, controllers as controller
from app.user.controllers import AuthorizationError, UserDoesNotExistError, InvalidPasswordError, UsernameTakenError

@login_manager.unauthorized_handler
def redirect_login():
	return redirect(url_for('user.login'))
	
@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return make_response(redirect("/"))

	form = LoginForm()
	if form.validate_on_submit():
		#try:
		try:
			controller.login(form.username.data, form.password.data)
			return redirect(url_for('web.index'))
		except UserDoesNotExistError:
			flash("Invalid username or password.")
		#except:
		#	return redirect(url_for('user.login'))
	return render_template("login.html", form=form)

@bp.route('/logout')
def logout():
	controller.logout()
	response = make_response(redirect("/login"))
	return response

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
	# If user is sandboxed, disable their profile.
	if current_user.is_sandboxed:
		return make_response(redirect("/"))

	change_pwd_form = ChangePasswordForm()
	add_user_form = AddUserForm()

	if change_pwd_form.change_password.data and change_pwd_form.validate_on_submit():
		try:
			controller.change_password(current_user.username, 
									   change_pwd_form.current_password.data, 
									   change_pwd_form.password.data)
		except InvalidPasswordError as e:
			flash("Current password was incorrect.")
		except Exception as e:
			if current_app.config["DEBUG"]:
				raise e
			flash("Something went wrong.")

	if add_user_form.add_user.data and add_user_form.validate_on_submit():
		try:
			controller.add_user(add_user_form.username.data, add_user_form.password.data)
		except AuthorizationError:
			flash("You can't do that!")
		except UsernameTakenError:
			flash("Username is already in use.")
		except Exception as e:
			raise e
			flash("User could not be added.")
	return render_template("user/profile.html", change_pwd_form = change_pwd_form, add_user_form = add_user_form)