import os
import threading
import subprocess

from shutil import copyfile
from PyQt5 import QtWidgets, QtGui , QtCore

#################################
#
# Botões com imagens
#
#################################
class GImageButton(QtWidgets.QPushButton):
    onClick = QtCore.pyqtSignal(int)

    default_width  = 120
    default_height = 120

    def __init__(self, img_url, index, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.image = img_url
        self.index = index
        self.parent = parent
        pixmap = QtGui.QPixmap(img_url)
        self.setIcon(QtGui.QIcon(pixmap))
        self.setIconSize(QtCore.QSize(self.default_width, self.default_height))
        self.setFixedSize(self.icon().actualSize(QtCore.QSize(self.default_width, self.default_height)))

    def mousePressEvent(self, ev):
    	self.onClick.emit(self.index)
#        lc = self.parent.text.textCursor()
#        range_content = lc.selectedText()
#        lc.insertText("__IMGX_" + str(self.index) + " " + range_content + " IMGX__")

    def contextMenuEvent(self, ev):
        menu = QtWidgets.QMenu()
        delete = QtWidgets.QAction(self.style().standardIcon(QtWidgets.QStyle.SP_BrowserStop), "Remover", self)
        delete.setStatusTip("Remover essa imagem da lista")
	#delete.triggered.connect()
	
        menu.addAction(delete)
        menu.exec(ev.globalPos())

#################################
#
# CheckBoxes com imagens
#
#################################
class GImageCheckBox(QtWidgets.QCheckBox):
    onClick = QtCore.pyqtSignal(int)

    default_width  = 120
    default_height = 120

    def __init__(self, img_url, index, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        self.image = img_url
        self.index = index
        self.parent = parent
        self.setFixedSize(self.default_width, self.default_height)
        pixmap = QtGui.QPixmap(img_url)
        self.setIcon(QtGui.QIcon(pixmap))
        self.setIconSize(QtCore.QSize(self.default_width, self.default_height))
        self.setFixedSize(self.icon().actualSize(QtCore.QSize(self.default_width, self.default_height)))
       
#################################
#
# Container em grid das imagens
#
################################# 
class GImageGrid(QtWidgets.QScrollArea):
	onClick = QtCore.pyqtSignal(int)
	onDownloadFinished = QtCore.pyqtSignal()
	
	clickable  = 0
	selectable = 1
	
	def __init__(self, mode = clickable, parent = None):
		QtWidgets.QScrollArea.__init__(self, parent)
		self.imgGrid = QtWidgets.QGridLayout()
		self.n_images = 0
		self.dl_index = 0
		self.mode = mode
		
		self.onDownloadFinished.connect(self.onImageDownloaded)

	def loadImages(self):
		names = []
		for filename in os.listdir("media/images/"):
			names.append("media/images/" + filename)
		names.sort()
		
		self.n_images = 0
		
		self.imgGrid = QtWidgets.QGridLayout()
		for filename in names:
			
			if self.mode == GImageGrid.clickable:
				label = GImageButton(filename, self.n_images + 1, self)
				label.onClick.connect(self.imageClicked)
			else:
				label = GImageCheckBox(filename, self.n_images + 1, self)
				
			self.imgGrid.addWidget(label, 0, self.n_images)
			self.n_images += 1
		
		view = QtWidgets.QGroupBox()
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
	
	def mode(self):
		return self.mode
	
	def setMode(self, mode):
		self.mode = mode
		self.loadImages()
	
	def clear(self):
		return

