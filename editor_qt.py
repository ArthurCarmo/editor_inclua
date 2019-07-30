import re
import sys
import GServer
import ahocorasick

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices
from pyvirtualdisplay import Display
from GSyntax import GSyntaxHighlighter

class Main(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.xephyr 		= QProcess(self)
		self.avatar 		= QProcess(self)
		self.window_manager	= QProcess(self)
		self.display = Display(visible=0, size=(640, 480))
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
		self.splitter	= QtWidgets.QSplitter(self)
		self.text	= QtWidgets.QTextEdit()
		self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)
		
		# Única chamada necessária para o SyntaxHighlighter
		highlighter	= GSyntaxHighlighter(self.text.document())
		
		# Setup do widget com o display virtual
		self.server_widget = GServer.getServerWidget(self.xephyr, "GXEPHYRSV")
		self.server_widget.setMinimumSize(QtCore.QSize(640, 480))
		self.server_widget.setMaximumSize(QtCore.QSize(640, 480))
		
		# Setup dos botões
		btn_open	= QtWidgets.QPushButton()
		btn_text 	= QtWidgets.QPushButton()
		btn_conn 	= QtWidgets.QPushButton()
		btn_show_cursor	= QtWidgets.QPushButton()
		
		btn_open.setText("Abrir Visualizador")
		btn_text.setText("Enviar Texto")
		btn_conn.setText("Conectar")
		btn_show_cursor.setText("Posições do cursor")
		
		btn_open.clicked.connect(self.runProcess)
		btn_text.clicked.connect(self.sendText)
		btn_conn.clicked.connect(GServer.startCommunication)
		btn_show_cursor.clicked.connect(self.print_cursor)
		
		self.btn_box.addWidget(btn_open)
		self.btn_box.addWidget(btn_text)
		self.btn_box.addWidget(btn_conn)
		self.btn_box.addWidget(btn_show_cursor)
		
		# Isso pode estar errado, coloca o layout
		# do btn_box no widget do editor de texto
		self.text.setLayout(self.btn_box)
		
		# Widget que aparece na janela é o splitter
		# os outros são adicionados a ele
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		self.splitter.addWidget(self.server_widget)
		
		# Init
		self.initToolbar()
		self.initFormatbar()
		self.initMenubar()

		self.statusbar = self.statusBar()

		self.setGeometry(0, 0, 1024, 480)
		self.setWindowTitle("Inclua")
		
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
		
	def runProcess(self):
		document = QUrl("./docs/fisica.pdf")
		QDesktopServices.openUrl(document)
		
	def toggleVisible(self, widget):
		if widget.isVisible():
			widget.hide()
		else:
			widget.show()
	
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
