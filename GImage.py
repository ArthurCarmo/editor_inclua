import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap

class GImageButton(QtWidgets.QLabel):

    onClick = QtCore.pyqtSignal(int)

    def __init__(self, img_url, index, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.image = img_url
        self.index = index
        self.parent = parent
        self.setScaledContents(True)
        self.setFixedSize(90, 90)
        pixmap = QPixmap(img_url)
        self.setPixmap(pixmap)

    def mousePressEvent(self, ev):
    	self.onClick.emit(self.index)
#        lc = self.parent.text.textCursor()
#        range_content = lc.selectedText()
#        lc.insertText("__IMGX_" + str(self.index) + " " + range_content + " IMGX__")
        
        
class GImageGrid(QtWidgets.QScrollArea):
	
	onClick = QtCore.pyqtSignal(int)
	
	def __init__(self, parent = None):
		QtWidgets.QScrollArea.__init__(self, parent)

	def loadImages(self):
		names = []
		for filename in os.listdir("media/images/"):
			names.append("media/images/" + filename)
		names.sort()
		i = 1
		
		imgGrid = QtWidgets.QGridLayout()
		for filename in names:
			label = GImageButton(filename, i, self)
			imgGrid.addWidget(label, 0, i-1)
			label.onClick.connect(self.imageClicked)
			i += 1
			
		view = QtWidgets.QWidget()
		view.setLayout(imgGrid)
		self.setWidget(view)
			
	def imageClicked(self, index):
		self.onClick.emit(index)
