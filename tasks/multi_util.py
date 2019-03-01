from collections import defaultdict

# items is a list of (key, value, size)
# will return a list of tuples of the form ([value1, value2, ...], key)
def partition(items, max_partition_size):
	partitions = []

	current_partition = list()
	current_partition_key = None
	current_partition_size = 0

	items.sort(key = lambda x: x[0])
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

# TODO: unit tests