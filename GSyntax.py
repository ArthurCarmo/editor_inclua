import re
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

from GSettings import GDefaultValues

class GParser():
	instance = None

	class __parser():
		def __init__(self):
			
			self.known_words = None
			
			self.retrieveKnownWords()
			self.retrieveAliases()

			self.tags = ["<", ">", "[", "]"]
			self.incomplete_keywords = ["<i", "<im", "<img", "<\\i", "<\\im", "<\\img"]
			self.keywords = ["<img0=", "<img1=", "<img2=", "<img3=", "<\\img0>", "<\\img1>", "<\\img2>", "<\\img3>"]
			self.commands = ["__save", "__stop", "__rec", "__last"]
			self.accentedCharacters = ['Á', 'À', 'Â', 'Ã',\
						   'É', 'È', 'Ê', 'Ẽ',\
						   'Í', 'Ì', 'Î', 'Ĩ',\
						   'Ó', 'Ò', 'Ô', 'Õ',\
						   'Ú', 'Ù', 'Û', 'Ũ',\
						   'Ń', 'Ǹ', 'Ñ', 'Ṕ']
						   
		def retrieveKnownWords(self):
			self.known_words = ahocorasick.Automaton()
			f = open("palavras")
			for w in f.read().splitlines():
				self.known_words.add_word(w, len(w))
			f.close()
			self.known_words.make_automaton()
			
		def retrieveAliases(self):
			return

	def __init__(self):
		if GParser.instance is None:
			GParser.instance = GParser.__parser()
	
	def known_words(self):
		return GParser.instance.known_words

	def tags(self):
		return GParser.instance.tags

	def incomplete_keywords(self):
		return GParser.instance.incomplete_keywords

	def known_words(self):
		return GParser.instance.known_words

	def keywords(self):
		return GParser.instance.keywords

	def commands(self):
		return GParser.instance.commands

	def getAccentedCharacters(self):
		return GParser.instance.accentedCharacters
	
	def getAlphabet(self):
		f = open("palavras")
		l = []
		for w in f:
			l.append(w[0:-1])
	
		for w in GParser.instance.keywords:
			l.append(w)
		
		for w in GParser.instance.commands:
			l.append(w)
		
		return l

	def cleanText(self, text):
		text = re.sub(r'[\n,\'; ]+', ' ', text)
		return text
	
	def getCommandBlocks(self, text):
		patterns = "("
		i = 0
		for cmd in GParser.instance.commands:
			if i == 0:
				patterns += cmd
				i = 1
			else:
				patterns += "|" + cmd
	
		patterns += ")"
		blocks = re.split(patterns, text)
		return list(filter(lambda a: a != "" and a != " ", blocks))

class GSyntaxHighlighter(QtGui.QSyntaxHighlighter):
	def __init__(self, parent):
		self.parent = parent
		QtGui.QSyntaxHighlighter.__init__(self, parent)

	def highlightBlock(self, text):
		cl_known	= QtGui.QColor(0x000000)
		cl_unknown	= QtGui.QColor(0xFF0000)
		cl_tag		= QtGui.QColor(0x000088)
		cl_cmd	  	= QtGui.QColor(0x2200FF)
		cl_wkblue   	= QtGui.QColor(0x000077)

		known		= QtGui.QTextCharFormat()
		unknown	 	= QtGui.QTextCharFormat()
		tag		= QtGui.QTextCharFormat()
		cmd		= QtGui.QTextCharFormat()
		hitting		= QtGui.QTextCharFormat()

		known.setForeground(cl_known)
		unknown.setForeground(cl_unknown)
		tag.setForeground(cl_tag)
		cmd.setForeground(cl_cmd)
		hitting.setForeground(cl_wkblue)
		
		cmd.setFontWeight(QtGui.QFont.Bold)

		word  = QtCore.QRegularExpression(r"[^<>\[\]=\(\).,;\s\n]+")
		tags  = QtCore.QRegularExpression(r"[<>\[\]]")
		links = QtCore.QRegularExpression(r"=.+?>")
		keywords = QtCore.QRegularExpression(r"(<[a-z0-9]+(=)?)|(<\\([a-z0-9]+)?)")

		i = word.globalMatch(text)
		while i.hasNext():
			match = i.next()
			end = match.capturedStart() + match.capturedLength()
			w = text[match.capturedStart():end]
			if w.isnumeric():
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in GParser().known_words():
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in GParser().commands():
				self.setFormat(match.capturedStart(), match.capturedLength(), cmd)
			elif w in GParser().keywords():
				self.setFormat(match.capturedStart(), match.capturedLength(), tag)
			elif w in GParser().incomplete_keywords():
				self.setFormat(match.capturedStart(), match.capturedLength(), hitting)
			else:
				self.setFormat(match.capturedStart(), match.capturedLength(), unknown)
		
		i = tags.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart(), match.capturedLength(), tag)
		
		
		i = keywords.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart(), match.capturedLength(), tag)
		
		i = links.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart()+1, match.capturedLength()-2, cmd)
