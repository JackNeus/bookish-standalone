
//task_list = [("ngram", "NGram"), ("ucsf_api_aggregate", "UCSF API Call")]

var max_parameters = 2;

var parameter_names = {
	"ucsf_api_aggregate": ["Query"],
	"ngram": ["Input Task", "Keywords (space separated)"]
};

var render_paramters = function(obj) {
	let task = $("#task_name").val();
	let task_params = parameter_names[task];

	$('#param_count').val(task_params.length);
	for (let i = 0; i < task_params.length; i++) {
		let label = $('.control-label[for="param' + (i+1) + '"]');
		label.text(task_params[i]);
		label.show();
		$("#param" + (i+1)).show();
	}
	for (let i = task_params.length; i < max_parameters; i++) {
		let label = $('.control-label[for="param' + (i+1) + '"]');
		label.hide();
		$("#param" + (i+1)).hide()
	}
}

$("#task_name").change(function(){
	console.log($(this).val());
	render_paramters();
});

$(document).ready(function() {
	render_paramters();
});