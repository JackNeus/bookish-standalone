#!/usr/bin/env python3
import argparse
from collections import defaultdict
import copy
from itertools import repeat, starmap
import math
import os
import sys
import time

from utils import *
from html import *
from stopwords import stopwords


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    elif os.path.isdir(arg):
        parser.error("%s is a directory!" % arg)
    else:
        return open(arg, 'r')


def is_valid_directory(parser, arg):
    if arg == "":
        return arg
    if not os.path.exists(arg):
        parser.error("The directory %s does not exist!" % arg)
    elif not os.path.isdir(arg):
        parser.error("%s is not a directory!" % arg)
    else:
        return arg


parser = argparse.ArgumentParser(
    description='Textual Analysis Tool for Standalone Bookish')
parser.add_argument('file_list',
                    help='File containing list of files to Analyze',
                    type=lambda x: is_valid_file(parser, x))
parser.add_argument('--prefix',
                    dest='file_prefix',
                    help='Common prefix for input files',
                    type=lambda x: is_valid_directory(parser, x),
                    default="",
                    required=False)
parser.add_argument('--dest',
                    dest='dest',
                    help='Name of Output File',
                    type=str,
                    required=False)
parser.add_argument('-f',
                    dest='force_dest',
                    help='Force overwrite dest if file exists',
                    action='store_true')
parser.add_argument(
    '--raw',
    dest='raw_output',
    help='Output raw analysis results instead of visualization html file',
    action='store_true')

subparsers = parser.add_subparsers(
    title='Analysis Tasks',
    dest='task',
)
subparsers.required = True

word_freq_parser = subparsers.add_parser(
    'word_freq',
    help='Word Frequency Analysis',
)
word_freq_parser.add_argument("keywords",
                              nargs="+",
                              help='Keywords to analyze (case-insensitive)')

bigram_parser = subparsers.add_parser('bigram', help='Top Bigrams Analysis')

word_family_parser = subparsers.add_parser('word_family',
                                           help='Word Family Graph Analysis')
word_family_parser.add_argument(
    metavar="family",
    dest="word_families",
    nargs="+",
    help='Word families to analyze -- words in a family are comma separated')

# ---------- WORD FREQ ----------


# Generic word freq function.
def word_freq(files, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]
    # Remove duplicates and make all keywords lowercase.
    keywords = [keyword.lower() for keyword in set(keywords)]

    # This can be switched out to use multiprocessing.starmap if desired
    # TODO: make this a cmd line arg
    word_freqs = starmap(get_word_freq, zip(files, repeat(keywords)))

    # Currently, discard any files that couldn't be found.
    word_freqs = [x for x in word_freqs if x is not None]

    # Merge dictionaries.
    years = [x[1] for x in files]
    min_year = int(min(years))
    max_year = int(max(years))
    years = range(min_year, max_year + 1)
    global_word_freqs = init_dict(keywords, init_dict(years, 0))
    corpus_size = init_dict(years, 0)
    metadata = init_dict(years, defaultdict(lambda: 0, {}))

    # Add results for each file to the appropriate overall bucket
    # for that file's year.
    for year, freqs, file_size in word_freqs:
        for word, frequency in freqs.items():
            global_word_freqs[word][year] += frequency
        corpus_size[year] += file_size
        metadata[year]["Files Analyzed"] += 1
        metadata[year]["Total Word Count"] += file_size

    # Convert absolute count to percentage
    for keyword in global_word_freqs:
        for year in global_word_freqs[keyword]:
            val = global_word_freqs[keyword][year]
            if corpus_size[year] != 0:
                val = val / corpus_size[year] * 100
            global_word_freqs[keyword][year] = float("%.6f" % val)

    return [global_word_freqs, metadata]


def get_word_freq(file_data, keywords):
    filename, fileyear = file_data
    # TODO: Determine behavior when a file can't be found.
    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        print("Could not find %s. Skipping..." % filename)
        return None
    # TODO: Handle .lower() here.
    file = list(map(lambda x: x.strip(), file.readlines()))
    freqs = init_dict(keywords, 0)
    for word in file:
        word = word.lower()
        if word in keywords:
            freqs[word] += 1
    return (fileyear, freqs, len(file))


