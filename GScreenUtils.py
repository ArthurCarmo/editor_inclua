from PyQt5 import QtGui, QtCore, QtWidgets
from GFile import GDocument

class GRubberBand(QtWidgets.QRubberBand):
	def __init__(self, shape, parent = None):
		QtWidgets.QRubberBand.__init__(self, shape, parent)

		self.bottomRightGrip = QtWidgets.QSizeGrip(self)		
		
		self.layout = QtWidgets.QHBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(self.bottomRightGrip, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
		self.setLayout(self.layout)

	def mouseClicked(self, event):
		click = self.mapFromParent(event.pos())
		return self.bottomRightGrip.geometry().contains(click)
	
class GLayeredDocumentCanvas(QtWidgets.QWidget):

	screenShot = QtCore.pyqtSignal(QtGui.QPixmap)

	def __init__(self, target, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		self.document = target
		self.area = GRubberBand(GRubberBand.Rectangle, self)

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
			self.takeScreenShot()
			return
		
		if not self.area.isVisible() or not self.area.geometry().contains(self.mousePosition):
			self.origin = self.mousePosition
			self.area.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
			self.area.show()	
		else:
			self.drag = not self.area.mouseClicked(event)
		
	def mouseMoveEvent(self, event):
		bounds = self.geometry()
		
		if self.drag:
			movement = event.pos()
			self.mousePosition -= movement
			
			newOrigin = QtCore.QPoint(self.origin.x(), self.origin.y())
			newOrigin -= self.mousePosition
			self.mousePosition = movement
			
			size = self.area.size()
			newTop	= max(bounds.top(), newOrigin.y())
			newLeft	= max(bounds.left(), newOrigin.x())
			
			if newTop + size.height() > bounds.bottom():
				newTop = self.origin.y()
				
			if newLeft + size.width() > bounds.right():
				newLeft = self.origin.x()
				
			self.origin = QtCore.QPoint(newLeft, newTop)
			self.area.move(self.origin)
		else:
			target = event.pos()
			newX = max(bounds.left(), min(target.x(), bounds.left() + bounds.width()))
			newY = max(bounds.top(), min(target.y(), bounds.top() + bounds.height()))
			target = QtCore.QPoint(newX, newY)
			self.area.setGeometry(QtCore.QRect(self.origin, target).normalized())
			
	def takeScreenShot(self):
		pos = self.document.mapFrom(self, self.area.geometry().topLeft())
		size = self.area.geometry().size()
		region = QtCore.QRect(pos, size)
		px = QtGui.QPixmap(region.size())			
		self.document.render(px, QtCore.QPoint(), QtGui.QRegion(region))
		self.screenShot.emit(px)
		
		

class Main(QtWidgets.QMainWindow):
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.splitter = QtWidgets.QSplitter(self)

		self.document = GDocument(self)
		self.widg = GLayeredDocumentCanvas(self.document)

		self.widg.show()
		
		self.lbl = QtWidgets.QLabel()
		
		
		self.document.load("/home/arthur/Documents/editor_inclua/docs/fisica.pdf")
		
		self.splitter.addWidget(self.widg)
		self.splitter.addWidget(self.lbl)
		self.setCentralWidget(self.splitter)
		
		self.widg.screenShot.connect(self.setLabel)
		
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
