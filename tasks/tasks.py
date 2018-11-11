# This file will contain all possible background jobs that the user can run.

import math
import os
import requests
import subprocess
from collections import defaultdict
from rq import get_current_job
from flask import current_app
from multiprocessing import Pool, Queue

from tasks.util import *

def resolve_task(task_name):
    if task_name == "ucsf_api_aggregate":
        return ucsf_api_aggregate
    if task_name == "ngram":
        return word_freq
    return None

# Get full results for a UCSF IDL API request.
# Does this by concatenating all 100-item pages.
# Returns list of document IDs matching the query.

def ucsf_api_aggregate(query):
    init_job()
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

        def extract_data(doc_metadata):
            document_year = ""
            if "documentdate" in doc_metadata:
                document_year = " " + doc_metadata["documentdate"][:4]
            document_id = doc_metadata["id"]
            document_location = "txt/ucsf/" + "/".join([c for c in document_id[:4]] + [document_id]) 
            return document_location + document_year 

        doc_ids.extend(list(map(extract_data, r["response"]["docs"])))
        print("Done page %d." % page)

        # Update RQ progress, if job is being run as an RQ task.
        set_task_progess(100.0 * (page + 1) / num_pages)

    return_from_task(doc_ids)

def word_freq(file_list_path, keywords):
    start_job()
    file_list_file = open(app.config["TASK_RESULT_PATH"] + file_list_path)
    file_list = map(lambda x: x.split(" "), file_list_file.readlines())
    # Remove files without years.
    file_list = dict(filter(lambda x: len(x) > 1, file_list))
    return_from_task(_word_freq(file_list, keywords))

def _word_freq(files, keywords):
    to_process = len(files)
    processed = 0

    # Return the following tuple (year, word freq dict)
    def _get_word_freq(file_data, keywords):
        filename, fileyear = file_data
        file = open(filename, "r").readlines()
        freqs = init_dict(keywords, 0)
        for word in file:
            if word in keywords:
                freq[word] += 1
        processed += 1

        # TODO: More sophisticated method of only updating at certain milestones?
        if processed % 100 == 0:
            set_task_progess(100.0 * processed / to_process)
        return (fileyear, freqs, len(file))

    # TODO: Replace constant with config variable
    word_freqs = Pool(1).map(_get_word_freq, files)

    # Merge dictionaries.
    years = [x[1] for x in files]
    min_year = min(years)
    max_year = max(years)
    years = range(min_year, max_year+1)

    global_word_freqs = init_dict(years, {})
    corpus_size = init_dict(years, 0)
    for year, freqs, file_size in word_freqs:
        global_word_freqs[year] += freqs
        corpus_size[year] += file_size

    # Convert absolute count to percentage
    for year in global_word_freqs:
        if corpus_size[year] != 0:
            global_word_freqs[year] = {k: v / corpus_size[year] * 100 for k, v in global_word_freqs[year]}

    return global_word_freqs

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