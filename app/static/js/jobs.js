setInterval(function() {
	$.getJSON("/jobs.json").done(function(data) {
		for (let i = 0; i < data.length; i++) {
			let job = data[i];
			let job_table_row = $("tr#"+job.id);

			job_table_row.find("td#status").html(job.status);
			job_table_row.find("td#progress").html(job.progress);
			job_table_row.find("td#description").html(job.description);
			
			if (job.status === "Completed") {
				job_table_row.find("td#view-results").html("<a href='jobs/view/"+job.id+"'>View Results</a>");
			} else {
				job_table_row.find("td#view-results").html("");
			}

			if (job.status === "Queued" || job.status === "Running") {
				job_table_row.find("td#action").html("<a href='jobs/kill/"+job.id+"'>Abort Job</a>");
			} else {
				job_table_row.find("td#action").html("<a href='jobs/delete/"+job.id+"'>Delete Job</a>");
			}
				
		}
	});
}, 1500);