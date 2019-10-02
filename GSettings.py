import os

from PyQt5 import QtCore, QtGui, QtWidgets

class GDefaultValues():
	cwd		= os.getcwd()
	home		= os.path.expanduser("~")
	pngDir		= home + "/.config/unity3d/LAViD/VLibrasVideoMaker"
	videoId 	= "teste_renderer"
	imgDir		= cwd + "/media/images"
	
	imgPrefix	= "IMG"
	
	pdfJs		= 'file://' + cwd + '/pdfjs/web/viewer.html'
	
	# Colors
	cl_known	= QtGui.QColor(0x000000)
	cl_unknown	= QtGui.QColor(0xFF0000)
	cl_tag		= QtGui.QColor(0x000088)
	cl_cmd	  	= QtGui.QColor(0x2200FF)
	cl_wkblue   	= QtGui.QColor(0x000077)
	
class GCustomizationMenu(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.setWindowTitle("Preferências")

		self.tabsMenu = QtWidgets.QTabWidget()
		
		colorsTab = QtWidgets.QWidget()

		colorDisplay	= QtWidgets.QWidget()
		colorDisplay.setGeometry(0, 0, 20, 20)
#		palette = QtGui.QPalette()
#		palette.setColor(palette.Background, color)
#		colorDisplay.setAutoFillBackground(True)
#		colorDisplay.setPalette(palette)
		
#		layout = QtWidgets.QHBoxLayout()
#		layout.addWidget(colorDialog)
#		layout.addWidget(colorDisplay)
#		colorsTab.setLayout(layout)

		self.tabsMenu.addTab(colorsTab, "Cores")

		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.tabsMenu)
		self.setLayout(layout)