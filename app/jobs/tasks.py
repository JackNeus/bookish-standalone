# This file will contain all possible background jobs that the user can run.

import math
import requests
from rq import get_current_job
from flask import current_app

def _set_task_progess(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()

def _set_task_status(status):
    job = get_current_job()
    if job:
        job.meta['status'] = status
        job.save_meta()

def _write_task_results(data):
    job = get_current_job()
    if job is None:
        # TODO: Raise exception
        return
    else:
        filename = job.get_id()
    # TODO: Put this in config file without using current_app
    path = 'rq_results/'
    f = open(path + filename, "w")
    # Write list
    if type(data) == type([]):
        for row in data:
            f.write(str(row) + '\n')
    f.close()

# Get full results for a UCSF IDL API request.
# Does this by concatenating all 100-item pages.
# Returns list of document IDs matching the query.

def ucsf_api_aggregate(query):
    # RQ setup.
    job = get_current_job()
    if job: 
        print("Job exists (%s)" % job.get_id())
        _set_task_status('Running')
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

    _write_task_results(doc_ids)
    _set_task_status('Done')

    return doc_ids