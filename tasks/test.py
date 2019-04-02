from tasks import *

w = {}
w["health"] = ["health", "research", "1", "ucsf"]
w["science"] = ["research", "science", "study"]
w["industry"] = ["market", "industry", "business", "profit", "corporation", "marketing"]

def get_file_list(file_list_path, include_without_year = False):
    file_list_file = open("rq_results/" + file_list_path)
    def extract(line):
        line = line.split(" ")
        line[0] += ".clean"
        if len(line) > 1:
            line[1] = int(line[1][:-1])
        return tuple(line)

    file_list = map(lambda line: extract(line), file_list_file.readlines())
    
    if not include_without_year:
        # Remove files without years.
        file_list = list(filter(lambda x: len(x) > 1, file_list))

    return file_list

print(get_word_family_graph(get_file_list("dummy"), w, False))