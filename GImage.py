import os
from natsort import natsorted
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
    default_box_width  = 130
    default_box_height = 130
    
#    default_alignment = QtCore.Qt.AlignRight | QtCore.Qt.AlignTop
    default_alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop

    def __init__(self, img_url, index, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.image = img_url
        self.index = index

        self.parent = parent

        self.selected = False
        
        pixmap = QtGui.QPixmap(img_url)
        self.setIcon(QtGui.QIcon(pixmap))
        self.setIconSize(QtCore.QSize(self.default_width, self.default_height))
        self.setFixedSize(self.icon().actualSize(QtCore.QSize(self.default_width, self.default_height)))
        self.setFixedSize(QtCore.QSize(self.default_box_width, self.default_box_height))
#        self.setStyleSheet("QPushButton { border-style: outset }") 
        
        self.layout = QtWidgets.QVBoxLayout()
        self.checkbox = QtWidgets.QCheckBox()
        self.layout.addWidget(self.checkbox, alignment = self.default_alignment)
        self.setLayout(self.layout)
#        self.checkbox.raise_()
       
        self.checkbox.hide()
       	self.checkbox.toggled.connect(self.setSelected)
    
    def toggleSelectionView(self):
        self.selected = False
        self.checkbox.setChecked(False)
        if self.checkbox.isVisible():
            self.checkbox.hide()
        else:
            self.checkbox.show()

    def setSelectionView(self, visible):
        self.selected = False
        self.checkbox.setChecked(False)
        if visible:
            self.checkbox.show()
        else:
            self.checkbox.hide()
    
    def toggleSelected(self):
        self.selected = not self.selected
        self.checkbox.setChecked(self.selected)
        print("Selected -> %d" % int(self.selected))
        
    def setSelected(self, selected):
        self.selected = selected
        self.checkbox.setChecked(self.selected)
        print("Selected -> %d" % int(self.selected))

    def isSelected(self):
        return self.selected
    
    def getIndex(self):
        return self.index

    def mousePressEvent(self, ev):
        mouseButton = ev.buttons()
        if mouseButton == QtCore.Qt.LeftButton:
            if self.checkbox.isVisible():
                self.checkbox.toggle()
            else:
                self.onClick.emit(self.index)
            	
        super().mousePressEvent(ev)
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
		self.next_id = 0
		self.raise_id = 1
		self.n_images = 0
		self.dl_index = 0
		self.mode = mode
		self.imagesPerRow = 5
		
		self.onDownloadFinished.connect(self.onImageDownloaded)

	def loadImages(self):
		names = []
		for filename in os.listdir("media/images/"):
			names.append("media/images/" + filename)
		names = natsorted(names)
		
		self.n_images = 0
		
		self.imgGrid = QtWidgets.QGridLayout()
		for filename in names:
			label = GImageButton(filename, self.n_images, self)
			label.onClick.connect(self.imageClicked)				
			self.imgGrid.addWidget(label, self.n_images // self.imagesPerRow, self.n_images % self.imagesPerRow)
			self.next_id  += self.raise_id
			self.n_images += 1
		
		self.raise_id = 0
		#view = QtWidgets.QGroupBox()
		view = QtWidgets.QWidget()
		view.setLayout(self.imgGrid)
		self.setWidget(view)

	def imageClicked(self, index):
		self.onClick.emit(index)
		
	def addImagesFromFile(self, files):
		cwd = os.getcwd()
		
		for src in files:
			filename, file_extension = os.path.splitext(src)
			filename = "media/images/IMG%d%s" % (self.next_id, file_extension.upper())
			copyfile(src, "%s/%s" % (cwd, filename))
			self.next_id += 1
		
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
		visible = self.mode == self.selectable
		for img in self.findChildren(GImageButton):
			img.setSelectionView(visible)
	
	def selectAll(self):
		for img in self.findChildren(GImageButton):
			img.setSelection(True)
			
	def getSelected(self):
		l = []
		for img in self.findChildren(GImageButton):
			if img.isSelected():
				l.append(img.index)
	
	def clear(self):
		return

