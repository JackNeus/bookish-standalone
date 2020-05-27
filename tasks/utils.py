from collections import defaultdict
import copy
from itertools import starmap
import json


# We use this function to concisely define multi-level dictionaries properly
# (the naive approach copies the inner dictionary by reference instead of value)
def init_dict(keys, default_value):
    new_dict = {}
    for k in keys:
        new_dict[k] = copy.deepcopy(default_value)
    return new_dict


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


def partition_map(map_func,
                  items,
                  size_func=lambda *a: 1,
                  max_partition_size=100):
    items = [item + (size_func(item), ) for item in items]
    partitions = partition(items, max_partition_size)
    # In theory, can be replaced with multiprocessing.starmap
    mapped_values = starmap(map_func, partitions)
    return mapped_values

    # Calculate max_partition_size in bytes.
    #bytes_per_gb = 1024 * 1024 * 1024
    #usable_memory = 1 * bytes_per_gb
    #max_partition_size = usable_memory / config["NUM_CORES"]


# items is a list of (key, value, size)
# will return a list of tuples of the form ([value1, value2, ...], key)
def partition(items, max_partition_size):
    partitions = []

    current_partition = list()
    current_partition_key = None
    current_partition_size = 0

    items.sort(key=lambda x: x[0])
    for item in items:
        key, value, size = item
        # This guarantees that even items with size > max_partition_size will
        # make it into a partition.
        if key != current_partition_key or current_partition_size + size > max_partition_size:
            if len(current_partition) > 0:
                partitions.append((current_partition, current_partition_key))
            current_partition = [value]
            current_partition_key = key
            current_partition_size = size
        else:
            current_partition.append(value)
            current_partition_size += size

    if len(current_partition) > 0:
        partitions.append((current_partition, current_partition_key))

    return partitions