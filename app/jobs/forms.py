from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.jobs import controllers as controller

def NonNegative(form, field):
	try:
		field_val = int(field.data)
	except ValueError as e:
		raise ValidationError("Field must be an integer.")
	if field_val < 0:
		raise ValidationError("Field must be non-negative.")

task_list = [("ngram", "NGram"), ("ucsf_api_aggregate", "UCSF API Call")][::-1]
class ScheduleForm(FlaskForm):
	job_name = StringField('Name', validators=[DataRequired()], default="freq")
	task_name = SelectField('Task Type', validators=[DataRequired()], choices = task_list)
	
	param_metadata = HiddenField('Parameter Metadata')

	param1 = StringField('', default="author:glantz")
	seed_task = SelectField('Input Task')

	param2 = StringField('', default="carcinogen")

	submit = SubmitField('Schedule Job')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.seed_task.choices = controller.get_seed_jobs()
