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
from rq import get_current_job
from flask import current_app

from tasks.util import *

nltk.download("stopwords")
stopwords = set(nltk.corpus.stopwords.words('english'))

def resolve_task(task_name):
    if task_name == "ucsf_api_aggregate" or task_name == "ucsf_api_aggregate_task":
        return ucsf_api_aggregate_task
    if task_name == "ngram" or task_name == "word_freq_task":
        return word_freq_task
    if task_name == "top_bigrams" or task_name == "top_bigrams_task":
        return top_bigrams_task
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
    file_list = get_file_list(file_list_path)

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

def top_bigrams_task(file_list_path):
    init_job([file_list_path])
    file_list = get_file_list(file_list_path)

    set_task_size(len(file_list))
    set_task_metadata("files_analyzed", 0)
    return_from_task(get_top_bigrams(file_list))

def get_top_bigrams(files):
    bigram_freqs = partition_map(get_bigrams, [x[::-1] for x in files])
    # Currently, discard any files that couldn't be found.
    bigram_freqs = [x for x in bigram_freqs if x is not None]
    push_metadata_to_db("files_analyzed", force = True)

    # Merge dictionaries.
    years = [x[1] for x in files]
    min_year = int(min(years))
    max_year = int(max(years))
    years = range(min_year, max_year+1)

    global_freqs = init_dict(years, defaultdict(lambda: 0, {}))
    total_bigram_counts = init_dict(years, 0)
    for year, freqs, file_size in bigram_freqs:
        total_bigram_counts[year] += file_size ** 2
        for bigram, freq in freqs.items():
            global_freqs[year][bigram] += freq
    for year in global_freqs.keys():
        # Only return bigrams that make up more than .5% of all bigrams for that year.
        #freq_threshold = 0.005 * total_bigram_counts[year]
        freq_threshold = 25
        global_freqs[year] = {";".join(k):v for (k,v) in global_freqs[year].items() if v >= freq_threshold}
    
    return global_freqs

def get_bigrams(files, year):
    # Still works with singletons.
    if not isinstance(files, list):
        files = [files]

    bigrams = defaultdict(lambda: 0, {})
    file_length = 0

    for filename in files:
        try:
            file = open(filename, "r")
        except FileNotFoundError as e:
            continue
        
        file = list(map(lambda x: x.strip(), file.readlines()))
        for i in range(len(file) - 1):
            if file[i+1] in stopwords:
                i += 1
                continue
            if file[i] in stopwords:
                continue
            bigram = tuple(sorted((file[i], file[i+1])))
            bigrams[bigram] += 1
        file_length += len(files)

        inc_task_processed()
        push_metadata_to_db("files_analyzed")
    return (year, dict(bigrams), file_length)