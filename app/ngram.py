import math
import os, glob
import requests
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from rq import get_current_job

def multi_ngram():
	os.chdir("txt/CRS_carcinogens")

	for file in glob.glob("*.txt"):
		text = open(file, "r").read()
		
		keywords = ["carcinogen", "carcinogenic", "mutagen", "cancer gene"]
		print(file,len(text))
		for keyword in keywords:
			print(keyword, text.count(keyword))
		print("")

def ngram(word, divide):	
	freq = {}
	size = {}
	for file in glob.glob("txt/CRS_carcinogens/*.txt"):
		text = open(file, "r").read()
		base_file_name = file[20:-4]
		year = int(base_file_name[3:7])
		#freq[file[20:-4]] = text.count(word)
		freq[year] = text.count(word)
		if year not in size:
			size[year] = len(text)
		else:
			size[year] += len(text)
	min_year = min(freq.keys())
	max_year = max(freq.keys())
	print(freq, size)
	for year in range(min_year, max_year+1):
		if year not in freq:
			freq[year] = 0
		elif divide and size[year] != 0:
			freq[year] = freq[year] * 1.0 / size[year] * 100
	for year in freq:
		freq[year] = "%.6f" % freq[year]
	return freq

def ucsf_aggregate(query):
	base_url = "http://solr.industrydocumentslibrary.ucsf.edu/solr/ltdl3/query"
	parameters = {"q": query,
				  "wt": "json"}
	r = requests.get(url = base_url, params = parameters)
	r = r.json()
	total_items = r["response"]["numFound"]
	page_size = 100
	num_pages = math.ceil(total_items * 1.0 / page_size)
	print("%d pages total." % num_pages)
	doc_ids = []
	for page in range(num_pages):
		parameters["start"] = page * page_size
		r = requests.get(url = base_url, params = parameters)
		r = r.json()
		doc_ids.extend(list(map(lambda x: x["id"], r["response"]["docs"])))
		print("Done page %d." % page)
	return doc_ids