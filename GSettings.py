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
	
class GColorScheme():
	Known		= 0
	Unknown		= 1
	Tags		= 2
	Commands 	= 3
	
	def __init__(self, known = GDefaultValues.cl_known, unknown = GDefaultValues.cl_unknown, tags = GDefaultValues.cl_tag, commands = GDefaultValues.cl_cmd):
		self.cl_known 	= known
		self.cl_unknown = unknown
		self.cl_tag	= tags
		self.cl_cmd	= commands
		
	def knownColor(self):
		return self.cl_known
		
	def unknownColor(self):
		return self.cl_unknown
		
	def tagsColor(self):
		return self.cl_tag
		
	def commandsColor(self):
		return self.cl_cmd

class GSettingsMenu(QtWidgets.QWidget):


	# Signals
	newColorScheme = QtCore.pyqtSignal(GColorScheme)

	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.setWindowTitle("Preferências")
		self.tabsMenu = QtWidgets.QTabWidget()
		self.colorsTab = QtWidgets.QWidget()

		self.colorScheme = self.retrieveCurrentColorScheme()

		self.changeKnownColor		= QtWidgets.QPushButton("Palavras conhecidas")
		self.changeUnknownColor		= QtWidgets.QPushButton("Palavras desconhecidas")
		self.changeTagsColor		= QtWidgets.QPushButton("Tags/Marcações")
		self.changeCommandsColor	= QtWidgets.QPushButton("Comandos")

		self.changeKnownColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Known))
		self.changeUnknownColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Unknown))
		self.changeTagsColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Tags))
		self.changeCommandsColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.Commands))

		self.changeKnownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeUnknownColor.setStyleSheet("text-align:left; padding:3px")
		self.changeTagsColor.setStyleSheet("text-align:left; padding:3px")
		self.changeCommandsColor.setStyleSheet("text-align:left; padding:3px")

		self.salvar	= QtWidgets.QPushButton("Salvar")
		self.cancelar	= QtWidgets.QPushButton("Cancelar")
		self.resetar	= QtWidgets.QPushButton("Resetar")

		self.salvar.clicked.connect(self.onSaveButtonPressed)
		self.cancelar.clicked.connect(self.onCancelButtonPressed)
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

	def retrieveCurrentColorScheme(self):
		self.cl_known		= QtGui.QColor(0x000000)
		self.cl_unknown		= QtGui.QColor(0xFF0000)
		self.cl_tag		= QtGui.QColor(0x000088)
		self.cl_cmd	  	= QtGui.QColor(0x2200FF)
		
		return GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd)

	def getColorScheme(self):
		return self.colorScheme

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
			if target == GColorScheme.Known:
				self.dialog.setCurrentColor(self.cl_known)
			elif target == GColorScheme.Unknown:
				self.dialog.setCurrentColor(self.cl_unknown)
			elif target == GColorScheme.Tags:
				self.dialog.setCurrentColor(self.cl_tag)
			elif target == GColorScheme.Commands:
				self.dialog.setCurrentColor(self.cl_cmd)

			self.dialog.open()

	def onColorSelected(self, target, color):
		if target == GColorScheme.Known:
			self.cl_known = color
		elif target == GColorScheme.Unknown:
			self.cl_unknown = color
		elif target == GColorScheme.Tags:
			self.cl_tag = color
		elif target == GColorScheme.Commands:
			self.cl_cmd = color
		
		self.updateButtons()

		
	def commitColorChanges(self):
		self.colorScheme = GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd)
		self.newColorScheme.emit(self.colorScheme)

	def cancelColorChanges(self):
		print("UAAAI")
		self.cl_known	= self.colorScheme.knownColor()
		self.cl_unknown	= self.colorScheme.unknownColor()
		self.cl_tag	= self.colorScheme.tagsColor()
		self.cl_cmd	= self.colorScheme.commandsColor()

		self.updateButtons()

	def resetDefaultValues(self):
		self.cl_known	= GDefaultValues.cl_known
		self.cl_unknown	= GDefaultValues.cl_unknown
		self.cl_tag	= GDefaultValues.cl_tag
		self.cl_cmd	= GDefaultValues.cl_cmd
		
		self.updateButtons()

	def onSaveButtonPressed(self):
			self.commitColorChanges()
			self.hide()

	def onCancelButtonPressed(self):
			self.cancelColorChanges()
			self.hide()
