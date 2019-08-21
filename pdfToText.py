import sys
import os
import subprocess
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.image import ImageWriter
from io import StringIO
from io import BytesIO
import unidecode

def PDFToTxt(path):
    ext = ""
    name = ""

    if(path[-4] == "."):
        ext = path[-3:]
        name = path[0:-4]
    else:
        ext = path[-4:]
        name = path[0:-5]
    if(ext != "pdf"):
        cmd = "unoconv -f pdf " + path
        resp = subprocess.call(cmd, shell=True)

    os.system("rm media/images/*")

    path = name + ".pdf"

    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    imagewriter = ImageWriter('media/images/') 

    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams, imagewriter=imagewriter)

    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue().decode("utf8", "ignore")
    retstr.close()
    
    refino = ""
    output = str.encode("utf-8")
    base = output.splitlines()
    encontrou = False
    for x in base:
    	if any(char != " " for char in x):
    		encontrou = False
    		if(x[-1] != " "):
    			x = x + " "
    		refino = refino + x
    		if(refino[-2] == "." or refino[-2] == "!"):
    	    		refino = refino + "\n"
    	elif not(encontrou):
    		encontrou = True
    		if(refino[-3:] != "\n"):
    			refino = refino + "\n"

    tempTxt = open("teste.txt", "w")
    tempTxt.write(refino)
    tempTxt.close()

PDFToTxt("fisica.odt")
