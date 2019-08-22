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

from GTranslatorInterface import GTranslator

############################################
# Classe para converter documentos para PDF
# extrair os textos e providenciar o widget
# que vai exibir o PDF
############################################
class GDocument(QtWebEngineWidgets.QWebEngineView):
	def __init__(self, parent = None):
		QtWebEngineWidgets.QWebEngineView.__init__(self, parent)
		self.file = None;
		self.rawText = None
		self.formattedText = None
		self.__pdfjs = 'file:///home/arthur/editor_inclua/pdfjs/web/viewer.html'
	
	def isPDF(self):
		if self.file is None:
			return False
		return self.file.endswith(".pdf")

	def convertToPDF(self):
		if self.file is None:
			raise Exception("Nenhum arquivo especificado")
		name = self.file.rsplit(".", 1)[0]
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

	#####################################
	##
	## Códigos do arquivo newConvert.py
	##
	#####################################
	
	# Extrair o texto do PDF
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

	# Refino
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

#############################################
# Classe para lidar com os arquivos de glosa
# E gerenciar o texto traduzido
#############################################
class GTranslation():
	def __init__(self, text = None, raw = True):
		self.text = text
		if self.text is None:
			self.paragraphs = None
			self.parseIndex = 0
			return
		if raw:
			self.text = self.translate(self.text)
		self.paragraphs = self.text.split(GTranslator.endl)
		self.parseIndex = 0
	
	def __getitem__(self, key):
		return self.paragraphs[key]
	
	def __len__(self):
		return len(self.paragraphs)
	
	def load(self, document):
		with open(document, "r") as doc:
			self.parseIndex = int(doc.readline())
			self.text = doc.read()
			print(self.text)
			self.paragraphs = self.text.split(GTranslator.endl)
		
	def save(self, document):
		with open(document, "w") as doc:
			doc.write(str(self.parseIndex) + "\n")
			for line in self.paragraphs:
				doc.write(line)
				doc.write(GTranslator.endl)
	
	def setText(self, text, raw = True, endl = GTranslator.endl):
		if raw:
			text = self.translate(text)
		self.text = text
		self.paragraphs = self.text.split(endl)
		self.parseIndex = len(self.paragraphs)
	
	def translate(self, text):
		return GTranslator().translate(text)
	
	def getRawText(self):
		return self.text
	
	def next(self):
		if self.parseIndex is None or self.parseIndex >= len(self.paragraphs)-1:
			return ""
		self.parseIndex += 1
		return self.paragraphs[self.parseIndex-1]
		
	def prev(self):
		if self.parseIndex is None or self.parseIndex <= 0:
			return ""
		self.parseIndex -= 1
		return self.paragraphs[self.parseIndex]
	
	def paragraphsToDisplay(self):
		return self.paragraphs[0:self.parseIndex]
	
	def resetIndex(self, index):
		self.parseIndex = 0
		
