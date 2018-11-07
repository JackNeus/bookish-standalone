# This file will contain all possible background jobs that the user can run.

import math
import os
import requests
import subprocess
from rq import get_current_job
from flask import current_app

from app.models import JobEntry
from app.jobs.util import *

def resolve_task(task_name):
    if task_name == "ucsf_api_aggregate":
        return ucsf_api_aggregate
    return None

# Get full results for a UCSF IDL API request.
# Does this by concatenating all 100-item pages.
# Returns list of document IDs matching the query.

def ucsf_api_aggregate(query):
    # RQ setup.
    job = get_current_job()
    if job: 
        print("Job exists (%s)" % job.get_id())
        set_task_status('Running')
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
        set_task_progess(100.0 * (page + 1) / num_pages)

    return_from_task(doc_ids)

    if job:
        job.meta['status'] = 'Done'
        job.save_meta()

    print("Returning. Job should not run again.")
    return doc_ids

# This job will probably never be client-facing, as it only needs to be run once.
def clean(files):
    def job_body(input_queue):
        print("Entered.")
        while not input_queue.empty():
            file_path = input_queue.get()
            subprocess.check_output(['./jobs/clean.sh', file_path])
            input_queue.task_done()
    util.start_job(job_body, files, num_threads = 3)

'''
# Temporary. Comment this out before running the actual app.
txt = []
for subdir, dirs, files in os.walk("../txt/ucsf/"):
    for file in files:
        txt.append(subdir + "/" + file)

clean(txt + txt)
print("Done.")
'''