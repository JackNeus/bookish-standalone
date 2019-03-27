import nltk

nltk.download("stopwords")
stopwords = set(nltk.corpus.stopwords.words('english'))
# From Dov's code.
stopwords |= set([
",","t", "w", "f", "industrydocuments.library.ucsf.edu","c", "I", "t", "e", "n",
"r", "l", "o", "s", "ot", "á", "áá", "k", "th", "y", "d", "ii", "p", "b", "u", 
"h", "j", "m", "st", "http", "1n", "v", "z", "g", "er", "io", "lo", "al", "jstor"
, "re", "ll", "II", "x", "q", "ia", "ti", "li", "ar", "1t", "ol", "de", "es", 
"1s", "fi", "ui", "s1", "lu", "downloaded", "j", "j j", "â", "á1", "ji", "il", 
"cl", "ucsf", "edu", "website", "web site", "web_site", "tt", "tobacco_docs", 
"docs", "ir", "ve", "tl", "ci", "ho", "cu", "cf", "pgnbr", "https", "ï", "ff", 
"nf", "l.l"])
# Ignore single digits as well.
stopwords |= set([str(x) for x in range(10)])