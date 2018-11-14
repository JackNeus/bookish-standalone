
//task_list = [("ngram", "NGram"), ("ucsf_api_aggregate", "UCSF API Call")]

var max_parameters = 2;

var all_fields = ["param1", "seed_task", "param2"];
var task_fields = {
	"ucsf_api_aggregate": ["param1"],
	"ngram": ["seed_task", "param2"]
};
var parameter_names = {
	"ucsf_api_aggregate": ["Query"],
	"ngram": ["Input Task", "Keywords (space separated)"]
};

var render_paramters = function(obj) {
	let task = $("#task_name").val();
	let task_params = task_fields[task];
	let task_param_names = parameter_names[task];

	$('#param_metadata').val(task_params.join(";"));
	for (let i = 0; i < all_fields.length; i++) {
		let field_name = all_fields[i];
		let field_label = $('.control-label[for="'+field_name+'"]');
		field_label.hide();
		let field = $('#'+field_name);
		field.hide();
	}
	for (let i = 0; i < task_params.length; i++) {
		let task_param = task_params[i];
		let field_label = $('.control-label[for="'+task_param+'"]');
		field_label.text(parameter_names[task][i]);
		field_label.show();
		let task_field = $('#'+task_param);
		task_field.show();
	}
}

$("#task_name").change(function(){
	console.log($(this).val());
	render_paramters();
});

$(document).ready(function() {
	render_paramters();
});