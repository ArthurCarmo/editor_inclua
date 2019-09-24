#!/usr/bin/python3

import os
import re
import sys
import threading
import subprocess
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QDesktopServices

from GText import GTextEdit
from GSyntax import GSyntaxHighlighter
from GFile import GDocument, GTranslation, GVideo
from GImage import GImageGrid, GCustomImageDialog

from GScreenUtils import GLayeredDocumentCanvas

from time import sleep
from GServer import GServer

from GSettings import GDefaultValues

class Main(QtWidgets.QMainWindow):
	cwd		= GDefaultValues.cwd
	home		= GDefaultValues.home
	default_pngDir  = GDefaultValues.pngDir
	default_videoId = GDefaultValues.videoId
	default_imgDir  = GDefaultValues.imgDir
	

	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.hasOpenTranslation = False
		self.hasOpenFile = False
		self.isRecording = False
		self.translationFileName = ""
		self.server = GServer()
		self.server.sender.finishedRecording.connect(self.createVideo)
		self.initUI()

	#####################################
	#
	# Menubar
	#
	#####################################
	def initMenubar(self):
		menubar = self.menuBar()
		file = menubar.addMenu("Arquivos")
		avatar = menubar.addMenu("Avatar")
		traducao = menubar.addMenu("Tradução")
		imagens = menubar.addMenu("Imagens")
		edit = menubar.addMenu("Preferências")
		

		fileNovo = QtWidgets.QAction("Novo", self)
		fileNovo.setShortcut("Ctrl+N")
		fileNovo.setStatusTip("Criar nova tradução")
		fileNovo.triggered.connect(self.newTextFile)

		fileAbrir = QtWidgets.QAction("Abrir documento", self)
		fileAbrir.setShortcut("Ctrl+O")
		fileAbrir.setStatusTip("Abre novo documento")
		fileAbrir.triggered.connect(self.openDocument)

		fileImportar = QtWidgets.QAction("Importar tradução", self)
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
		fileSalvarComo.triggered.connect(self.saveTextFileAs)

		fileExportar = QtWidgets.QAction("Exportar", self)
		fileExportar.setStatusTip("Exportar tradução para...")
		fileExportar.triggered.connect(self.exportTextFile)	

		fileQuit = QtWidgets.QAction("Sair", self)
		fileQuit.setShortcut("Ctrl+Q")
		fileQuit.setStatusTip("Sair da aplicação")
		fileQuit.triggered.connect(self.__del__)	

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


		avatarGravar = QtWidgets.QAction("Gravar vídeo", self)
		avatarGravar.setStatusTip("Grava o vídeo para o texto selecionado")
		avatarGravar.triggered.connect(self.recordVideo)

		avatarConectar = QtWidgets.QAction("Conectar", self)
		avatarConectar.setStatusTip("Conecta com o servidor do avatar")
		avatarConectar.triggered.connect(self.server.startCommunication)
		
		avatarMostrar = QtWidgets.QAction("Mostrar avatar", self)
		avatarMostrar.setShortcut("Ctrl+Shift+T")
		avatarMostrar.setStatusTip("Habilita/Desabilita tela do avatar")
		avatarMostrar.triggered.connect(self.toggleAvatarVisible)

		avatar.addAction(avatarEnviar)
		avatar.addAction(avatarGravar)
		avatar.addSeparator()
		avatar.addAction(avatarConectar)
		avatar.addAction(avatarMostrar)

		traducaoShowAll = QtWidgets.QAction("Mostrar tudo", self)
		traducaoShowAll.setStatusTip("Exibir toda a tradução do arquivo")
		traducaoShowAll.triggered.connect(self.showAllTranslation)
		
		traducaoNext	= QtWidgets.QAction("Próxima linha", self)
		traducaoNext.setStatusTip("Próxima linha da tradução do arquivo")
		traducaoNext.triggered.connect(self.addNextTranslationParagraph)
		
		traducaoReset	= QtWidgets.QAction("Resetar tradução", self)
		traducaoReset.setStatusTip("Apaga todo o conteúdo do editor e reinicia a tradução para a primeira linha")
		traducaoReset.triggered.connect(self.resetTranslation)
		
		traducaoCreate	= QtWidgets.QAction("Gerar tradução", self)
		traducaoCreate.setStatusTip("Traduz o arquivo selecionado")
		traducaoCreate.triggered.connect(self.getTranslationFromFile)
		
		traducao.addAction(traducaoNext)
		traducao.addSeparator()
		traducao.addAction(traducaoShowAll)
		traducao.addAction(traducaoReset)
		traducao.addSeparator()
		traducao.addAction(traducaoCreate)

		imagensNewFromFile = QtWidgets.QAction("Adicionar imagem do computador", self)
		imagensNewFromFile.setStatusTip("Adiciona uma imagem do computador à lista de imagens disponíveis para o vídeo")
		imagensNewFromFile.triggered.connect(self.addImagesFromFile)

		imagensNewFromUrl = QtWidgets.QAction("Adicionar imagem da internet", self)
		imagensNewFromUrl.setStatusTip("Adiciona uma imagem da internet à lista de imagens disponíveis para o vídeo")
		imagensNewFromUrl.triggered.connect(self.addImageFromUrl)
		
		self.imagensDelete = QtWidgets.QAction("Remover imagens")
		self.imagensDelete.setStatusTip("Remover imagens da área de seleção")
		self.imagensDelete.triggered.connect(self.setRemoveImagesState)
		
		imagens.addAction(imagensNewFromFile)
		imagens.addAction(imagensNewFromUrl)
		imagens.addSeparator()
		imagens.addAction(self.imagensDelete)
		
		bar = QtWidgets.QMenuBar(menubar)
		menubar.setCornerWidget(bar, QtCore.Qt.TopRightCorner)

		help = bar.addMenu("Ajuda")
		
		sobre = QtWidgets.QAction("Sobre o projeto", self)
		sobre.setStatusTip("Conheça mais sobre o projeto")
		sobre.triggered.connect(lambda: self.showOne(self.sobre_view))
		bar.addAction(sobre)

		#btn_nxt.setText("Próxima linha")


	###########################################
	#
	# Componentes da UI
	#
	# Janela do servidor, editor de texto,
	# visualizador de PDF e das imagens
	#
	###########################################
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
		self.translation.sender.translationReady.connect(self.onTranslationReady)
		
		# Visualizador de pdf pode ser uma página web dentro de um webView
		self.pdf_widget = GDocument()
		self.pdf_widget.sender.formattedReady.connect(self.onPDFTextReady)
		
		self.screenshotLayer = GLayeredDocumentCanvas(self.pdf_widget)
		self.screenshotLayer.screenShot.connect(self.onScreenShot)
		self.screenshotLayer.hide()
		
		# Widget que contém a janela do avatar e o grid com as imagens
		self.filler	= QtWidgets.QSplitter(Qt.Vertical)
		
		# Setup do widget com o display virtual
		self.server_widget = self.server.getServerWidget()
		self.server_widget.setMinimumSize(QtCore.QSize(640, 480))
		self.server_widget.setMaximumSize(QtCore.QSize(640, 480))
		
		# Widget das imagens
		self.images_widget = GImageGrid(self.default_imgDir)
		self.images_widget.onClick.connect(self.onImageClick)

		#Sobre o projeto
		self.sobre_view = QtWidgets.QTextEdit()
		self.sobre_view.setReadOnly(True)
		self.sobre_view.hide()
		self.initSobre()

		#####################################
		#
		# Toolbar para gerenciar imagens
		#
		#####################################
		self.images_toolbar = QtWidgets.QWidget()
		self.images_toolbar.setMaximumHeight(20)
		
		self.it_layout = QtWidgets.QHBoxLayout()
		self.it_layout.setContentsMargins(5, 0, 5, 0)
		
		self.confirmar_selecao = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), "", self)
		self.confirmar_selecao.setStatusTip("Remover as imagens selecionadas")
		self.confirmar_selecao.clicked.connect(self.removeSelected)
		
		self.confirmar_selecao.setFixedSize(QtCore.QSize(150, 20))
		self.confirmar_selecao.hide()

		self.deletar_imagens = QtWidgets.QPushButton(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon), "", self)
		self.deletar_imagens.setStatusTip("Remover imagens da lista")
		self.deletar_imagens.setCheckable(True)
		self.deletar_imagens.toggled.connect(self.changeImageViewerState)
		
		self.it_layout.addWidget(self.confirmar_selecao, alignment = Qt.AlignLeft | Qt.AlignBottom)
		self.it_layout.addWidget(self.deletar_imagens, alignment = Qt.AlignRight | Qt.AlignBottom)
		
		self.images_toolbar.setLayout(self.it_layout)

		self.filler.addWidget(self.server_widget)
		self.filler.addWidget(self.images_toolbar)
		self.filler.addWidget(self.images_widget)
		
		# Widget que aparece na janela é um splitter
		# os outros são adicionados a ele
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		self.splitter.addWidget(self.filler)
		self.splitter.addWidget(self.screenshotLayer)
		self.splitter.addWidget(self.sobre_view)
		
		# Init
		self.initMenubar()

		self.statusbar = self.statusBar()
		
		# Força o widget a atualizar
		self.toggleVisible(self.server_widget)
		threading.Thread(target=self.tryCommunication).start()

	def print_cursor(self):
		cursor = self.text.textCursor()
		print("position:%2d\nachor:%5d\n" % (cursor.position(), cursor.anchor()))

	##################################
	#
	# ARQUIVOS
	#
	##################################	
	
	##################################
	#
	# Documentos
	#
	##################################
	def openDocument(self):
		filename = QtWidgets.QFileDialog().getOpenFileName(caption="Abrir documento", filter="Documentos (*.pdf *.odt *.doc *.docx *.ppt *.pptx *.rtf *.pps *.ppsx *.odp);; Todos os arquivos (*.*)")
		if filename[0] == "":
			return 1
		
		if not self.text.document().isEmpty():
			box = QtWidgets.QMessageBox()
			box.setIcon(QtWidgets.QMessageBox.Question)
			box.setWindowTitle('Abrir documento')
			box.setText("Apagar texto do editor?")
			box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
			buttonY = box.button(QtWidgets.QMessageBox.Yes)
			buttonY.setText('Sim')
			buttonN = box.button(QtWidgets.QMessageBox.No)
			buttonN.setText('Não')
			reply = box.exec_()

