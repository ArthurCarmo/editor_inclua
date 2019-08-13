import re
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt


known_words= ahocorasick.Automaton()
f = open("palavras")
for w in f.read().splitlines():
	known_words.add_word(w, len(w))
f.close()
known_words.make_automaton()

tags = ["<", ">", "[", "]"]
incomplete_keywords = ["i", "im", "img", "\\i", "\\im", "\\img"]
keywords = ["img0", "img1", "img2", "img3", "\\img0", "\\img1", "\\img2", "\\img3"]
commands = ["__save", "__stop", "__rec", "__last"]		

def cleanText(text):
	text = re.sub(r'[\n,\';]+', ' ', text)
	return text
	
def getCommandBlocks(text):
	patterns = "("
	i = 0
	for cmd in commands:
		if i == 0:
			patterns += cmd
			i = 1
		else:
			patterns += "|" + cmd
	
	patterns += ")"
	blocks = re.split(patterns, text)
	return list(filter(lambda a: a != "", blocks))

class GSyntaxHighlighter(QtGui.QSyntaxHighlighter):
	def __init__(self, parent):
		self.parent = parent
		QtGui.QSyntaxHighlighter.__init__(self, parent)

	def highlightBlock(self, text):
		cl_known	= QtGui.QColor(0x000000)
		cl_unknown	= QtGui.QColor(0xFF0000)
		cl_tag		= QtGui.QColor(0x000088)
		cl_cmd	  = QtGui.QColor(0x2200FF)
		cl_wkblue   = QtGui.QColor(0x000077)

		known	   = QtGui.QTextCharFormat()
		unknown	 = QtGui.QTextCharFormat()
		tag		 = QtGui.QTextCharFormat()
		cmd		 = QtGui.QTextCharFormat()
		hitting	 = QtGui.QTextCharFormat()

		known.setForeground(cl_known)
		unknown.setForeground(cl_unknown)
		tag.setForeground(cl_tag)
		cmd.setForeground(cl_cmd)
		hitting.setForeground(cl_wkblue)
		
		cmd.setFontWeight(QtGui.QFont.Bold)

		word  = QtCore.QRegularExpression("[^<>\\[\\]=\\(\\).,;\\s\\n]+")
		tags  = QtCore.QRegularExpression("[<>\\[\\]]")
		links = QtCore.QRegularExpression("=.+?>")

		i = word.globalMatch(text)
		while i.hasNext():
			match = i.next()
			end = match.capturedStart() + match.capturedLength()
			w = text[match.capturedStart():end]
			if w.isnumeric():
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in known_words:
				self.setFormat(match.capturedStart(), match.capturedLength(), known)
			elif w in commands:
				self.setFormat(match.capturedStart(), match.capturedLength(), cmd)
			elif w in keywords:
				self.setFormat(match.capturedStart(), match.capturedLength(), tag)
			elif w in incomplete_keywords:
				self.setFormat(match.capturedStart(), match.capturedLength(), hitting)
			else:
				self.setFormat(match.capturedStart(), match.capturedLength(), unknown)
		
		i = tags.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart(), match.capturedLength(), tag)
		
		i = links.globalMatch(text)
		while i.hasNext():
			match = i.next()
			self.setFormat(match.capturedStart()+1, match.capturedLength()-2, cmd)