# ---------- BIGRAM ----------


def get_top_bigrams(files):
    bigram_freqs = partition_map(get_bigrams, [x[::-1] for x in files])
    # Currently, discard any files that couldn't be found.
    bigram_freqs = [x for x in bigram_freqs if x is not None]

    # Merge dictionaries.
    years = [x[1] for x in files]

    global_freqs = init_dict(years, defaultdict(lambda: 0, {}))
    total_bigram_counts = init_dict(years, 0)
    metadata = init_dict(years, defaultdict(lambda: 0, {}))
    for year in years:
        metadata[year]["Files Analyzed"] += 1

    for year, freqs, file_size in bigram_freqs:
        total_bigram_counts[year] += file_size**2
        for bigram, freq in freqs.items():
            global_freqs[year][bigram] += freq
        metadata[year]["Total Word Count"] += file_size
    for year in global_freqs.keys():
        # Only return bigrams that make up more than .5% of all bigrams for that year.
        #freq_threshold = 0.005 * total_bigram_counts[year]
        #freq_threshold = 25
        #global_freqs[year] = {";".join(k):v for (k,v) in global_freqs[year].items() if v >= freq_threshold}
        global_freqs[year] = n_highest_entries(global_freqs[year], 50)

    return [global_freqs, metadata]


def n_highest_entries(d, n):
    if isinstance(d, dict):
        d = d.items()
    elif not isinstance(d, list):
        return None
    return sorted(d, key=lambda x: x[1], reverse=True)[:n]


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
        file = list(map(lambda x: x.strip().lower(), file.readlines()))
        for i in range(len(file) - 1):
            if file[i + 1] in stopwords:
                i += 1
                continue
            if file[i] in stopwords:
                continue
            bigram = tuple((file[i], file[i + 1]))
            file_bigrams[bigram] += 1

        # Only take the top 50 bigrams for an individual file.
        file_bigrams = n_highest_entries(file_bigrams, 50)
        # Merge dictionaries.
        for key, value in file_bigrams:
            bigrams[key] += value

        file_length += len(file)
    return (year, dict(bigrams), file_length)


# ---------- WORD FAMILY ----------


def get_word_family_graph(file_list, word_families):
    keywords = []
    if isinstance(word_families, list):
        temp = {}
        for i in range(len(word_families)):
            temp[i] = word_families[i]
        word_families = temp
    for family in word_families.values():
        keywords = keywords + family
    # Remove stopwords.
    keywords = filter(lambda x: x not in stopwords, keywords)
    # Remove duplicates.
    keywords = list(set(keywords))

    word_family_data = starmap(get_word_family_data,
                               zip(file_list, repeat(keywords)))

    # Merge dictionaries.
    years = [x[1] for x in file_list]

    empty_fcm = defaultdict(lambda: copy.deepcopy(defaultdict(lambda: 0)))
    fcms = init_dict(years, empty_fcm)
    word_freqs = init_dict(years, defaultdict(lambda: 0, []))
    metadata = init_dict(years, defaultdict(lambda: 0, []))

    # Merge fcms by year.
    for entry in word_family_data:
        if entry is None:
            continue
        year, file_fcm, file_word_freqs, word_count = entry
        metadata[year]["Files Analyzed"] += 1
        metadata[year]["Total Word Count"] += word_count
        for keyword in file_fcm:
            word_freqs[year][keyword] += file_word_freqs[keyword]
            for word, gfreq in file_fcm[keyword].items():
                fcms[year][keyword][word] += gfreq

    # Convert from defaultdicts to dicts.
    fcms = dict(fcms)
    word_freqs = dict(word_freqs)
    metadata = dict(metadata)
    for year in fcms:
        word_freqs[year] = dict(word_freqs[year])
        fcms[year] = dict(fcms[year])
        metadata[year] = dict(metadata[year])
        for keyword in fcms[year]:
            fcms[year][keyword] = dict(fcms[year][keyword])

    # Normalize word freq table to [0, 1].
    for year in word_freqs:
        if len(word_freqs[year]) > 0:
            min_freq = min(word_freqs[year].values())
            max_freq = max(word_freqs[year].values())
            for word, freq in word_freqs[year].items():
                freq_range = max_freq - min_freq
                if max_freq == min_freq:
                    freq_range = 1
                word_freqs[year][word] = (freq - min_freq) / freq_range

    # Adjust weights in fcms
    for year in fcms:
        max_edge_val = 0
        # weight = log(1 + weight)
        for keyword in fcms[year]:
            for word, val in fcms[year][keyword].items():
                fcms[year][keyword][word] = math.log(1 + val)
                max_edge_val = max(max_edge_val, fcms[year][keyword][word])
        # normalize so <= 1
        if max_edge_val != 0:
            for keyword in fcms[year]:
                for word, val in fcms[year][keyword].items():
                    fcms[year][keyword][word] = val / max_edge_val

    return [fcms, word_freqs, word_families, metadata]


