from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

task_list = [("ngram", "NGram"), ("ucsf_api_aggregate", "UCSF API Call")]
class ScheduleForm(FlaskForm):
	job_name = StringField('Name', validators=[DataRequired()], default="freq")
	task_name = SelectField('Task Type', validators=[DataRequired()], choices = task_list)
	params = StringField('Parameters', default="dummy carcinogen")
	submit = SubmitField('Schedule Job')
