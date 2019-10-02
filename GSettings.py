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
	
class GCustomizationMenu(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.setWindowTitle("Preferências")
		self.tabsMenu = QtWidgets.QTabWidget()
		self.colorsTab = QtWidgets.QWidget()

		self.getCurrentColorScheme()

		self.changeKnownColor		= QtWidgets.QPushButton("Palavras conhecidas")
		self.changeUnknownColor		= QtWidgets.QPushButton("Palavras desconhecidas")
		self.changeTagsColor		= QtWidgets.QPushButton("Tags/Marcações")
		self.changeCommandsColor	= QtWidgets.QPushButton("Comandos")

		self.updateButtons()

		colorsLayout = QtWidgets.QVBoxLayout()
		colorsLayout.addWidget(self.changeKnownColor)
		colorsLayout.addWidget(self.changeUnknownColor)
		colorsLayout.addWidget(self.changeTagsColor)
		colorsLayout.addWidget(self.changeCommandsColor)
		self.colorsTab.setLayout(colorsLayout)
		
		self.tabsMenu.addTab(self.colorsTab, "Cores")

		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.tabsMenu)
		self.setLayout(layout)

	def getCurrentColorScheme(self):
		self.cl_known	= QtGui.QColor(0x000000)
		self.cl_unknown	= QtGui.QColor(0xFF0000)
		self.cl_tag		= QtGui.QColor(0x000088)
		self.cl_cmd	  	= QtGui.QColor(0x2200FF)

	def updateButtons(self):
		knownPixmap = QtGui.QPixmap(100, 100)
		knownPixmap.fill(self.cl_known)
		self.changeKnownColor.setIcon(QtGui.QIcon(knownPixmap))

		unknownPixmap = QtGui.QPixmap(100, 100)
		unknownPixmap.fill(self.cl_unknown)
		self.changeUnknownColor.setIcon(QtGui.QIcon(unknownPixmap))

		tagsPixmap = QtGui.QPixmap(100, 100)
		tagsPixmap.fill(self.cl_tag)
		self.changeTagsColor.setIcon(QtGui.QIcon(tagsPixmap))

		commandsPixmap = QtGui.QPixmap(100, 100)
		commandsPixmap.fill(self.cl_cmd)
		self.changeCommandsColor.setIcon(QtGui.QIcon(commandsPixmap))