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

	screenShotModeKeyPressed = QtCore.pyqtSignal()

	def __init__(self, clScheme, parent = None):
		QtWidgets.QTextEdit.__init__(self, parent)
		self.completer = GCompleter(GParser().getAlphabet())
		self.completer.setWidget(self)
		self.completer.insertText.connect(self.insertCompletion)
		self.pressed = {}
		self.onDeadKey = False
		
		self.clScheme = clScheme
		
		self.completionEnd = " "
		
		self.setAttribute(QtCore.Qt.WA_InputMethodEnabled)
	
	def colorScheme(self):
		return self.clScheme
		
	def setColorScheme(self, colorScheme):
		self.clScheme = colorScheme
		
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
	
	# QChar::QParagraphSeparator 	= chr(0x2029)
	# QChar::LineSeparator 		= chr(0x2028)
	def selectToken(self, stopChars = (' ','\t', '\n', '\r', '\n\r', chr(0x2029), chr(0x2028)), leftSeparators = ('<', '['), rightSeparators = ('=', '>', ']') ):
		cursor = self.textCursor()
		start = cursor.position()
		
		discardStopChars  = stopChars + leftSeparators
		maintainStopChars = rightSeparators
		while cursor.movePosition(cursor.Right, cursor.KeepAnchor):
			if cursor.selectedText().endswith(discardStopChars):
				cursor.movePosition(cursor.Left, cursor.KeepAnchor)
				break
			if cursor.selectedText().endswith(maintainStopChars):
				break
		print("Peguei 1: " + cursor.selectedText() + "|")		
		
		cursor.setPosition(cursor.position(), cursor.MoveAnchor)
		cursor.setPosition(start, cursor.KeepAnchor)
		
		
		discardStopChars  = stopChars + rightSeparators
		maintainStopChars = leftSeparators
		if cursor.selectedText() != "" and cursor.selectedText().startswith(discardStopChars):
			cursor.movePosition(cursor.Right, cursor.KeepAnchor)
		
		if cursor.selectedText() != "" and cursor.selectedText().startswith(maintainStopChars):
			return cursor
		
		while cursor.movePosition(cursor.Left, cursor.KeepAnchor):
			print("char:", ord(cursor.selectedText()[0]), "oi")
			if cursor.selectedText().startswith(discardStopChars):
				cursor.movePosition(cursor.Right, cursor.KeepAnchor)
				break
			if cursor.selectedText().startswith(maintainStopChars):
				break
				
		print("Peguei 2: " + cursor.selectedText() + "|")
		return cursor
	
	#########################################
	#
	# Controle fino do input
	#
	# Mexer aqui para tratar teclas mortas
	# ( `, ´, ~, ^ )
	#
	#########################################
	def inputMethodEvent(self, event):
		commitString  = event.commitString()
		preeditString = event.preeditString()

		print("UIA")
		print("COMMIT: |" + commitString + "|")
		print("PREDIT: |" + preeditString + "|")
		
		# Se for uma tecla morta que não invoca o keyPressEvent
		# cria o evento na mão já com o caractere em maiúsculo
		if commitString.upper() in GParser().getAccentedCharacters():
			newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Any, QtCore.Qt.NoModifier, commitString.upper())
			self.keyPressEvent(newEvent)
		else:
			super().inputMethodEvent(event)
	
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
		
		if ek == QtCore.Qt.Key_Control:
			self.screenShotModeKeyPressed.emit()
		
		if (ek == QtCore.Qt.Key_Tab or ek == QtCore.Qt.Key_Return) and self.completer.popup().isVisible():
			self.completer.insertText.emit(self.completer.getSelected())
			self.completer.setCompletionMode(self.completer.PopupCompletion)
			return
		
		moveWordFlag = False
		srcCursor = self.selectToken()
		if self.isPressed(QtCore.Qt.Key_Control) and ek in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
			moveWordFlag = True
		
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
		
		# Cópia do evento, mas com o texto em maiúsculo
		newEventText = event.text()
		if not srcCursor.selectedText().startswith('<'):
			newEventText = newEventText.upper()
		newEvent = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, event.key(), event.modifiers(), event.nativeScanCode(), event.nativeVirtualKey(), event.nativeModifiers(), newEventText, event.isAutoRepeat(), event.count())
		
		if not moveWordFlag:
			QtWidgets.QTextEdit.keyPressEvent(self, newEvent)
			
		txt = newEvent.text()
		
		# Aparece o completer ao digitar uma letra, símbolo de tag ou comando, ou Ctrl+Espaço
		if txt.isalpha() or txt.isdigit() or txt in ('_', '<') or (self.isPressed(QtCore.Qt.Key_Control) and ek == QtCore.Qt.Key_Space):
			self.completerHandler()
		else:
			self.completer.popup().hide()	


	def completerHandler(self):
		tc = self.selectToken()
		cr = self.cursorRect()
		
		word = tc.selectedText()
		if len(word) > 0:
			print("|->"+word)
			self.completer.setCompletionPrefix(word)
			popup = self.completer.popup()
			popup.setCurrentIndex(self.completer.completionModel().index(0,0))
			cr.setWidth(self.completer.popup().sizeHintForColumn(0) | self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			if self.completer.completionCount() == 0:
				self.completer.popup().hide()
		else:
			self.completer.popup().hide()

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
		
		if completion in GParser().keywords():
			tc.insertText(completion)
		else:
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
			
	def wordSwap(self, event, swapword1, swapword2):
		# Limpa o fundo da palavra 1
		self.setTextCursor(swapword1)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		# Limpa o fundo da palavra 2
		self.setTextCursor(swapword2)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		self.setTextCursor(self.cursorForPosition(event.pos()))

		if (swapword1 == swapword2):
			return

		w1 = swapword1.selectedText()
		w2 = swapword2.selectedText()
		self.textCursor().beginEditBlock()
		swapword1.insertText(w2)
		swapword2.insertText(w1)
		self.textCursor().endEditBlock()

	def contextMenuEvent(self, event):
	
		targetColor = self.clScheme.targetSubColor()
	
		# Pega a palavra 1
		swapword1 = self.selectToken()
		# Colore o fundo da palavra 1
		self.setTextCursor(swapword1)
		highlight = self.textCursor().charFormat()
		highlight.setBackground(QtGui.QBrush(targetColor))
		self.textCursor().setCharFormat(highlight)

		# Pega a palavra 2
		self.setTextCursor( self.cursorForPosition(event.pos()) )
		swapword2 = self.selectToken()
		# Colore o fundo da palavra 2
		self.setTextCursor(swapword2)
		highlight = self.textCursor().charFormat()
		highlight.setBackground(QtGui.QBrush(targetColor))
		self.textCursor().setCharFormat(highlight)

		# Remove a seleção da palavra 2
		self.setTextCursor(self.cursorForPosition(event.pos()))

		menu = self.createStandardContextMenu()
		menu.addAction(QtGui.QIcon.fromTheme("view-refresh"), "Trocar Palavras", lambda:self.wordSwap(event, swapword1, swapword2))
		menu.exec(event.globalPos())
		
		# Limpa o fundo da palavra 1
		self.setTextCursor(swapword1)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		# Limpa o fundo da palavra 2
		self.setTextCursor(swapword2)
		highlight = self.textCursor().charFormat()
		highlight.clearBackground()
		self.textCursor().setCharFormat(highlight)

		swapword1 = None
		swapword2 = None
		self.setTextCursor(self.cursorForPosition(event.pos()))


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
