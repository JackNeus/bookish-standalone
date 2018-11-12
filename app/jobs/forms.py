from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

def NonNegative(form, field):
	try:
		field_val = int(field.data)
	except ValueError as e:
		raise ValidationError("Field must be an integer.")
	if field_val < 0:
		raise ValidationError("Field must be non-negative.")

task_list = [("ngram", "NGram"), ("ucsf_api_aggregate", "UCSF API Call")]
class ScheduleForm(FlaskForm):
	job_name = StringField('Name', validators=[DataRequired()], default="freq")
	task_name = SelectField('Task Type', validators=[DataRequired()], choices = task_list)
	param_count = HiddenField('Parameter Count', validators=[NonNegative])
	param1 = StringField('', default="dummy")
	param2 = StringField('', default="carcinogen")
	submit = SubmitField('Schedule Job')
