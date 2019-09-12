from GSyntax import GParser

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
		self.completer = GCompleter(GParser().getAlphabet())
		self.completer.setWidget(self)
		self.completer.insertText.connect(self.insertCompletion)
		self.pressed = {}
		self.onDeadKey = False
		
		self.completionEnd = " "
		
		self.textChanged.connect(self.onTextChanged)
		# self.setAttribute(QtCore.Qt.WA_KeyCompression)
		self.setAttribute(QtCore.Qt.WA_InputMethodEnabled)
	
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
	# Funções auxiliares para selecionar
	# tokens com separators padrão
	#
	####################################
	def selectToken(self, stopChars = [' ','\t','\n']):
		cursor = self.textCursor()
		start = cursor.position()
		cursor.movePosition(cursor.EndOfWord, cursor.MoveAnchor)
		while cursor.movePosition(cursor.Right, cursor.KeepAnchor):
			if cursor.selectedText()[-1] in stopChars:
				cursor.movePosition(cursor.Left, cursor.KeepAnchor)
				break
		print("Peguei 1: " + cursor.selectedText() + "|")		
		
		cursor.setPosition(cursor.position(), cursor.MoveAnchor)
		cursor.setPosition(start, cursor.KeepAnchor)
		while cursor.movePosition(cursor.Left, cursor.KeepAnchor):
			if cursor.selectedText()[0] in stopChars:
				cursor.movePosition(cursor.Right, cursor.KeepAnchor)
				break
				
		print("Peguei 2: " + cursor.selectedText() + "|")
		return cursor
	
	####################################
	#
	# keyPressEvent
	#
	####################################
	def keyPressEvent(self, event):
		print("KEY")
		ek = event.key()
		self.pressed[ek] = True

		# Provavelmente só tem o efeito desejado em sistemas
		# cujas teclas mortas não invocam esse evento
		self.onDeadKey = False
		
		if (ek == QtCore.Qt.Key_Tab or ek == QtCore.Qt.Key_Return) and self.completer.popup().isVisible():
			self.completer.insertText.emit(self.completer.getSelected())
			self.completer.setCompletionMode(self.completer.PopupCompletion)
			return
		
		moveWordFlag = False
		if self.isPressed(QtCore.Qt.Key_Control) and ek in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
			moveWordFlag = True
		
			srcCursor = self.selectToken()
			dstCursor = self.selectToken()
			
			if ek == QtCore.Qt.Key_Left:
				direction = dstCursor.Left
				print("LEFT")
				dstCursor.setPosition(dstCursor.selectionStart(), dstCursor.MoveAnchor)
				dstCursor.movePosition(direction, dstCursor.MoveAnchor)
			else:
				direction = dstCursor.Right
				print("RIGHT")
				dstCursor.setPosition(dstCursor.selectionEnd(), dstCursor.MoveAnchor)
				dstCursor.movePosition(direction, dstCursor.MoveAnchor)
			
			
			
			self.setTextCursor(dstCursor)
			dstCursor = self.selectToken()
		
			if srcCursor != dstCursor:
				w1 = srcCursor.selectedText()
				w2 = dstCursor.selectedText()
				self.textCursor().beginEditBlock()
				srcCursor.insertText(w2)
				dstCursor.insertText(w1)
				self.textCursor().endEditBlock()
		
		
		if not moveWordFlag:
			QtWidgets.QTextEdit.keyPressEvent(self, event)
		
#		newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, event.key(), event.modifiers(), event.nativeScanCode(), event.nativeVirtualKey(), event.nativeModifiers(), event.text().upper(), event.isAutoRepeat(), event.count())	
#		QtWidgets.QTextEdit.keyPressEvent(self, newEvent)

		
		if not event.text().isalpha() and not ek == QtCore.Qt.Key_Shift and not event.text() in ('_', '<'):
			self.completer.popup().hide()
			
		# Só mostra sugestão em caso de adicionar uma letra Ctrl+Espaço
		if self.popupShowConditions(event.text(), ek):
			self.onTextChanged()
	
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
			
		tc.insertText(completion + self.completionEnd)
		self.setTextCursor(tc)
		self.completer.popup().hide()
	
	#########################################
	#
	# Atalho de teclado para o completer
	#
	#########################################
	def popupShowConditions(self, text, key):
		return key == QtCore.Qt.Key_Space and self.isPressed(QtCore.Qt.Key_Control)
		
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
		return cursor.selectedText(), cursor

	
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
	# Controle fino do input
	#
	# Mexer aqui para tratar teclas mortas
	# ( `, ´, ~, ^ )
	#
	#########################################
	def inputMethodEvent(self, event):
		print("HI")
		
		commitString  = event.commitString()
		preeditString = event.preeditString()
		
		print("COMMIT: |" + commitString + "|")
		print("PREDIT: |" + preeditString + "|")
		
		# Desse jeito o usuário não pode digitar
		# os caracteres ~, ´, ` e ^ sozinhos, 
		# talvez depois tentar algum fix
		if commitString in ('´', '^', '~', '`'):
			event.setCommitString("")
		
		print("++++++++++++++++++++++++")
		super().inputMethodEvent(event)
	
	#########################################
	#
	# Teste textChanged
	#
	#########################################
	def onTextChanged(self):
		tc = self.textCursor()
		lc = self.textCursor()
		lc.movePosition(lc.Left, lc.KeepAnchor)
		ek = lc.selectedText()

		if self.onDeadKey:
			self.onDeadKey = False
			return

		if not ek.isalpha() and not ek.isdigit() and not ek in ('<', '_'):
			self.completer.popup().hide()
			return
		
		tc.select(QtGui.QTextCursor.WordUnderCursor)

		if ek.isalpha() and not ek.isupper() and not tc.selectedText().startswith('_'):
			self.textChanged.disconnect()
			lc.insertText(ek.upper())
			self.textChanged.connect(self.onTextChanged)


		lc.select(QtGui.QTextCursor.WordUnderCursor)

		word = lc.selectedText()
		
		if ek == '_' or ek == '<':
			word = ek
		
		lc.movePosition(lc.StartOfWord, lc.MoveAnchor)
		lc.movePosition(lc.Left, lc.KeepAnchor)
		lc = lc.selectedText()
		
		if lc == '<' and not word.startswith('<'):
			word = '<' + word
			
		print("lc: " + lc)
		print("word:" + word)

		cr = self.cursorRect()
		
		if len(word) > 0:
			print("|->"+word)
			self.completer.setCompletionPrefix(word)
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0) | self.completer.popup().verticalScrollBar().sizeHint().width())
			# Essa linha causa bug com acentuação
			self.completer.complete(cr)
			#############################
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
		else:
			self.completer.popup().hide()
