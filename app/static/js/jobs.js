setInterval(function() {
	$.getJSON("/jobs.json").done(function(data) {
		for (let i = 0; i < data.length; i++) {
			let job = data[i];
			let job_table_row = $("tr#"+job.id);

			job_table_row.find("td.status").html(job.status);
			job_table_row.find("td.task-progress").html(job.progress);
			job_table_row.find("td.description").html(job.description);
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
			}
				
		}
		updateViewLinks();
		updateRows();
	});
}, 1500);

function updateRows() {
	$(".select").on("click", function() {
		updateViewLinks();
	})
}

// TODO: Expand to delete. 
function updateViewLinks() {
	$(".view-results").html("");
	var selected_ids = [];
	var task_type;
	var type_mismatch = false;
	var selected_rows = $(".select:checked").parent().parent().each(function() {
		let type = $(this).find(".id").text();
		if (task_type === undefined)
			task_type = type;
		else if (task_type !== type)
			type_mismatch = true;
		selected_ids.push(this.id);
	});
	// Can't multivisualize things of different types.
	if (type_mismatch) return;

	if (selected_ids.length > 0) {
		if (selected_ids.length > 1) { // True multivis.
			// Currently, only support multivisualization of word family.
			if (task_type !== "word_family_graph_task") return;
		}

		var url_param = selected_ids.join(";");
		$(".select:checked").parent().parent().find(".view-results")
			.html("<a href=\"jobs/view/"+url_param+"\">View Results</a>")
	} else {
		$("tr").each(function() {
			var id = $(this)[0].id;
			$(this).find(".view-results")
				.html("<a href=\"jobs/view/"+id+"\">View Results</a>")
		});
	}
}

updateRows();
updateViewLinks();
