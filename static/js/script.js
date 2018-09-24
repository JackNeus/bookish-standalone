var ngram_chart;
var chart_data = {};
var x_min = 1960;
var x_max = 1980;

var generate_labels = function() {
	let labels = [];
	for (var i = x_min; i <= x_max; i++) {
		if (i % 2 == 0) labels.push(i);	
		else labels.push("");
	}
	return labels;
}

var init_chart = function() {
	chart_data.labels = generate_labels();
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
		    			suggestedMax: 0.001
		    		}
		    	}]
		    }
		 }
	});
}

var add_dataset = function(label, data) {
	years = Object.keys(data);
	var freqs = Object.values(data);

	for (var i = 0; i < years.length; i++) {
		x_max = Math.max(x_max, years[i]);
		x_min = Math.min(x_min, years[i]);
	}

	chart_data.labels = generate_labels();
	chart_data.datasets.push({
		label: label,
		data: freqs,
		borderColor: use_color()
	});
	// Render new datasets.
	ngram_chart.update();
}

var remove_dataset = function(label) {
	for (var i = 0; i < chart_data.length; i++) {
		if (chart_data[i].label === label) {
			unuse_color(chart_data[i].color);
			delete chart_data[i];
		}
	}
}

var has_dataset = function(label) {
	for (var i = 0; i < chart_data.datasets.length; i++) {
		if (chart_data.datasets[i].label === label) return true;
	}
	return false;
}

var success_callback = function(data) {
	add_dataset($("#ngram").val(), data);
}

$('#make-ngram').click(function() {
	let word = $('#ngram').val();
	// Don't add the same word twice.
	if (has_dataset(word)) {
		return;
	}
	var divide = $("#divide").is(":checked");
	$.ajax({
		url: 'http://localhost:5000/api/ngram/' + word + "/true",
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
