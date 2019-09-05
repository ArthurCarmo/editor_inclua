import os
from shutil import copyfile
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
		self.imgGrid = QtWidgets.QGridLayout()
		self.n_images = 0

	def loadImages(self):
		names = []
		for filename in os.listdir("media/images/"):
			names.append("media/images/" + filename)
		names.sort()
		
		self.n_images = 0
		
		self.imgGrid = QtWidgets.QGridLayout()
		for filename in names:
			label = GImageButton(filename, self.n_images + 1, self)
			self.imgGrid.addWidget(label, 0, self.n_images)
			label.onClick.connect(self.imageClicked)
			self.n_images += 1
		
		view = QtWidgets.QWidget()
		view.setLayout(self.imgGrid)
		self.setWidget(view)
			
	def imageClicked(self, index):
		self.onClick.emit(index)
		
	def addImage(self, src):
		cwd = os.getcwd()
		filename, file_extension = os.path.splitext(src)
		
		filename = "media/images/IMG%d%s" % (self.n_images, file_extension.upper())
		
		copyfile(src, "%s/%s" % (cwd, filename))
		self.loadImages()
