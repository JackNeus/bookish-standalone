setInterval(function() {
	$.getJSON("/jobs.json").done(function(data) { updateData(data); });
}, 1500);

var firstUpdate = true;
function updateData(data) {
	for (let i = 0; i < data.length; i++) {
		let job = data[i];
		let job_table_row = $("tr#"+job.id);

	        var previous_status = job_table_row.find("td.status").html();
		job_table_row.find("td.status").html(job.status);
	        if (previous_status === "Queued" || previous_status === "Running" || firstUpdate)
		    job_table_row.find("td.task-progress").html(job.progress);
		var description = job.description;

		// Truncate description if too long.
		var max_description_length = 150;
		if (job.description.length > max_description_length) {
			description = job.description.substr(0, max_description_length) + "...";
		}
		// Only update text of running tasks.
		// This allows the text in other tasks to be selected.
	        if (previous_status === "Queued" || previous_status === "Running" || firstUpdate) {
			job_table_row.find("td.description")
			.html(description)
			.attr("title", job.description);
		}
		job_table_row.find("td.time-started").html(job.time_started);
		job_table_row.find("td.time-finished").html(job.time_finished);
		
		if (job.status === "Completed") {
			job_table_row.find("td.view-results").html("<a href='jobs/view/"+job.id+"'>View Results</a>");
		} else {
			job_table_row.find("td.view-results").html("");
		}

		if (job.status === "Queued" || job.status === "Running") {
			job_table_row.find("td.action").html("<a href='jobs/kill/"+job.id+"'>Abort Job</a>");
		} else {
			job_table_row.find("td.action").html("<a href='jobs/delete/"+job.id+"'>Delete Job</a>");
			job_table_row.find("td.replay").html("<a href='jobs/replay/"+job.id+"'>Replay</a>");
		}
			
	}
	updateLinks();
	updateRows();
        firstUpdate = false;
}

function updateRows() {
	$(".select").on("click", function() {
		updateLinks();
	})
}

function updateLinks() {
	$(".view-results").html("");
	$(".action").html("");

	var selected_ids = [];
	var task_type;
	var valid_vis = true;
	var all_deleteable = true;
	var selected_rows = $(".select:checked").parent().parent().each(function() {
		let status = $(this).find(".status").text();
		let type = $(this).find(".id").text();
		if (task_type === undefined)
			task_type = type;
		else if (task_type !== type || status !== "Completed")
			valid_vis = false;
		selected_ids.push(this.id);

		if (status === "Queued" || status === "Running" || status === "Aborting") 
			all_deleteable = false;
	});

	if (selected_ids.length > 0) {
		var url_param = selected_ids.join(";");

		if (valid_vis && (selected_ids.length == 1 || 
				selected_ids.length <= 3 && (task_type === "word_family_graph_task" || 
				task_type === "top_bigrams_task"))) {
			// Currently, only support multivisualization of word family.
			$(".select:checked").parent().parent().find(".view-results")
				.html("<a href=\"jobs/view/"+url_param+"\">View Results</a>")
		}
		if (all_deleteable) {
			let action_text = selected_ids.length > 1 ? "Delete Jobs" : "Delete Job";
			$(".select:checked").parent().parent().find(".action")
				.html("<a href=\"jobs/delete/"+url_param+"\">"+action_text+"</a>");
		}
	} else {
		$("tr").each(function() {
			var id = $(this)[0].id;
			var status = $(this).find(".status").text();
			if (status === "Completed") {
				$(this).find(".view-results")
					.html("<a href=\"jobs/view/"+id+"\">View Results</a>")
			}

			if (status === "Queued" || status === "Running") {
				$(this).find(".action")
					.html("<a href=\"jobs/kill/"+id+"\">Abort Job</a>");
			} else if (status !== "Aborting") {
				$(this).find(".action")
					.html("<a href=\"jobs/delete/"+id+"\">Delete Job</a>");

			}
		});
	}
}
