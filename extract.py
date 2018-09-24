import PyPDF2
import glob, os

os.chdir("txt/CRS_carcinogens")
# Get base file names (no extension) of extracted files.
already_extracted = map(lambda x: x[:-4], glob.glob("*.txt"))

os.chdir("../../docs/CRS_carcinogens")
for file in glob.glob("*.pdf"):
	# File has already been extracted.
	if file[:-4] in already_extracted:
		continue

	pdfFileObj = open(file, 'rb')

	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	num_pages = pdfReader.numPages
	pages = [pdfReader.getPage(i) for i in range(num_pages)]
	page_text = [page.extractText() for page in pages]
	pdf_text = ''.join(page_text)

	print(file, num_pages, len(pdf_text))
	txtFileObj = open('../../txt/CRS_carcinogens/' + file[:-4] + ".txt", "w")
	txtFileObj.write(pdf_text)
	txtFileObj.close()
	print("Text successfully extracted.")