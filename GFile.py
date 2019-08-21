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

from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5.QtCore import QUrl

class GDocument(QtWebEngineWidgets.QWebEngineView):
	def __init__(self, parent = None):
		QtWebEngineWidgets.QWebEngineView.__init__(self, parent)
		self.file = None;
		self.rawText = None
		self.formattedText = None
		self.__pdfjs = 'file:///home/arthur/editor_inclua/pdfjs/web/viewer.html'
		
	def getRawText(self):
		if self.rawText is not None:
			return self.rawText
		rsrcmgr = PDFResourceManager()
		retstr = BytesIO()
		codec = 'utf-8'
		laparams = LAParams()
		imagewriter = ImageWriter('media/images/') 
		device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams, imagewriter=imagewriter)
		fp = open(self.file, 'rb')
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		password = ""
		maxpages = 0
		caching = True
		pagenos=set()
		for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
			interpreter.process_page(page)
		fp.close()
		device.close()
		s = retstr.getvalue().decode("utf8", "ignore")
		retstr.close()
		self.rawText = s;
		return self.rawText

	def isPDF(self):
		if self.file is None:
			return False
		return self.file.endswith(".pdf")

	def convertToPDF(self):
		if self.file is None:
			raise Exception("Nenhum arquivo especificado")
		name = self.file.rsplit(".", 1)
		cmd = "unoconv -f pdf " + self.file
		resp = subprocess.call(cmd, shell=True)
		self.file = name + ".pdf"

	def load(self, f, url = "file://"):
		self.file = f
		self.rawText = None
		self.formattedText = None
		if not self.isPDF():
			self.convertToPDF()
		super().load(QtCore.QUrl.fromUserInput(self.__pdfjs + "?file="+url+self.file))

	def getFormattedText(self):
		if self.formattedText is not None:
			return self.formattedText
			
		os.system("rm media/images/*")
		output = self.getRawText()
		refino = ""
		output2 = output.encode("utf-8")
		base = output2.splitlines()
		encontrou = False
		for x in base:
			if any(char != " " for char in x):
				encontrou = False
				if(x[-1] != " "):
					x = x + b" "
				refino = refino + x.decode("utf-8")
				if(refino[-2] == "." or refino[-2] == "!"):
						refino = refino + "\n"
			elif not(encontrou):
				encontrou = True
				if(refino[-3:] != "\n"):
					refino = refino + "\n"
		self.formattedText = refino
		return self.formattedText

