import os
import threading
import subprocess

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
	onDownloadFinished = QtCore.pyqtSignal()
	
	def __init__(self, parent = None):
		QtWidgets.QScrollArea.__init__(self, parent)
		self.imgGrid = QtWidgets.QGridLayout()
		self.n_images = 0
		self.dl_index = 0

		self.onDownloadFinished.connect(self.onImageDownloaded)

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
		
	def addImagesFromFile(self, files):
		cwd = os.getcwd()
		
		i = self.n_images
		for src in files:
			filename, file_extension = os.path.splitext(src)
			filename = "media/images/IMG%d%s" % (i, file_extension.upper())
			copyfile(src, "%s/%s" % (cwd, filename))
			i += 1
		
		self.loadImages()
		
	def addImageFromUrl(self, src):
		threading.Thread(target=self.handle_web_image, args=([src])).start()
	
	def onImageDownloaded(self):
		self.loadImages()
		self.dl_index += 1
	
	def handle_web_image(self, src):
		cwd = os.getcwd()
		filename, file_extension = os.path.splitext(src)
		cmd = "wget -O %s/media/images/DL%d%s %s" % (cwd, self.dl_index, file_extension, src)
		subprocess.run(cmd, shell=True)
		self.onDownloadFinished.emit()
	
	def clear(self):
		return
