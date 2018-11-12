# This file will contain all possible background jobs that the user can run.

import math
import multiprocessing
import os
import requests
import subprocess
import queue
from collections import defaultdict
from itertools import repeat
from rq import get_current_job
from flask import current_app

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
    set_task_size(num_pages)
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
            document_location = "txt/ucsf/" + "/".join([c for c in document_id[:4]] + [document_id, document_id]) + ".ocr"
            return document_location + document_year 

        doc_ids.extend(list(map(extract_data, r["response"]["docs"])))
        print("Done page %d." % page)

        # Update RQ progress, if job is being run as an RQ task.
        inc_task_processed()

    return_from_task(doc_ids)

def word_freq(file_list_path, keywords):
    init_job()
    
    if isinstance(keywords, str):
        keywords = keywords.split()

    # TODO: Replace rq_results with a config file.
    # TODO: Make sure file_list_path is a valid task ID.
    file_list_file = open('rq_results/' + file_list_path)
    def extract(line):
        line = line.split(" ")
        line[0] += ".clean"
        line[1] = int(line[1][:-1])
        return tuple(line)

    file_list = map(lambda line: extract(line), file_list_file.readlines())
    # Remove files without years.
    file_list = list(filter(lambda x: len(x) > 1, file_list))

    set_task_size(len(file_list))
    print("Analyzing %d files" % len(file_list))
    return_from_task(word_freq_helper(file_list, keywords))

def word_freq_helper(files, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]
    # Remove duplicates and make all keywords lowercase.
    keywords = [keyword.lower() for keyword in set(keywords)]
    to_process = len(files)

    word_freqs = multiprocessing.Pool(1).starmap(get_word_freq, zip(files, repeat(keywords)))
    # Currrently, discard any files that couldn't be found.
    word_freqs = filter(lambda x: x is not None, word_freqs)

    # Merge dictionaries.
    years = [x[1] for x in files]
    min_year = int(min(years))
    max_year = int(max(years))
    years = range(min_year, max_year+1)
    global_word_freqs = init_dict(keywords, init_dict(years, 0))
    corpus_size = init_dict(years, 0)
    for year, freqs, file_size in word_freqs:
        for word, frequency in freqs.items():
            global_word_freqs[word][year] += frequency
        corpus_size[year] += file_size
    # Convert absolute count to percentage
    #for year in global_word_freqs:
    #    if corpus_size[year] != 0:
    #        global_word_freqs[year] = {k: v / corpus_size[year] * 100 for k, v in global_word_freqs[year].items()}

    return global_word_freqs

def get_word_freq(file_data, keywords):
    filename, fileyear = file_data
    # TODO: Determine behavior when a file can't be found.
    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        return None
    file = list(map(lambda x: x.strip(), file.readlines()))
    freqs = init_dict(keywords, 0)
    for word in file:
        word = word.lower()
        if word in keywords:
            freqs[word] += 1
    inc_task_processed()
    return (fileyear, freqs, len(file))

# This job will probably never be client-facing, as it only needs to be run once.
def clean(files):
    def job_body(input_queue):
        print("Entered.")
        while not input_queue.empty():
            file_path = input_queue.get()
            subprocess.check_output(['./jobs/clean.sh', file_path])
            input_queue.task_done()
    util.multi_work(job_body, files, num_threads = 3)

'''
# Temporary. Comment this out before running the actual app.
txt = []
for subdir, dirs, files in os.walk("../txt/ucsf/"):
    for file in files:
        txt.append(subdir + "/" + file)

clean(txt + txt)
print("Done.")
'''