from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.jobs import controllers as controller

def NonNegative(form, field):
	try:
		field_val = int(field.data)
	except ValueError as e:
		raise ValidationError("Field must be an integer.")
	if field_val < 0:
		raise ValidationError("Field must be non-negative.")

task_list = [
("ucsf_api_aggregate", "UCSF API Call (selection)"), 
("ngram", "NGram (analysis)"), 
("top_bigrams", "Top Bigrams (analysis)"),
("word_families", "Word Family Graph (analysis)")]

class ScheduleForm(FlaskForm):
	job_name = StringField('Name', validators=[DataRequired()], default="")
	task_name = SelectField('Task Type', validators=[DataRequired()], choices = task_list)
	
	param_metadata = HiddenField('Parameter Metadata')

	param1 = StringField('', default="")
	seed_task = SelectField('Input Task')

	param2 = TextAreaField('', default="")

	submit = SubmitField('Schedule Job')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.seed_task.choices = controller.get_seed_jobs()
