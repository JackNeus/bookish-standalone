#!/usr/bin/env python3
import argparse
from collections import defaultdict
import copy
from itertools import repeat, starmap
import json
import os
import sys
import time


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


# We use this function to concisely define multi-level dictionaries properly
# (the naive approach copies the inner dictionary by reference instead of value)
def init_dict(keys, default_value):
    new_dict = {}
    for k in keys:
        new_dict[k] = copy.deepcopy(default_value)
    return new_dict


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


# Handy little recursive function for serializing result objects.
def dump_task_results(data):
    if isinstance(data, list):
        result = ""
        for row in data:
            result += dump_task_results(row) + '\n'
        return result
    elif isinstance(data, dict):
        return json.dumps(data)
    else:
        return str(data) + '\n'


def main():
    args = parser.parse_args(sys.argv[1:])
    print(args)
    file_list = []
    for line in args.file_list.readlines():
        line = line.strip().split()
        file_list.append((os.path.join(args.file_prefix,
                                       line[0]), int(line[1])))

    epoch = int(time.time())
    output_filename = "%s%s.analysis" % (args.task, epoch)
    if args.dest:
        if os.path.exists(args.dest) and not args.force_dest:
            sys.exit(
                "Output file %s already exists. Please rerun with -f or provide a different filename."
                % args.dest)
        output_filename = args.dest

    res = None
    if args.task == "word_freq":
        res = word_freq(file_list, args.keywords)

    output_file = open(output_filename, "w")
    output_file.write(dump_task_results(res))
    output_file.close()
    print("Results written to %s." % output_filename)


if __name__ == "__main__":
    main()