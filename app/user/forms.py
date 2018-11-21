from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    #remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField('Sign In')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), 
        Length(min = 6, message = "Password must be at least 6 characters long."),
        EqualTo('confirm', message = "Passwords must match.")])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    
    change_password = SubmitField('Change Password')

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), 
        Length(min = 6, message = "Password must be at least 6 characters long."),
        EqualTo('confirm', message = "Passwords must match.")])
    confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    
    add_user = SubmitField('Add User')
