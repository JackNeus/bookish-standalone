import os, glob
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

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
			size[year] = 0
		else:
			size[year] += len(text)
	min_year = min(freq.keys())
	max_year = max(freq.keys())
	for year in range(min_year, max_year):
		if year not in freq:
			freq[year] = 0
		elif divide and size[year] != 0:
			freq[year] /= size[year]
	return freq