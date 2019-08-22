#!/usr/bin/python3

import re
import sys
import GServer
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QDesktopServices

#from pyvirtualdisplay import Display

from GText import GTextEdit
from GSyntax import GSyntaxHighlighter
from GFile import GDocument, GTranslation
#from pdfToText import PDFToTxt

class Main(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.xephyr 		= QProcess(self)
		self.avatar 		= QProcess(self)
		self.window_manager	= QProcess(self)
		#self.display = Display(visible=0, size=(640, 480))
		self.initUI()
	
	def initToolbar(self):
		self.toolbar = self.addToolBar("Options")
		self.addToolBarBreak()

	def initFormatbar(self):
		self.formatBar = self.addToolBar("Format")

	def initMenubar(self):
		menubar = self.menuBar()
		file = menubar.addMenu("File")
		edit = menubar.addMenu("Edit")
		view = menubar.addMenu("View")

	def initUI(self):
		# Dimensões iniciais da janela
		self.screen_rect = QtWidgets.QDesktopWidget().screenGeometry()
		self.setGeometry(self.screen_rect)
		self.setWindowTitle("Inclua")
		
		# Componentes principais do editor
		self.splitter	= QtWidgets.QSplitter(self)
		self.text	= GTextEdit()
		self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)
		
		# Inicia o SyntaxHighlighter
		self.highlighter = GSyntaxHighlighter(self.text.document())
		self.translation = GTranslation()
		
		# Visualizador de pdf pode ser uma página web dentro de um webView
		self.pdf_widget = GDocument()
		self.pdf_widget.hide()
		
		# Widget para permitir redimensionamento vertical do editor
		# de texto (sem ele o splitter fica no tamanho exato da janela Xephyr)
		self.filler	= QtWidgets.QSplitter(Qt.Vertical)
		
		# Setup do widget com o display virtual
		self.server_widget = GServer.getServerWidget(self.xephyr, "GXEPHYRSV")
		self.server_widget.setMinimumSize(QtCore.QSize(640, 480))
		self.server_widget.setMaximumSize(QtCore.QSize(640, 480))
		
		self.filler.addWidget(self.server_widget)
		self.filler.addWidget(QtWidgets.QGraphicsView())
		
		# Setup dos botões
		btn_open	= QtWidgets.QPushButton()
		btn_text 	= QtWidgets.QPushButton()
		btn_conn 	= QtWidgets.QPushButton()
		btn_show_cursor	= QtWidgets.QPushButton()
		btn_import	= QtWidgets.QPushButton()
		btn_save	= QtWidgets.QPushButton()
		btn_hide	= QtWidgets.QPushButton()
		btn_nxt		= QtWidgets.QPushButton()
		
		btn_open.setText("Abrir Visualizador")
		btn_text.setText("Enviar Texto")
		btn_conn.setText("Conectar")
		btn_show_cursor.setText("Posições do cursor")
		btn_import.setText("Importar tradução")
		btn_save.setText("Salvar tradução")
		btn_hide.setText("Toggle avatar")
		btn_nxt.setText("Próxima linha")
		
		btn_open.clicked.connect(self.openDocument)
		btn_text.clicked.connect(self.sendText)
		btn_conn.clicked.connect(GServer.startCommunication)
		btn_show_cursor.clicked.connect(self.print_cursor)
		btn_import.clicked.connect(self.importTextFile)
		btn_save.clicked.connect(self.saveTextFile)
		btn_hide.clicked.connect(self.toggleAvatarVisible)
		btn_nxt.clicked.connect(self.addNextParagraph)
		
		self.btn_box.addWidget(btn_open)
		self.btn_box.addWidget(btn_text)
		self.btn_box.addWidget(btn_conn)
		self.btn_box.addWidget(btn_show_cursor)
		self.btn_box.addWidget(btn_import)
		self.btn_box.addWidget(btn_save)
		self.btn_box.addWidget(btn_hide)
		self.btn_box.addWidget(btn_nxt)
		
		# Isso pode estar errado, coloca o layout
		# do btn_box no widget do editor de texto
		self.text.setLayout(self.btn_box)
		
		# Widget que aparece na janela é um splitter
		# os outros são adicionados a ele
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		self.splitter.addWidget(self.filler)
		self.splitter.addWidget(self.pdf_widget)
		
		# Init
		self.initToolbar()
		self.initFormatbar()
		self.initMenubar()

		self.statusbar = self.statusBar()
		
		# Força o widget a atualizar
		self.toggleVisible(self.server_widget)

	def print_cursor(self):
		cursor = self.text.textCursor()
		print("position:%2d\nachor:%5d\n" % (cursor.position(), cursor.anchor()))

	def sendText(self):
		cursor = self.text.textCursor()
		if cursor.hasSelection():
			text = cursor.selection().toPlainText()
			GServer.send(text)
		else:
			text = self.text.toPlainText()
		print(text)
		
	def openDocument(self):
		filename = QtWidgets.QFileDialog().getOpenFileName()
		self.pdf_widget.load(filename[0])
		
#		print(self.pdf_widget.getRawText())
		self.translation = GTranslation(self.pdf_widget.getFormattedText())
		
		# Força o widget a atualizar
		self.pdf_widget.hide()
		self.pdf_widget.show()
		self.pdf_widget.setGeometry(0, 0, self.screen_rect.width() / 3, self.screen_rect.height())
	
	def toggleAvatarVisible(self):
		self.toggleVisible(self.server_widget)
		self.toggleVisible(self.filler)
	
	def toggleVisible(self, widget):
		if widget.isVisible():
			widget.hide()
		else:
			widget.show()
	
	def importTextFile(self):
		filename = QtWidgets.QFileDialog().getOpenFileName()
		if filename[0] == "":
			return
		self.text.clear()
		self.translation.load(filename[0])
		for line in self.translation.paragraphsToDisplay():
			print(line)
			self.text.textCursor().insertText(line + "\n")

	def saveTextFile(self):
		filename = QtWidgets.QFileDialog().getSaveFileName()
		self.translation.setText(self.text.toPlainText(), endl = "\n", raw = False)
		fname = filename[0]
		if not fname.endswith(".egl")
			fname += ".egl"
		self.translation.save(fname)

	def addNextParagraph(self):
		if self.translation is None:
			return
		cursor = self.text.textCursor()
		cursor.movePosition(cursor.End, cursor.MoveAnchor)
		text = self.translation.next()
		if text != "\n" and text != "":
			text += "\n"
		cursor.insertText(text)

	def __del__(self):
		print("Destrutor")
		self.avatar.kill()
		self.xephyr.kill()
		exit()

def main():
	global app
	app = QtWidgets.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
