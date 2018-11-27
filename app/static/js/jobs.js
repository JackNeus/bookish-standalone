setInterval(function() {
	$.getJSON("/jobs.json").done(function(data) {
		for (let i = 0; i < data.length; i++) {
			let job = data[i];
			let job_table_row = $("tr#"+job.id);
			console.log(job.progress);
			job_table_row.find("td#progress").html(job.progress);
		}
		/*{% for i in range(jobs|length) %}
				<tr>
					<th scope="row">{{ i }}</th>
					<td title="{{ jobs[i].id }}">{{ jobs[i].task }}</td>
					<td>{{ jobs[i].name }}</td>
					<td>{{ jobs[i].status }}</td>
					<td>
						{% if jobs[i].status == "Completed" %}
							<a href="jobs/view/{{jobs[i].id}}">View Results</a>
						{% endif %}
					</td>
					<td>{{ jobs[i].time_started }}</td>
					<td></td>
					<td>{{ jobs[i].progress }}</td>
					<td>{{ jobs[i].description }}</td>
					<td>
						{% if jobs[i].status in ["Queued", "Running"] %}
							<a href="jobs/kill/{{jobs[i].id}}">Abort Job</a>
						{% else %}
							<a href="jobs/delete/{{jobs[i].id}}">Delete Job</a>
						{% endif %}
					</td>
				</tr>
		{% endfor %}*/
	})
}, 2500);