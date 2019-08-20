import GSyntax

from copy import deepcopy
from PyQt5 import QtGui, QtCore, QtWidgets

class GCompleter(QtWidgets.QCompleter):
	insertText = QtCore.pyqtSignal(str)
	def __init__(self, alphabet, parent = None):
		QtWidgets.QCompleter.__init__(self, alphabet, parent)
		self.setCompletionMode(self.PopupCompletion)
		self.activated.connect(self.oi)
		self.highlighted.connect(self.setHighlighted)

	def oi(self):
		self.insertText.emit(self.getSelected())
		self.setCompletionMode(self.PopupCompletion)

	def setHighlighted(self, text):
	    self.lastSelected = text

	def getSelected(self):
	    return self.lastSelected


class GTextEdit(QtWidgets.QTextEdit):
	def __init__(self, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
		self.completer = GCompleter(GSyntax.getAlphabet())
		self.completer.setWidget(self)
		self.completer.insertText.connect(self.insertCompletion)
	
	def insertCompletion(self, completion):
		tc = self.textCursor()
		extra = (len(completion) - len(self.completer.completionPrefix()))
		tc.movePosition(QtGui.QTextCursor.StartOfWord, tc.MoveAnchor)
		tc.movePosition(QtGui.QTextCursor.EndOfWord, tc.KeepAnchor)
		tc.insertText(completion)
		self.setTextCursor(tc)
		self.completer.popup().hide()
		
	def keyPressEvent(self, event):
		tc = self.textCursor()
		ek = event.key()

		if (ek == QtCore.Qt.Key_Tab or ek == QtCore.Qt.Key_Return) and self.completer.popup().isVisible():
			self.completer.insertText.emit(self.completer.getSelected())
			self.completer.setCompletionMode(self.completer.PopupCompletion)
			return

		QtWidgets.QTextEdit.keyPressEvent(self, event)
		tc.select(QtGui.QTextCursor.WordUnderCursor)
		cr = self.cursorRect()

		if ek == QtCore.Qt.Key_Space:
			self.completer.popup().hide()
			return

		if len(tc.selectedText()) > 0:
			print(tc.selectedText())
			self.completer.setCompletionPrefix(tc.selectedText())
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0)+self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
		else:
			self.completer.popup().hide()
			
	def wordSubFunction(self, target, cursor):
		cursor.insertText(target.text())
		self.setTextCursor(cursor)

	def getClickedWord(self):
		cursor = self.textCursor()
		cursor.select(cursor.WordUnderCursor)	
		return cursor.selection().toPlainText(), cursor

	def getDisambiguationList(self, word):
		return [word, word+"YES", "NO"]
	
	def mouseReleaseEvent(self, event):
		super().mouseReleaseEvent(event)
		
		tc = self.textCursor()

		if tc.hasSelection():
			return

		tc.select(QtGui.QTextCursor.WordUnderCursor)
		cr = self.cursorRect()
		
		if len(tc.selectedText()) > 0:
			print(tc.selectedText())
			self.completer.setCompletionPrefix(tc.selectedText())
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0)+self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			popup.show()
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
			
			
		"""menu = QtWidgets.QMenu()
		word, cursor = self.getClickedWord()
		if word != "":
			menu.addAction(word)
			menu.addSeparator()
			for signal in self.getDisambiguationList(word):
				print(signal)
				menu.addAction(signal)
			
			menu.triggered[QtWidgets.QAction].connect(lambda w: self.wordSubFunction(w, cursor))
			menu.exec(event.globalPos())
		"""

