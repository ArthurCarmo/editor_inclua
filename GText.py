import GSyntax

from copy import deepcopy
from PyQt5 import QtGui, QtCore, QtWidgets

class GTextEdit(QtWidgets.QTextEdit):
	def __init__(self, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
	
	def wordSubFunction(self, target):
		print("Ola->%s" % (target.text()))

	def getClickedWord(self):
		cursor = self.textCursor()
		click  = cursor.position()
		
		cursor.movePosition(cursor.StartOfWord, cursor.MoveAnchor)
		start  = cursor.position()
		
		cursor.movePosition(cursor.EndOfWord, cursor.KeepAnchor)
		end    = cursor.position()
		
		if start <= click and click < end:
			return cursor.selection().toPlainText()
		return ""

	def getDisambiguationList(self, word):
		return [word, word+"YES", "NO"]
	
	def mousePressEvent(self, event):
		super().mousePressEvent(event)
		menu = QtWidgets.QMenu()
		word = self.getClickedWord()
		if word != "":
			menu.addAction(word)
			menu.addSeparator()
			for signal in self.getDisambiguationList(word):
				print(signal)
				menu.addAction(signal)
			
			menu.triggered[QtWidgets.QAction].connect(lambda w: self.wordSubFunction(w))
			menu.exec(event.globalPos())
		

