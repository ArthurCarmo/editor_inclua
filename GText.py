import GSyntax

from copy import deepcopy
from PyQt5 import QtGui, QtCore, QtWidgets

class GTextEdit(QtWidgets.QTextEdit):
	def __init__(self, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
	
	def wordSubFunction(self, target, cursor):
		print("Ola->%s" % (target.text()))
		#cursor.removeSelectedText()
		cursor.insertText(target.text())
		self.setTextCursor(cursor)

	def getClickedWord(self):
		cursor = self.textCursor()
		cursor.select(cursor.WordUnderCursor)	
		return cursor.selection().toPlainText(), cursor

	def getDisambiguationList(self, word):
		return [word, word+"YES", "NO"]
	
	def mousePressEvent(self, event):
		super().mousePressEvent(event)
		menu = QtWidgets.QMenu()
		word, cursor = self.getClickedWord()
		if word != "":
			menu.addAction(word)
			menu.addSeparator()
			for signal in self.getDisambiguationList(word):
				print(signal)
				menu.addAction(signal)
			
			menu.triggered[QtWidgets.QAction].connect(lambda w: self.wordSubFunction(w, cursor))
			menu.exec(event.globalPos())
		

