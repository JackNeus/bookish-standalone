from flask import current_app, make_response, request, redirect, render_template, url_for
from flask_login import current_user
from app import login_manager
from app.user.forms import LoginForm
from app.user import bp, controllers as controller
from app.user.controllers import UserDoesNotExistError

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