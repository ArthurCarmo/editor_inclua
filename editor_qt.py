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

	def initMenubar(self):
		menubar = self.menuBar()
		file = menubar.addMenu("Arquivos")
		avatar = menubar.addMenu("Avatar")
		edit = menubar.addMenu("Preferências")
		help = menubar.addMenu("Ajuda!")

		fileNovo = QtWidgets.QAction("Novo", self)
		fileNovo.setShortcut("Ctrl+N")
		fileNovo.setStatusTip("Criar nova tradução")
		fileNovo.triggered.connect(self.saveTextFile)

		fileAbrir = QtWidgets.QAction("Abrir documento", self)
		fileAbrir.setShortcut("Ctrl+O")
		fileAbrir.setStatusTip("Abre novo documento")
		fileAbrir.triggered.connect(self.openDocument)

		fileImportar = QtWidgets.QAction("Importar tadução", self)
		fileImportar.setShortcut("Ctrl+I")
		fileImportar.setStatusTip("Importa tradução")
		fileImportar.triggered.connect(self.importTextFile)

		fileSalvar = QtWidgets.QAction("Salvar", self)
		fileSalvar.setShortcut("Ctrl+S")
		fileSalvar.setStatusTip("Salva arquivo da tradução")
		fileSalvar.triggered.connect(self.saveTextFile)

		fileSalvarComo = QtWidgets.QAction("Salvar como...", self)
		fileSalvarComo.setShortcut("Ctrl+Shift+S")
		fileSalvarComo.setStatusTip("Salvar arquivo da tradução como...")
		fileSalvarComo.triggered.connect(self.saveTextFile)

		fileExportar = QtWidgets.QAction("Exportar", self)
		fileExportar.setStatusTip("Exportar tradução para...")
		fileExportar.triggered.connect(self.saveTextFile)	

		fileQuit = QtWidgets.QAction("Sair", self)
		fileQuit.setShortcut("Ctrl+Q")
		fileQuit.setStatusTip("Sair da aplicação")
		fileQuit.triggered.connect(self.saveTextFile)	

		file.addAction(fileNovo)
		file.addSeparator()
		file.addAction(fileAbrir)
		file.addAction(fileImportar)
		file.addSeparator()
		file.addAction(fileSalvar)
		file.addAction(fileSalvarComo)
		file.addAction(fileExportar)
		file.addSeparator()
		file.addAction(fileQuit)


		avatarEnviar = QtWidgets.QAction("Enviar texto", self)
		avatarEnviar.setShortcut("Ctrl+Shift+Return")
		avatarEnviar.setStatusTip("Envia o texto selecionado para o avatar sinalizar")
		avatarEnviar.triggered.connect(self.sendText)

		avatarConectar = QtWidgets.QAction("Conectar", self)
		avatarConectar.setStatusTip("Conecta com o servidor do avatar")
		avatarConectar.triggered.connect(GServer.startCommunication)
		
		avatarMostrar = QtWidgets.QAction("Mostrar avatar", self)
		avatarMostrar.setShortcut("Ctrl+Shift+T")
		avatarMostrar.setStatusTip("Habilita/Desabilita tela do avatar")
		avatarMostrar.triggered.connect(self.toggleAvatarVisible)

		avatar.addAction(avatarEnviar)
		avatar.addSeparator()
		avatar.addAction(avatarConectar)
		avatar.addAction(avatarMostrar)

		#btn_nxt.setText("Próxima linha")

	def initUI(self):
		# Dimensões iniciais da janela
		self.screen_rect = QtWidgets.QDesktopWidget().screenGeometry()
		self.setGeometry(self.screen_rect)
		self.setWindowTitle("Inclua")
		
		# Componentes principais do editor
		self.splitter	= QtWidgets.QSplitter(self)
		self.text	= GTextEdit()
		
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
				
		# Widget que aparece na janela é um splitter
		# os outros são adicionados a ele
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		self.splitter.addWidget(self.filler)
		self.splitter.addWidget(self.pdf_widget)
		
		# Init
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
		if not fname.endswith(".egl"):
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
