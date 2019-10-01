from PyQt5 import QtWidgets, QtCore

from GFile import GDocument
from GImage import GCustomImageDialog
from GScreenUtils import GLayeredDocumentCanvas

class Main(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.splitter = QtWidgets.QSplitter(self)

		self.document = GDocument(self)
		
		self.main = QtWidgets.QWidget()
		
		self.widg = GLayeredDocumentCanvas(self.document)
				
		self.tb = QtWidgets.QToolBar()
		self.tb.addWidget(QtWidgets.QPushButton("WAT"))
		self.layout = QtWidgets.QHBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(self.tb, alignment = QtCore.Qt.AlignRight)
		self.layout.addWidget(self.widg)

		self.main.setLayout(self.layout)
		
		self.lbl = QtWidgets.QLabel()
		
		import os
		cwd = os.getcwd()
		self.document.load(cwd + "/docs/fisica.pdf")
		
		self.splitter.addWidget(self.lbl)
		self.splitter.addWidget(self.main)
		self.setCentralWidget(self.splitter)
		
		self.widg.screenShot.connect(self.setLabel)
		
		teste = GCustomImageDialog().question()
		print(teste)
		
	def setLabel(self, px):
		self.lbl.setPixmap(px)
		self.lbl.hide()
		self.lbl.show()
		
	
def main():
	import sys
	global app
	app = QtWidgets.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())
if __name__ == "__main__":
	main()
