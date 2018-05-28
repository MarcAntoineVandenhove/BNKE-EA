#This program scans for PDF within children directories and extracts text off
#their first pages into a .csv file

import sys
import os
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, resolve1
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

import pandas as pd
import re

import time

from progress.bar import IncrementalBar

start = time.time()

parent_dir = sys.argv[1]

total_length = 0
for subdir in os.listdir(parent_dir):
	if os.path.isdir(parent_dir+'/'+subdir):
		total_length+=len(os.listdir(parent_dir+'/'+subdir))
bar = IncrementalBar('Processing PDFs', max =total_length)

columns = ["filename", "category", "size", "number_of_pages", "number_of_words",
 "meta_author", "meta_category", "meta_company", "meta_creation_date",
  "meta_subject", "meta_title", "first_page_text"]
my_dataframe = pd.DataFrame(index=[],columns=columns)

for subdir in os.listdir(parent_dir):
	if os.path.isdir(parent_dir+'/'+subdir):
		for file_ in os.listdir(parent_dir+'/'+subdir):
			file_extension = os.path.splitext(file_)[1]
			if file_extension == '.pdf':
				my_path = parent_dir + '/' + subdir + '/' + file_

				output = io.StringIO()
				manager = PDFResourceManager()
				converter = TextConverter(manager, output, laparams=None)
				interpreter = PDFPageInterpreter(manager, converter)

				infile = open(my_path,'rb')

				name = os.path.basename(my_path)[:-4]
				size = os.stat(my_path).st_size

				parser = PDFParser(infile)
				doc = PDFDocument(parser)

				metadata = doc.info
				my_metadata = []
				for key in ['Author','Category','Company','CreationDate',
				 'Subject','Title']:
				 my_metadata.append(metadata[0].get(key))

				page_count = resolve1(doc.catalog['Pages'])['Count']
				for page in PDFPage.get_pages(infile,caching=False):
					interpreter.process_page(page)
					break
				infile.close()
				converter.close()
				text = output.getvalue()
				output.close()

				word_count = len(text.split())
				my_info = [name, subdir, size, page_count, word_count] + my_metadata
				my_info.append(text)
				my_dataframe.loc[len(my_dataframe)] = my_info
				bar.next()
my_dataframe.to_csv(parent_dir+"_extracted_text.csv")
bar.finish()

print("Processing took "+str(time.time()-start)+"s.")