#			reply = QtWidgets.QMessageBox.question(self, "Abrir documento", "Apagar texto do editor?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if reply == QtWidgets.QMessageBox.Yes:
				self.text.clear()

		self.pdf_widget.load(filename[0])
		
		# Força o widget a atualizar
		self.screenshotLayer.hide()
		self.screenshotLayer.show()
		self.screenshotLayer.setGeometry(0, 0, self.screen_rect.width() / 10, self.screen_rect.height())
		
		self.hasOpenDocument = True
		
		return 0
	
	def onPDFTextReady(self):
		self.images_widget.loadImages()
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Question)
		box.setWindowTitle('Abrir documento')
		box.setText("Traduzir documento?")
		box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		buttonY = box.button(QtWidgets.QMessageBox.Yes)
		buttonY.setText('Sim')
		buttonN = box.button(QtWidgets.QMessageBox.No)
		buttonN.setText('Não')
		reply = box.exec_()
#		reply = QtWidgets.QMessageBox.question(self, "Abrir documento", "Traduzir documento?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		if reply == QtWidgets.QMessageBox.Yes:
			self.getTranslationFromFile()

	#################################
	#
	# Arquivos de traduçao
	#
	#################################
	def newTextFile(self):
	
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Question)
		box.setWindowTitle('Novo arquivo de glosa')
		box.setText("Salvar alterações?")
		box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
		buttonY = box.button(QtWidgets.QMessageBox.Yes)
		buttonY.setText('Sim')
		buttonN = box.button(QtWidgets.QMessageBox.No)
		buttonN.setText('Não')
		buttonC = box.button(QtWidgets.QMessageBox.Cancel)
		buttonC.setText('Cancelar')
		reply = box.exec_()
