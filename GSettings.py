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

	# Macros
	KnownColor		= 0
	UnknownColor	= 1
	TagsColor		= 2
	CommandsColor	= 3

	# Signals
	newColorsSet = QtCore.pyqtSignal(dict)

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

		self.changeKnownColor.clicked.connect(lambda : self.newColorSelectionMenu(self.KnownColor))
		self.changeUnknownColor.clicked.connect(lambda : self.newColorSelectionMenu(self.UnknownColor))
		self.changeTagsColor.clicked.connect(lambda : self.newColorSelectionMenu(self.TagsColor))
		self.changeCommandsColor.clicked.connect(lambda : self.newColorSelectionMenu(self.CommandsColor))

		self.changeKnownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeUnknownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeTagsColor.setStyleSheet("text-align:left; padding:3px")
		self.changeCommandsColor.setStyleSheet("text-align:left; padding:3px")

		self.salvar		= QtWidgets.QPushButton("Salvar")
		self.cancelar	= QtWidgets.QPushButton("Cancelar")
		self.resetar	= QtWidgets.QPushButton("Resetar")

		self.salvar.clicked.connect(self.commitColorChanges)
		self.cancelar.clicked.connect(self.cancelColorChanges)
		self.resetar.clicked.connect(self.resetDefaultValues)

		colorsExitLayout = QtWidgets.QHBoxLayout()
		colorsExitLayout.addWidget(self.salvar)
		colorsExitLayout.addWidget(self.cancelar)
		colorsExitLayout.addWidget(self.resetar)

		self.updateButtons()

		colorsLayout = QtWidgets.QVBoxLayout()
		colorsLayout.addWidget(self.changeKnownColor)
		colorsLayout.addWidget(self.changeUnknownColor)
		colorsLayout.addWidget(self.changeTagsColor)
		colorsLayout.addWidget(self.changeCommandsColor)

		colorsLayout.addLayout(colorsExitLayout)
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

		self.subcl_known	= QtGui.QColor(0x000000)
		self.subcl_unknown	= QtGui.QColor(0xFF0000)
		self.subcl_tag		= QtGui.QColor(0x000088)
		self.subcl_cmd	  	= QtGui.QColor(0x2200FF)

	def updateButtons(self):
		knownPixmap = QtGui.QPixmap(16, 9)
		knownPixmap.fill(self.cl_known)
		self.changeKnownColor.setIcon(QtGui.QIcon(knownPixmap))

		unknownPixmap = QtGui.QPixmap(16, 9)
		unknownPixmap.fill(self.cl_unknown)
		self.changeUnknownColor.setIcon(QtGui.QIcon(unknownPixmap))

		tagsPixmap = QtGui.QPixmap(16, 9)
		tagsPixmap.fill(self.cl_tag)
		self.changeTagsColor.setIcon(QtGui.QIcon(tagsPixmap))

		commandsPixmap = QtGui.QPixmap(16, 9)
		commandsPixmap.fill(self.cl_cmd)
		self.changeCommandsColor.setIcon(QtGui.QIcon(commandsPixmap))
	
	def newColorSelectionMenu(self, target):
			self.dialog = QtWidgets.QColorDialog()
			self.dialog.colorSelected.connect(lambda color: self.onColorSelected(target, color))
			if target == self.KnownColor:
				self.dialog.setCurrentColor(self.cl_known)
			elif target == self.UnknownColor:
				self.dialog.setCurrentColor(self.cl_unknown)
			elif target == self.TagsColor:
				self.dialog.setCurrentColor(self.cl_tag)
			elif target == self.CommandsColor:
				self.dialog.setCurrentColor(self.cl_cmd)
			self.dialog.open()

	def onColorSelected(self, target, color):
		if target == self.KnownColor:
			self.cl_known = color
		elif target == self.UnknownColor:
			self.cl_unknown = color
		elif target == self.TagsColor:
			self.cl_tag = color
		elif target == self.CommandsColor:
			self.cl_cmd = color
		
		self.updateButtons()

		
	def commitColorChanges(self):
		self.subcl_known	= self.cl_known
		self.subcl_unknown	= self.cl_unknown
		self.subcl_tag		= self.cl_tag
		self.subcl_cmd		= self.cl_cmd

		self.newColorsSet.emit()

	def cancelColorChanges(self):
		self.cl_known	= self.subcl_known
		self.cl_unknown	= self.subcl_unknown
		self.cl_tag		= self.subcl_tag
		self.cl_cmd		= self.subcl_cmd

	def resetDefaultValues(self):
		self.cl_known	= GDefaultValues.cl_known
		self.cl_unknown	= GDefaultValues.cl_unknown
		self.cl_tag		= GDefaultValues.cl_tag
		self.cl_cmd		= GDefaultValues.cl_cmd
		
		self.updateButtons()