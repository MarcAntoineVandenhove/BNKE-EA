#This program runs a classifier over a PDF and returns its category between
# ['SingleStock', 'Industry', 'Economy'] with 81.%-97.5% accuracy depending on
#the prediction.

import sys
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from sklearn.externals import joblib

def main():
    #First: extract text from PDF
    path_to_pdf = sys.argv[1]
    infile = open(path_to_pdf,'rb')

    output = io.StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=None)
    interpreter = PDFPageInterpreter(manager, converter)
    parser = PDFParser(infile)
    doc = PDFDocument(parser)
    for page in PDFPage.get_pages(infile,caching=False):
    	interpreter.process_page(page)
    	break
    infile.close()
    converter.close()
    text = [output.getvalue()]
    output.close()

    #Second: classify between Single Stock or not
    model_tfidf_ss = joblib.load('my_2D_tfidf_full_model.pkl')
    text_tfidf_ss_transformed = model_tfidf_ss.transform(text)

    model_clf_ss = joblib.load('my_2D_linear_reg_model.pkl')
    label_clf_ss_predicted = model_clf_ss.predict(text_tfidf_ss_transformed)

    #Third: if SngleStock, return, otherwise classify between Economy and Industry
    if label_clf_ss_predicted == 'SingleStock':
        return label_clf_ss_predicted[0]
    else:
        model_tfidf_2D3D = joblib.load('my_2D3D_tfidf_model.pkl')
        text_tfidf_2D3D_transformed = model_tfidf_2D3D.transform(text)

        model_clf_2D3D = joblib.load('my_2D3D_linear_SVC_model.pkl')
        label_clf_2D3D_predicted = model_clf_2D3D.predict(text_tfidf_2D3D_transformed)

        return label_clf_2D3D_predicted[0]
if __name__ == "__main__":
    print(main())
