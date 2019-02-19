# This file will contain all possible background jobs that the user can run.
import nltk
import math
import os
import requests
import shlex
import subprocess
import queue
from collections import defaultdict
from itertools import repeat
from nltk.corpus import stopwords
from rq import get_current_job
from flask import current_app

from tasks.util import *

def resolve_task(task_name):
    if task_name == "ucsf_api_aggregate" or task_name == "ucsf_api_aggregate_task":
        return ucsf_api_aggregate_task
    if task_name == "ngram" or task_name == "word_freq_task":
        return word_freq_task
    if task_name == "top_bigrams":
        return get_top_bigrams_task
    return None

# Get full results for a UCSF IDL API request.
# Does this by concatenating all 100-item pages.
# Returns list of document IDs matching the query.

def ucsf_api_aggregate_task(query):
    init_job([query])

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
    files_found = 0
    set_task_metadata("files_count", total_items)
    set_task_metadata("files_found", files_found)
    
    # Calculate number of pages.
    num_pages = math.ceil(total_items * 1.0 / page_size)
    set_task_size(num_pages)
    print("%d pages total." % num_pages)

    output_file = open_task_output_file()

    # Request each page.
    for page in range(num_pages):
        parameters["start"] = page * page_size
        try:
            r = requests.get(url = base_url, params = parameters)
            r = r.json()
        except:
            continue

        def extract_data(doc_metadata):
            document_year = ""
            if "documentdate" in doc_metadata:
                document_year = " " + doc_metadata["documentdate"][:4]
            document_id = doc_metadata["id"]
            document_location = "txt/ucsf/" + "/".join([c for c in document_id[:4]] + [document_id, document_id]) + ".ocr"
            return document_location + document_year 

        doc_ids = list(map(extract_data, r["response"]["docs"])) 
        write_task_results(doc_ids, output_file)

        files_found += len(doc_ids)
        set_task_metadata("files_found", files_found)
        

        print("Done page %d." % page)

        # Update RQ progress, if job is being run as an RQ task.
        inc_task_processed()

    output_file.close()

# Top level task function.
def word_freq_task(file_list_path, keywords):
    if isinstance(keywords, str):
        keywords = shlex.split(keywords)
    init_job([file_list_path, " ".join(keywords)])

    # TODO: Make sure file_list_path is a valid task ID.
    file_list_file = open(config["TASK_RESULT_PATH"] + file_list_path)
    def extract(line):
        line = line.split(" ")
        line[0] += ".clean"
        if len(line) > 1:
            line[1] = int(line[1][:-1])
        return tuple(line)

    file_list = map(lambda line: extract(line), file_list_file.readlines())
    # Remove files without years.
    file_list = list(filter(lambda x: len(x) > 1, file_list))

    set_task_size(len(file_list))
    print("Analyzing %d files" % len(file_list))
    set_task_metadata("files_analyzed", 0)
    return_from_task(word_freq(file_list, keywords))

# Generic word freq function.
def word_freq(files, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]
    # Remove duplicates and make all keywords lowercase.
    keywords = [keyword.lower() for keyword in set(keywords)]
    to_process = len(files)

    word_freqs = get_pool().starmap(get_word_freq, zip(files, repeat(keywords)))
    # Currrently, discard any files that couldn't be found.
    word_freqs = [x for x in word_freqs if x is not None]
    set_task_metadata("files_analyzed", len(word_freqs))

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
    for keyword in global_word_freqs:
        for year in global_word_freqs[keyword]:
            val = global_word_freqs[keyword][year]
            if corpus_size[year] != 0:
                val = val / corpus_size[year] * 100
            global_word_freqs[keyword][year] = float("%.6f" % val)

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
    push_metadata_to_db("files_analyzed")
    return (fileyear, freqs, len(file))

def get_top_bigrams_task(file_list_path):
    init_job([file_list_path])

    # TODO: Make sure file_list_path is a valid task ID.
    file_list_file = open(config["TASK_RESULT_PATH"] + file_list_path)
    def extract(line):
        line = line.split(" ")
        line[0] += ".clean"
        if len(line) > 1:
            line[1] = int(line[1][:-1])
        return tuple(line)

    file_list = map(lambda line: extract(line), file_list_file.readlines())
    # Remove files without years.
    file_list = list(filter(lambda x: len(x) > 1, file_list))

    set_task_size(len(file_list))
    set_task_metadata("files_analyzed", 0)
    return_from_task(get_top_bigrams(file_list))

def get_top_bigrams(files):
    to_process = len(files)

    bigram_freqs = get_pool().starmap(get_bigrams, files)
    # Currently, discard any files that couldn't be found.
    bigram_freqs = [x for x in word_freqs if x is not None]
    set_task_metadata("files_analyzed", len(word_freqs))

    # Merge dictionaries.
    years = [x[1] for x in files]
    min_year = int(min(years))
    max_year = int(max(years))
    years = range(min_year, max_year+1)

    global_freqs = init_dict(years, defaultdict(lambda x: 0, {}))

    for year, freqs in bigram_freqs:
        for bigram, freq in freqs:
            global_freqs[year][bigram] += freq
    global_freqs = {k:v for (k,v) in d.items() if v >= 20}

    return global_freqs


def get_bigrams(file_data):
    filename, fileyear = file_data

    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        return None
    
    file = list(map(lambda x: x.strip(), file.readlines()))
    bigrams = defaultdict(lambda: 0, {})
    stop_words = set(stopwords.words('english'))
    for i in range(len(file) - 1):
        if file[i+1] in stop_words:
            i += 1
            continue
        if file[i] in stop_words:
            continue
        bigram = tuple(sorted((file[i], file[i+1])))
        bigrams[bigram] += 1

    return (fileyear, bigrams)



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
i = 0
for subdir, dirs, files in os.walk("../txt/ucsf/"):
    for file in files:
        txt.append((subdir + "/" + file, 1900 + i % 10))
        i += 1
print(txt[:10])
print(get_top_bigrams(txt))
print("Done.")
'''