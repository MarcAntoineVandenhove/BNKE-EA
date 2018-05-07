#This program scans for PDF within children directories and extracts text off their first pages into a .csv file

import sys
import os
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import pandas as pd

import time

from progress.bar import IncrementalBar

start=time.time()

parentdir =sys.argv[1]

totalLength=0
for subdir in os.listdir(parentdir):
	if os.path.isdir(parentdir+'/'+subdir):
		totalLength+=len(os.listdir(parentdir+'/'+subdir))
bar = IncrementalBar('Processing PDFs', max =totalLength)

columns=["filename","category","firstpagetext","wordscount"]
myDataFrame=pd.DataFrame(index=[],columns=columns)
count=0
jump=1
for subdir in os.listdir(parentdir):
	if os.path.isdir(parentdir+'/'+subdir):
		for myFile in os.listdir(parentdir+'/'+subdir):
			fileExtension = os.path.splitext(myFile)[1]
			if fileExtension == '.pdf':
				if count>149:
					myDataFrame.to_csv(parentdir+"ExtractedText_%s.csv"%(jump))
					myDataFrame.drop(myDataFrame.index[len(myDataFrame)-1])
					jump+=1
					count=0
				rsrcmgr = PDFResourceManager()
				retstr = io.StringIO()
				laparams = LAParams()
				device = TextConverter(rsrcmgr, retstr, laparams=laparams)
				fp = open(parentdir+'/'+subdir+'/'+myFile,'rb')
				interpreter = PDFPageInterpreter(rsrcmgr,device)
				for page in PDFPage.get_pages(fp,caching=False):
    					interpreter.process_page(page)
    					break
				text = retstr.getvalue()
				fp.close()
				device.close()
				retstr.close()
				wordscount=len(text.split())
				myDataFrame.loc[len(myDataFrame)]=[myFile,subdir,text,wordscount]
				bar.next()
				count+=1
myDataFrame.to_csv(parentdir+"ExtractedText_Last.csv")
bar.finish()

print("Processing took "+str(time.time()-start)+"s.")