#		reply = QtWidgets.QMessageBox.question(self, "Novo arquivo de glosa", "Salvar alterações", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
		if reply == QtWidgets.QMessageBox.Yes:
			self.saveTextFile()
		elif reply == QtWidgets.QMessageBox.Cancel:
			return
			
		self.text.clear()
		self.translationFileName = ""
		self.hasOpenTranslationFile = False	
	
	
	def getTranslationFromFile(self):
		if not self.pdf_widget.hasFile() and self.openDocument() == 1:
			return
			
		if self.hasOpenTranslation:
			box = QtWidgets.QMessageBox()
			box.setIcon(QtWidgets.QMessageBox.Question)
			box.setWindowTitle('Gerar tradução')
			box.setText("Já existe uma tradução aberta. Substituir?")
			box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
			buttonY = box.button(QtWidgets.QMessageBox.Yes)
			buttonY.setText('Sim')
			buttonN = box.button(QtWidgets.QMessageBox.No)
			buttonN.setText('Não')
			reply = box.exec_()
#			reply = QtWidgets.QMessageBox.question(self, "Gerar tradução", "Já existe uma tradução aberta. Substituir?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
			if reply == QtWidgets.QMessageBox.No:
				return 
		
		txt = self.pdf_widget.getFormattedText()
		self.translation.update(txt)

	
	def importTextFile(self):
		filename = QtWidgets.QFileDialog().getOpenFileName(caption="Abrir arquivo de tradução", filter="EGL (*.egl);; TXT (*.txt);; Todos os arquivos (*.*)")
		if filename[0] == "":
			return
		self.text.clear()
		self.translation.load(filename[0])
		self.translationFileName = filename[0]
		for line in self.translation.paragraphsToDisplay():
			print(line)
			self.text.textCursor().insertText(line + "\n")

	def saveTextFile(self):
		if self.translationFileName == "":
			self.saveTextFileAs()
		else:
			self.translation.save(self.translationFileName)
		
	def saveTextFileAs(self):
		filename = QtWidgets.QFileDialog().getSaveFileName(caption="Salvar arquivo de tradução")
		#self.translation.setText(self.text.toPlainText(), endl = "\n", raw = False)
		fname = filename[0]
		if not fname.endswith(".egl") and not fname.endswith(".txt"):
			fname += ".egl"
		self.translationFileName = fname
		self.translation.save(self.translationFileName)
		
	def exportTextFile(self):
		filename = QtWidgets.QFileDialog().getSaveFileName(caption="Exportar arquivo de tradução")
		fname = filename[0]
		with open(fname, "w") as doc:
			doc.write(self.text.toPlainText)

	def addNextTranslationParagraph(self):
		cursor = self.text.textCursor()
		cursor.movePosition(cursor.End, cursor.MoveAnchor)
		
		spaces = ""
		text = self.translation.next()
		
		while text.isspace():
			spaces += text
			text = self.translation.next()
		
		end = "\n"
		if text == "":
			end = ""
		text = spaces + text + end
		cursor.insertText(text)

	def showAllTranslation(self):
		cursor = self.text.textCursor()
		for line in self.translation.getParagraphsTillEnd():
			self.text.textCursor().insertText(line + "\n")	

	def clearTranslation(self):
		self.text.clear()
		self.translation = GTranslation()
		self.hasOpenTranslation = False
		
	def resetTranslation(self):
		self.text.clear()
		self.translation.resetIndex()
		
	def onTranslationReady(self):
			self.hasOpenTranslation = True


	##################################
	#
	# IMAGENS
	#
	##################################

	def addImagesFromFile(self):
		filename = QtWidgets.QFileDialog().getOpenFileNames(caption="Adicionar imagem do computador", filter="Imagens (*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG);; JPG (*.jpg *.JPG *.jpeg *JPEG);; PNG (*.png *.PNG);; Todos os arquivos (*.*)")
		print(filename[0])
		if len(filename[0]) == 0:
			return
		self.images_widget.addImagesFromFile(filename[0])
	
	def addImageFromUrl(self):
		dlg = QtWidgets.QInputDialog(self)
		dlg.setOkButtonText("Enviar")
		dlg.setCancelButtonText("Cancelar")
		dlg.setInputMode(QtWidgets.QInputDialog.TextInput) 
		dlg.setWindowTitle("Adicionar imagem por url")
		dlg.setLabelText("Url da imagem:")
		dlg.resize(500,100)                             
		ok = dlg.exec_()                                
		lineEdit = dlg.textValue()
		print ("LINEEDIT " + lineEdit)
		if lineEdit == '':
			return
		self.images_widget.addImageFromUrl(lineEdit)

	def setRemoveImagesState(self):
		self.confirmar_selecao.show()
		self.deletar_imagens.setChecked(True)
		self.images_widget.setMode(GImageGrid.selectable)

	def setClickableImagesState(self):
		self.confirmar_selecao.hide()
		self.deletar_imagens.setChecked(False)
		self.images_widget.setMode(GImageGrid.clickable)
		
	def changeImageViewerState(self, checked):
		if checked:
			self.setRemoveImagesState()
		else:
			self.setClickableImagesState()
	
	def removeSelected(self):
		box = QtWidgets.QMessageBox()
		box.setIcon(QtWidgets.QMessageBox.Question)
		box.setWindowTitle('Remover imagens')
		box.setText("Remover todas as imagens selecionadas?")
		box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		buttonY = box.button(QtWidgets.QMessageBox.Yes)
		buttonY.setText('Confirmar')
		buttonN = box.button(QtWidgets.QMessageBox.No)
		buttonN.setText('Cancelar')
		reply = box.exec_()
		reply = QtWidgets.QMessageBox.question(self, "Remover imagens", "Remover todas as imagens selecionadas?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		if reply == QtWidgets.QMessageBox.Yes:
			self.images_widget.removeSelected()
			self.setClickableImagesState()
	
	def onImageClick(self, index):
		lc = self.text.textCursor()
		range_content = lc.selectedText()
		pos = GCustomImageDialog().question()
		lc.insertText("<img%d=%s%s> %s <\\img%d>" % (pos, str(index), self.images_widget.getImageButtonFromIndex(index).getExtension(), range_content, pos))
	
	##################################
	#
	# SCREENSHOTS
	#
	##################################
	def keyPressEvent(self, event):
		ek = event.key()
		ev = self.screenshotLayer.getCaptureMode()
		print(ev)
		if ek == QtCore.Qt.Key_Control:
			self.screenshotLayer.setCaptureMode(not ev)
		QtWidgets.QMainWindow.keyPressEvent(self, event)
	
	def onScreenShot(self, pixmap):
		self.targetPixmap = pixmap
		self.images_widget.addImageFromPixmap(self.targetPixmap)
	
	##################################
	#
	# AVATAR
	#
	##################################
	
	def sendText(self):
		cursor = self.text.textCursor()
		if cursor.hasSelection():
			text = cursor.selection().toPlainText()
			self.server.send(text)
		else:
			text = self.text.toPlainText()
		print(text)
		
	def toggleAvatarVisible(self):
		self.toggleVisible(self.server_widget)
		self.toggleVisible(self.filler)
	
	def toggleVisible(self, widget):
		if widget.isVisible():
			widget.hide()
		else:
			widget.show()

	def createVideo(self, vName, vId = default_videoId, pngDir = default_pngDir):
		vid = GVideo()
		vid.sender.videoReady.connect(self.onVideoReady)
		vid.createVideo(vId, vName, pngDir)
		
	def recordVideo(self):
		fName = QtWidgets.QFileDialog().getSaveFileName(caption="Gerar vídeo", filter="MP4 (*.mp4)")
		vName = fName[0]
		if vName == "":
			return
		cmd = "rm %s/%s/*" % (self.default_pngDir, self.default_videoId)
		subprocess.run(cmd, shell=True)
		cursor = self.text.textCursor()
		if cursor.hasSelection():
			txt = cursor.selection().toPlainText()
			if not txt.isspace():
				txt = "__rec " + txt + " __stop"
				self.server.sendToRecord(txt, vName)

	def tryCommunication(self, n = 10):
		tries = 0
		while self.server.startCommunication() != 0 and tries < n:	
			print("Tentativa %d" % (tries))
			tries += 1
			sleep(3)
	
	def onVideoReady(self, title):
		QtWidgets.QMessageBox.question(self, "Gerar vídeo", "Vídeo %s criado com sucesso!" % title, (QtWidgets.QMessageBox.Ok))

	####################################
	#
	# TELAS ESTÁTICAS
	#
	###################################

	def showOne(self, widget):
		for i in range(self.splitter.count()):
			self.splitter.widget(i).hide()
		widget.show()

	def initSobre(self):
		self.textGrid = QtWidgets.QGridLayout()
		cursor = self.sobre_view.textCursor()
		cursor.insertText("\n")
		cursor.insertText("Equipe\n\n")
		cursor.insertText("Marcus\n")
		cursor.insertText("Arthur\n")
		cursor.insertText("Gustavo\n")
		cursor.insertText("Maria Eduarda\n")
		cursor.insertText("Róger\n")


	##################################
	#
	# DESTRUTOR
	#
	##################################
	def __del__(self):
		print("Destrutor")
		self.server.kill()
		self.images_widget.clearImages()
		exit()
	
	def closeEvent(self, event):
		self.__del__()

		
########################################################

def main():
	global app
	app = QtWidgets.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
