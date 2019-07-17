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
		highlighter	= GSyntaxHighlighter(self.text.document())
		self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)
		
		btn_open	= QtWidgets.QPushButton()
		btn_text 	= QtWidgets.QPushButton()
		btn_conn 	= QtWidgets.QPushButton()
		btn_show_cursor	= QtWidgets.QPushButton()
		
		btn_open.setText("Abrir Visualizador")
		btn_text.setText("Enviar Texto")
		btn_conn.setText("Conectar")
		btn_show_cursor.setText("Posições do cursor")
		
		btn_open.clicked.connect(self.runProcess)
		btn_text.clicked.connect(self.getText)
		btn_conn.clicked.connect(GServer.startCommunication)
		btn_show_cursor.clicked.connect(self.print_cursor)
		
		self.btn_box.addWidget(btn_open)
		self.btn_box.addWidget(btn_text)
		self.btn_box.addWidget(btn_conn)
		self.btn_box.addWidget(btn_show_cursor)
		
		self.text.setLayout(self.btn_box)
		
		self.setCentralWidget(self.splitter)
		self.splitter.addWidget(self.text)
		
		self.initToolbar()
		self.initFormatbar()
		self.initMenubar()

		self.statusbar = self.statusBar()

		self.setGeometry(0, 0, 1024, 480)
		self.setWindowTitle("Inclua")

	def print_cursor(self):
		cursor = self.text.textCursor()
		print("position:%2d\nachor:%5d\n" % (cursor.position(), cursor.anchor()))

	def getText(self):
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
		
		xephyr_title = "GXEPHYRSV"
		self.xephyr.start("Xephyr -ac -br -screen 640x480 :100 -title " + xephyr_title)
		
#		xephyr_title= "VLibrasVideoMaker"
#		self.xephyr.start("/home/arthur/Documents/editor_inclua/unityVideo/videoCreator.x86_64 teste_renderer 1 30 32 37 -screen-fullscreen 0 -screen-quality Fantastic -force-opengl")
		
		server_widget = GServer.getServerWidget(xephyr_title)
		
		server_widget.setMinimumSize(QtCore.QSize(640, 480))
		server_widget.setMaximumSize(QtCore.QSize(640, 480))
		self.splitter.addWidget(server_widget)
		
	
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
