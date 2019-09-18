from PyQt5 import QtGui, QtCore, QtWidgets
from GFile import GDocument

class GRubberBand(QtWidgets.QRubberBand):
	def __init__(self, shape, parent = None):
		QtWidgets.QRubberBand.__init__(self, shape, parent)
		self.origin = QtCore.QPoint(0, 0)

class GScreenshot(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		self.pixmap = QtGui.QPixmap()
	

class GLayeredDocumentCanvas(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		self.area = GRubberBand(GRubberBand.Rectangle, self)
		
		self.document = GDocument(self)
		self.document.load("/home/arthur/Documents/editor_inclua/docs/fisica.pdf")
		self.setCaptureMode(True)
		
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.document)
		
		self.drag = False
		self.origin = QtCore.QPoint(0, 0)
		self.mousePosition = QtCore.QPoint(0, 0)
		
		self.setLayout(self.layout)
	
	def gdocument(self):
		return self.document
	
	def setGDocument(self, document):
		self.document = document
		
	def setCaptureMode(self, capture):
		self.document.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, capture)
	
	def getCaptureMode(self):
		return self.document.testAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
	
	def mousePressEvent(self, event):
		self.mousePosition = event.pos()
		self.drag = False
		
		if event.buttons() != QtCore.Qt.LeftButton:
			self.area.hide()
			return
		
		if not self.area.isVisible() or not self.area.geometry().contains(self.mousePosition):
			self.origin = self.mousePosition
			self.area.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
			self.area.show()	
		else:
			self.drag = True
		
		
		
	def mouseMoveEvent(self, event):
		if self.drag:
			movement = event.pos()
			self.mousePosition -= movement
			self.origin -= self.mousePosition
			self.area.move(self.origin)
			self.mousePosition = movement
		else:
			self.area.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())


class Main(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.splitter = QtWidgets.QSplitter(self)
		self.widg = GLayeredDocumentCanvas()
		self.widg.show()
		
		self.splitter.addWidget(self.widg)
		self.splitter.addWidget(QtWidgets.QGraphicsView())
		self.setCentralWidget(self.splitter)
		
	
def main():
	import sys
	global app
	app = QtWidgets.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
