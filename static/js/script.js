var ngram_chart;
var chart_data = {};
var x_min = 1960;
var x_max = 1980;

var init_chart = function() {
	var default_years = [];
	for (var i = 1960; i <= 1980; i += 2) default_years.push(i);
	chart_data.labels = default_years;
	chart_data.datasets = [];

	var ctx = $("#chart");
	ngram_chart = new Chart(ctx, {
	    type: 'line',
	    data: chart_data,
	    options: {
		    responsive: false,
		    scales: {
		    	yAxes: [{
		    		ticks: {
		    			suggestedMin: 0,
		    			suggestedMax: 10
		    		}
		    	}]
		    }
		 }
	});
}

var add_dataset = function(label, data) {
	years = Object.keys(data);
	var freqs = Object.values(data);

	// TODO: Check if x_min and x_max need to be updated.

	chart_data.datasets.push({
		label: label,
		data: freqs,
		borderColor: use_color()
	});
	// Render new datasets.
	ngram_chart.update();
}

var remove_dataset = function(label) {
	for (var i = 0; i < data.length; i++) {
		if (data[i].label === label) {
			unuse_color(data[i].color);
			delete data[i];
		}
	}
}

var success_callback = function(data) {
	add_dataset($("#ngram").val(), data);
}

$('#make-ngram').click(function() {
	var divide = $("#divide").is(":checked");
	$.ajax({
		url: 'http://localhost:5000/api/ngram/' + $('#ngram').val() + "/" + divide,
		dataType: 'json',
		success: success_callback
	});
});

init_chart();

/* Utilities */

var free_colors = new Set([
	"#3e95cd", 
	"#8e5ea2", 
	"#3cba9f", 
	"#e8c3b9", 
	"#c45850"]);
var used_colors = new Set();

// Picks a color from free_colors and
// returns it. That color is moved
// to used_colors.
// TODO: When there are no free colors, 
// return a default color.
var use_color = function() {
	let color = free_colors.values().next().value;
	free_colors.delete(color);
	used_colors.add(color);
	return color;
}

// Move color from used_colors to 
// free_colors. If color not in
// used_colors, do nothing.
var unuse_color = function(color) {
	if (used_colors.has(color)) {
		used_colors.delete(color);
		free_colors.add(color);
	}
}
