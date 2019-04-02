# This file will contain all possible background jobs that the user can run.
import math
import os
import copy
import requests
import shlex
import subprocess
import queue
from collections import defaultdict
from itertools import repeat
from rq import get_current_job
from flask import current_app

# Conditional imports so task helper functions can be run outside
# of the application context.
if os.environ.get("in_bookish"):
    from tasks.util import *
    from tasks.stopwords import stopwords
else:
    from util import init_dict
    from stopwords import stopwords

def resolve_task(task_name):
    if task_name == "ucsf_api_aggregate" or task_name == "ucsf_api_aggregate_task":
        return ucsf_api_aggregate_task
    if task_name == "ngram" or task_name == "word_freq_task":
        return word_freq_task
    if task_name == "top_bigrams" or task_name == "top_bigrams_task":
        return top_bigrams_task
    if task_name == "word_families" or task_name == "word_family_graph_task":
        return word_family_graph_task
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
    # TODO: Handle .lower() here.
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
        #freq_threshold = 25
        #global_freqs[year] = {";".join(k):v for (k,v) in global_freqs[year].items() if v >= freq_threshold}
        global_freqs[year] = n_highest_entries(global_freqs[year], 50)

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
        
        file_bigrams = defaultdict(lambda: 0)
        # TODO: Handle .lower() here.
        file = list(map(lambda x: x.strip(), file.readlines()))
        for i in range(len(file) - 1):
            if file[i+1] in stopwords:
                i += 1
                continue
            if file[i] in stopwords:
                continue
            bigram = tuple((file[i], file[i+1]))
            file_bigrams[bigram] += 1

        # Only take the top 50 bigrams for an individual file.
        file_bigrams = n_highest_entries(file_bigrams, 50)
        # Merge dictionaries.
        for key, value in file_bigrams:
            bigrams[key] += value

        file_length += len(files)

        inc_task_processed()
        push_metadata_to_db("files_analyzed")
    return (year, dict(bigrams), file_length)

def word_family_graph_task(file_list_path, word_families):
    init_job([file_list_path, word_families])
    if isinstance(word_families, str):
        word_families = word_families.split(";")
        word_families = [x.split(",") for x in word_families]
    file_list = get_file_list(file_list_path)

    set_task_size(len(file_list))
    set_task_metadata("files_analyzed", 0)
    return_from_task(get_word_family_graph(file_list, word_families))

def get_word_family_graph(file_list, word_families, in_app = True):
    keywords = []
    if isinstance(word_families, dict):
        word_families = word_families.values()
    for family in word_families:
        keywords = keywords + family
    # Remove stopwords.
    keywords = filter(lambda x: x not in stopwords, keywords)
    # Remove duplicates.
    keywords = list(set(keywords))
    
    if in_app:
        word_family_data = get_pool().starmap(get_word_family_data, zip(file_list, repeat(keywords)))
    else:
        word_family_data = list(map(lambda x: get_word_family_data(x, keywords, in_app), file_list))

    # Merge dictionaries.
    years = [x[1] for x in file_list]

    empty_fcm = defaultdict(lambda: copy.deepcopy(defaultdict(lambda: 0)))
    fcms = init_dict(years, empty_fcm)
    word_freqs = defaultdict(lambda: 0, [])
    # Merge fcms by year.
    for year, file_fcm, file_word_freqs in word_family_data:
        for keyword in file_fcm:
            word_freqs[keyword] += file_word_freqs[keyword]
            for word, gfreq in file_fcm[keyword].items():
                fcms[year][keyword][word] += gfreq

    # Convert from defaultdicts to dicts.
    fcms = dict(fcms)
    for year in fcms:
        fcms[year] = dict(fcms[year])
        for keyword in fcms[year]:
            fcms[year][keyword] = dict(fcms[year][keyword])
    word_freqs = dict(word_freqs)

    # Normalize word freq table to [0, 1].
    if len(word_freqs) > 0:
        min_freq = min(word_freqs.values())
        max_freq = max(word_freqs.values())
        for word, freq in word_freqs.items():
            word_freqs[word] = (freq - min_freq) / (max_freq - min_freq)

    # Adjust weights in fcms
    for year in fcms:
        max_edge_val = 0
        # weight = log(1 + weight)
        for keyword in fcms[year]:
            for word, val in fcms[year][keyword].items():
                fcms[year][keyword][word] = math.log(1+val)
                max_edge_val = max(max_edge_val, fcms[year][keyword][word])
        # normalize so <= 1
        if max_edge_val != 0:
            for keyword in fcms[year]:
                for word, val in fcms[year][keyword].items():
                    fcms[year][keyword][word] = val / max_edge_val

    return [fcms, word_freqs]

def get_word_family_data(file_data, keywords, in_app = True):
    filename, fileyear = file_data
    # TODO: Determine behavior when a file can't be found.
    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        return None
    # TODO: Remove call to lower()
    file = list(map(lambda x: x.strip().lower(), file.readlines()))
    
    sigma = 5
    window_size = 4 * sigma
    weights = [math.exp((-x**2)/(2*sigma))/sigma for x in range(0, window_size+1)]

    # Only calculate fcm for keywords that appear in the file.
    keywords = list(filter(lambda x: x in file, keywords))

    # Compute feature co-ocurrence matrix using a 
    # Gaussian weighting of word frequencies.
    fcm = init_dict(keywords, {x: 0 for x in keywords})
    # Also, build a frequency table for the keywords.
    word_freq = init_dict(keywords, 0)
    for i in range(len(file)):
        if file[i] not in keywords:
            continue
        word_freq[file[i]] += 1
        for j in range(max(0, i - window_size), min(len(file), i + window_size + 1)):
            # Don't want to compare word to itself.
            if i == j:
                continue
            if file[j] in keywords:
                fcm[file[i]][file[j]] += weights[abs(i - j)]
                # Avoid double counting if the words are the same.
                if file[i] != file[j]:
                    fcm[file[j]][file[i]] += weights[abs(i - j)]

    if in_app:
        inc_task_processed()
        push_metadata_to_db("files_analyzed")
    return (fileyear, fcm, word_freq)
