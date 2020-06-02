# Stopwords downloaded using on 6/1/20. We use a snapshot to avoid an nltk dependency
# (which is not installed on university machines)

# nltk.download("stopwords", quiet=True)
# stopwords = set(nltk.corpus.stopwords.words('english'))
stopwords = set({
    'hers', 're', 'have', 'doesn', 'at', 'some', 'below', 'they', "won't",
    'we', "she's", "shouldn't", 'during', 'doing', 'with', 'i', 'by', 'aren',
    'don', 'in', 'after', 'mustn', 'as', 'own', 'if', 'those', "weren't", 'on',
    'm', "wasn't", "haven't", 'not', 'yourselves', 'about', "needn't",
    'themselves', 'her', "you'll", 'there', 'should', 'that', 'yourself',
    'the', 'for', 'too', 'between', 'here', 'needn', 'ours', "isn't",
    'shouldn', 'haven', 'these', 'had', 'while', 'shan', 'won', 'under', 'how',
    'because', 'do', "should've", 'myself', 'an', 'such', "you'd", 'only',
    "hadn't", 'from', 'further', 'no', 'nor', 'same', 'who', "don't", 'but',
    'has', 'than', 'both', "that'll", 'ourselves', 'couldn', 'weren', 'wouldn',
    'most', 've', 'which', 'herself', 'y', 'other', 'him', 'be', 'been',
    'then', 'are', 'me', "you've", 'before', 'their', 'were', 'ain', 'them',
    'why', "aren't", 'out', 'so', 'll', 'against', 'through', 'more', 'a',
    'any', 'hadn', 'did', 'he', 'your', 'what', 'mightn', 'hasn', 'very',
    'his', 'and', 'up', 'she', 'isn', 'where', "wouldn't", 'whom', 'again',
    'you', 'being', 'wasn', 'few', 'having', 'my', 'now', 'when', "hasn't",
    'd', 'of', 'down', "mightn't", 'itself', 'is', "it's", "didn't", 'off',
    'didn', 'ma', 'all', 'theirs', 'over', 'will', 'just', 's', 'once', 'its',
    'or', 'to', 'himself', 'until', 'our', "shan't", 'this', 't', 'am',
    "couldn't", 'o', 'above', "doesn't", 'into', 'can', 'does', "you're",
    "mustn't", 'it', 'was', 'each', 'yours'
})
# From Dov Grohsgal's code.
stopwords |= set([
    ",", "t", "w", "f", "industrydocuments.library.ucsf.edu", "c", "I", "t",
    "e", "n", "r", "l", "o", "s", "ot", "á", "áá", "k", "th", "y", "d", "ii",
    "p", "b", "u", "h", "j", "m", "st", "http", "1n", "v", "z", "g", "er",
    "io", "lo", "al", "jstor", "re", "ll", "II", "x", "q", "ia", "ti", "li",
    "ar", "1t", "ol", "de", "es", "1s", "fi", "ui", "s1", "lu", "downloaded",
    "j", "j j", "â", "á1", "ji", "il", "cl", "ucsf", "edu", "website",
    "web site", "web_site", "tt", "tobacco_docs", "docs", "ir", "ve", "tl",
    "ci", "ho", "cu", "cf", "pgnbr", "https", "ï", "ff", "nf", "l.l"
])
# Ignore single digits as well.
stopwords |= set([str(x) for x in range(10)])