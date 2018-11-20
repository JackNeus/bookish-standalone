from flask import current_app, flash, make_response, request, redirect, render_template, url_for
from flask_login import current_user
from app import login_manager
from app.user.forms import LoginForm, ChangePasswordForm
from app.user import bp, controllers as controller
from app.user.controllers import UserDoesNotExistError, InvalidPasswordError

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
	change_pwd_form = ChangePasswordForm()

	if change_pwd_form.submit.data and change_pwd_form.validate_on_submit():
		try:
			controller.change_password(current_user.username, 
									   change_pwd_form.current_password.data, 
									   change_pwd_form.password.data)
		except InvalidPasswordError as e:
			flash("Current password was incorrect.")
		except Exception as e:
			raise e
			flash("Something went wrong.")
	return render_template("user/profile.html", change_pwd_form = change_pwd_form)