def get_word_family_data(file_data, keywords):
    filename, fileyear = file_data

    # TODO: Determine behavior when a file can't be found.
    try:
        file = open(filename, "r")
    except FileNotFoundError as e:
        print("Could not find %s. Skipping..." % filename)
        return None
    # TODO: Remove call to lower()
    file = list(map(lambda x: x.strip().lower(), file.readlines()))

    sigma = 5
    window_size = 4 * sigma
    weights = [
        math.exp((-x**2) / (2 * sigma)) / sigma
        for x in range(0, window_size + 1)
    ]

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
        for j in range(max(0, i - window_size),
                       min(len(file), i + window_size + 1)):
            # Don't want to compare word to itself.
            if i == j:
                continue
            if file[j] in keywords:
                fcm[file[i]][file[j]] += weights[abs(i - j)]
                # Avoid double counting if the words are the same.
                if file[i] != file[j]:
                    fcm[file[j]][file[i]] += weights[abs(i - j)]
    return (fileyear, fcm, word_freq, len(file))


# ---------- MISC ----------


def main():
    args = parser.parse_args(sys.argv[1:])
    file_list = []
    for line in args.file_list.readlines():
        line = line.strip().split()
        file_list.append((os.path.join(args.file_prefix,
                                       line[0]), int(line[1])))

    epoch = int(time.time())
    output_filename = "%s%s.%s" % (args.task, epoch,
                                   "analysis" if args.raw_output else "html")
    if args.dest:
        if os.path.exists(args.dest) and not args.force_dest:
            sys.exit(
                "Output file %s already exists. Please rerun with -f or provide a different filename."
                % args.dest)
        output_filename = args.dest

    keys = None
    res = None
    if args.task == "word_freq":
        keys = ["word_freqs", "metadata"]
        res = word_freq(file_list, [x.lower() for x in args.keywords])
    elif args.task == "bigram":
        keys = ["word_freqs", "metadata"]
        res = get_top_bigrams(file_list)
    elif args.task == "word_family":
        keys = ["fcms", "word_freqs", "word_families", "metadata"]
        word_families = [[y.lower() for y in x.split(",")]
                         for x in args.word_families]
        res = get_word_family_graph(file_list, word_families)
    else:
        sys.exit("Unknown task.")

    enc_res = zip(keys + ["fileName"],
                  [json.dumps(x) for x in res] + [output_filename])
    js_vars = "\n\t\t".join(
        [localStorageTemplate % (k, data) for (k, data) in enc_res])
    vis_html = template % (js_vars, args.task)

    output_file = open(output_filename, "w")
    output_file.write(dump_task_results(res) if args.raw_output else vis_html)
    output_file.close()
    print("Results written to %s." % output_filename)


if __name__ == "__main__":
    main()