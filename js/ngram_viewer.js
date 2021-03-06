var ngram_chart;
var chart_data = {};
var x_min = 10000;
var x_max = 0;

/* Utilities */

var free_colors = new Set([
"#1f77b4",
"#aec7e8",
"#ff7f0e",
"#ffbb78",
"#2ca02c",
"#98df8a",
"#d62728",
"#ff9896",
"#9467bd",
"#c5b0d5",
"#8c564b",
"#c49c94",
"#e377c2",
"#f7b6d2",
"#7f7f7f",
"#c7c7c7",
"#bcbd22",
"#dbdb8d",
"#17becf",
"#9edae5"]);
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

/* End Utilities */

var generate_labels = function() {
	let labels = [];
	for (var i = x_min; i <= x_max; i++) {
		labels.push(i);	
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
		    responsive: true,
		    maintainAspectRatio: false,
		    scales: {
		    	yAxes: [{
		    		ticks: {
		    			suggestedMin: 0,
		    			suggestedMax: 0.001
		    		},
		    		scaleLabel: {
		    			display: true,
		    			labelString: '% of words'
		    		}
		    	}],
		    	xAxes: [{
		    		scaleLabel: {
		    			display: true,
		    			labelString: 'year'
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
	for (var i = 0; i < chart_data.datasets.length; i++) {
		if (chart_data.datasets[i].label === label) {
			unuse_color(chart_data.datasets[i].color);
			chart_data.datasets.splice(i, 1);
		}
	}
	$(".list-group-item#" + label).remove();
	// Render chart without dataset.
	ngram_chart.update();
}

var has_dataset = function(label) {
	for (var i = 0; i < chart_data.datasets.length; i++) {
		if (chart_data.datasets[i].label === label) return true;
	}
	return false;
}

function adjust_canvas() {
	let canvas = $("#chart")[0];
	canvas.style.width = "100%";
	canvas.style.height = "100%";
	canvas.width = canvas.offsetWidth;
	canvas.height = canvas.offsetHeight;
}

var fileName = localStorage.getItem('fileName');
$("#task-info").text(fileName);
var task_results = JSON.parse(localStorage.getItem('word_freqs'));
start();

function start() {
	init_chart();
	var task_name = Object.keys(task_results).join(", ");

	var task_data = task_results;
	for (var index in task_results) {
		add_dataset(index, task_data[index])
	}

	// Raw Data Show/Hide
	$("#show-data").on("click", function(d) {
	  if ($("#raw-data").hasClass("hidden")) {
	    $(this).text("Hide Raw Data");
	    $("#raw-data").removeClass("hidden");
	  } else {
	    $(this).text("Show Raw Data");
	    $("#raw-data").addClass("hidden");
	  }
	});

	var data_string = "{";
	var items_processed = 0;
	for (var index in task_results) {
		data_string = data_string + "\"" + index + "\": " +
			JSON.stringify(task_results[index]);
		items_processed += 1;
		if (items_processed < Object.keys(task_results).length) {
			data_string = data_string + ",";
		}
		data_string = data_string + "<br />";
	}
	data_string += "}"
	$("#raw-data").html(data_string);
}