# This file will contain all possible background jobs that the user can run.

import math
import requests
import subprocess
from rq import get_current_job

from app.jobs.util import start_job

def _set_task_progess(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()

# Get full results for a UCSF IDL API request.
# Does this by concatenating all 100-item pages.
# Returns list of document IDs matching the query.

def ucsf_api_aggregate(query):
    # RQ setup.
    job = get_current_job()
    if job: 
        print("Job exists (%s)" % job.get_id())
        job.meta['status'] = 'Running'
        job.save_meta()
    else:
        print("Job DNE.")
    print(query)
    # CONSTANTS:
    # Base URL of API.
    base_url = "http://solr.industrydocumentslibrary.ucsf.edu/solr/ltdl3/query"
    # Page size of API results.
    page_size = 100

    # Initial API parameters.
    parameters = {"q": query,
                  "wt": "json"}

    # Make initial request to get total number of results.
    r = requests.get(url = base_url, params = parameters)
    r = r.json()
    total_items = r["response"]["numFound"]

    # Calculate number of pages.
    num_pages = math.ceil(total_items * 1.0 / page_size)
    print("%d pages total." % num_pages)

    doc_ids = []
    # Request each page.
    for page in range(num_pages):
        parameters["start"] = page * page_size
        r = requests.get(url = base_url, params = parameters)
        r = r.json()
        doc_ids.extend(list(map(lambda x: x["id"], r["response"]["docs"])))
        print("Done page %d." % page)

        # Update RQ progress, if job is being run as an RQ task.
        _set_task_progess(100.0 * (page + 1) / num_pages)

    if job:
        job.meta['status'] = 'Done'
        job.save_meta()

    print("Returning. Job should not run again.")
    return doc_ids

# This job will probably never be client-facing, as it only needs to be run once.
def clean(files):
    def body(input_queue):
        while not input_queue.empty():
            filename = input_queue.get()
            # TODO: Fix file paths
            subprocess.check_output(['./clean.sh', filename])

    start_job(job_body, files, num_threads = 1)
