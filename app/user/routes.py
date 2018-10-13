from flask import make_response, request, redirect, render_template, url_for
from flask_login import current_user
from app.user.forms import LoginForm
from app.user import bp, controllers as controller

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return make_response(redirect("/"))

	form = LoginForm()
	if form.validate_on_submit():
		#try:
		controller.login(form.username.data, form.password.data)
		#except:
		#	return redirect(url_for('user.login'))
	return render_template("login.html", form=form)

@bp.route('/logout')
def logout():
	controller.logout()
	response = make_response(redirect("/login"))
	return response
