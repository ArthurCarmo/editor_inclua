import GSyntax

from copy import deepcopy
from PyQt5 import QtGui, QtCore, QtWidgets

#######################################
#
# Completer
#
#######################################
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

#######################################
#
# Editor de texto
#
#######################################
class GTextEdit(QtWidgets.QTextEdit):
	def __init__(self, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
		self.completer = GCompleter(GSyntax.getAlphabet())
		self.completer.setWidget(self)
		self.completer.insertText.connect(self.insertCompletion)
		self.pressed = {}
		
		self.textChanged.connect(self.onTextChanged)
		# self.setAttribute(QtCore.Qt.WA_KeyCompression)
	
	#####################################
	#
	# Eventos do teclado
	#
	#####################################
	def isPressed(self, key):
		if key in self.pressed:
			return self.pressed[key]
		return False
			
	def keyReleaseEvent(self, event):
		ek = event.key()
		self.pressed[ek] = False
		QtWidgets.QTextEdit.keyReleaseEvent(self, event)
	
	####################################
	#
	# keyPressEvent
	#
	####################################
	def keyPressEvent(self, event):
		print("KEY")
		ek = event.key()
		self.pressed[ek] = True
		
		if (ek == QtCore.Qt.Key_Tab or ek == QtCore.Qt.Key_Return) and self.completer.popup().isVisible():
			self.completer.insertText.emit(self.completer.getSelected())
			self.completer.setCompletionMode(self.completer.PopupCompletion)
			return
		
#		newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, event.key(), event.modifiers(), event.nativeScanCode(), event.nativeVirtualKey(), event.nativeModifiers(), event.text().upper(), event.isAutoRepeat(), event.count())
#		QtWidgets.QTextEdit.keyPressEvent(self, newEvent)
		QtWidgets.QTextEdit.keyPressEvent(self, event)
		
		# Só mostra sugestão em caso de adicionar uma letra Ctrl+Espaço
		if self.popupShowConditions(event.text(), ek) and self.completer.completionCount() != 0:
			self.completer.popup().show()
			return
	
	###########################################
	#
	# Ações do completer
	#
	###########################################
	def insertCompletion(self, completion):
		tc = self.textCursor()
		lc = self.textCursor()
		
		
		tc.movePosition(QtGui.QTextCursor.EndOfWord, tc.MoveAnchor)
		tc.movePosition(QtGui.QTextCursor.StartOfWord, tc.KeepAnchor)
		
		lc.movePosition(QtGui.QTextCursor.StartOfWord, lc.MoveAnchor)
		lc.movePosition(QtGui.QTextCursor.Left, lc.KeepAnchor)
		lc = lc.selectedText()
		if lc == '<':
			tc.movePosition(QtGui.QTextCursor.Left, tc.KeepAnchor)
			
		tc.insertText(completion)
		self.setTextCursor(tc)
		self.completer.popup().hide()
	
	# Atalho de teclado para o completer
	def popupShowConditions(self, text, key):
		return text == '_' or text == '<' or (key == QtCore.Qt.Key_Space and self.isPressed(QtCore.Qt.Key_Control))
		
	def wordSubFunction(self, target, cursor):
		cursor.insertText(target.text())
		self.setTextCursor(cursor)

	def getDisambiguationList(self, word):
		return [word, word+"YES", "NO"]
		
	##########################################
	#
	# Ações do mouse
	#
	##########################################
	def getClickedWord(self):
		cursor = self.textCursor()
		cursor.select(cursor.WordUnderCursor)	
		return cursor.selection().toPlainText(), cursor

	
	def mouseReleaseEvent(self, event):
		super().mouseReleaseEvent(event)
		
		tc = self.textCursor()

		if tc.atEnd() or tc.hasSelection():
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
	#########################################
	#
	# Teste textChanged
	#
	#########################################
	def onTextChanged(self):
		print("Oloco")
		tc = self.textCursor()
		lc = self.textCursor()
		lc.movePosition(lc.Left, lc.KeepAnchor)
		ek = lc.selectedText()
		self.textChanged.disconnect()
		if not ek.isupper():
			lc.insertText(ek.upper())
		self.textChanged.connect(self.onTextChanged)
		if not ek.isalpha():
			self.completer.popup().hide()
			return

		tc.select(QtGui.QTextCursor.WordUnderCursor)
		lc.select(QtGui.QTextCursor.WordUnderCursor)
		cr = self.cursorRect()

		word = tc.selectedText()
		
		if ek == '_' or ek == '<':
			word = ek
		
		lc.movePosition(lc.StartOfWord, lc.MoveAnchor)
		lc.movePosition(lc.Left, lc.KeepAnchor)
		lc = lc.selectedText()
		
		if lc == '<' and not word.startswith('<'):
			word = '<' + word
			
		print("lc: " + lc)
		print("word:" + word)
		if len(word) > 0:
			print("|->"+word)
			self.completer.setCompletionPrefix(word)
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0)+self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
		else:
			self.completer.popup().hide()
