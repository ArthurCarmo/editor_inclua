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
	
	#######################
	#
	# Colors
	#
	#######################
	
	# tokens
	cl_known	= QtGui.QColor(0x000000)
	cl_unknown	= QtGui.QColor(0xFF0000)
	cl_tag		= QtGui.QColor(0x000088)
	cl_cmd	  	= QtGui.QColor(0x2200FF)

	# markers
	cl_textEditBackground = None
	cl_subWordFont = None
	cl_subWordBackground = None
	
	def __init__(self):
		self.__class__.cl_textEditBackground = QtWidgets.QTextEdit().palette().color(QtGui.QPalette.Window)
		self.__class__.cl_subWordFont = self.cl_textEditBackground
		rgba = [abs(x - y) for x in (255, 255, 255, 0) for y in self.cl_subWordFont.getRgb()]
		self.__class__.cl_subWordBackground = QtGui.QColor(rgba[0], rgba[1], rgba[2], 255)
	
class GColorScheme():
	Known			= 0
	Unknown			= 1
	Tags			= 2
	Commands 		= 3
	SubWordBackground	= 4
	SubWordFont		= 5
	
	def __init__(self, known = GDefaultValues.cl_known, unknown = GDefaultValues.cl_unknown, tags = GDefaultValues.cl_tag, commands = GDefaultValues.cl_cmd, subWordBackground = GDefaultValues.cl_subWordBackground, subWordFont = GDefaultValues.cl_subWordFont):
		self.cl_known 	= known
		self.cl_unknown = unknown
		self.cl_tag	= tags
		self.cl_cmd	= commands
		
		self.cl_subWordBackground = subWordBackground
		self.cl_subWordFont = subWordFont
		
	def knownColor(self):
		return self.cl_known
		
	def unknownColor(self):
		return self.cl_unknown
		
	def tagsColor(self):
		return self.cl_tag
		
	def commandsColor(self):
		return self.cl_cmd

	def subWordBackgroundColor(self):
		return self.cl_subWordBackground
		
	def subWordFontColor(self):
		return self.cl_subWordFont
		
	def getInverseColor(self, color):
		rgba = [abs(x - y) for x in (255, 255, 255, 0) for y in color.getRgb()]
		return QtGui.QColor(rgba[0], rgba[1], rgba[2], 255)
		
class GSettingsMenu(QtWidgets.QWidget):
	# Signals
	newColorScheme = QtCore.pyqtSignal(GColorScheme)

	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.setWindowTitle("Preferências")
		self.tabsMenu = QtWidgets.QTabWidget()
		
		##########################
		#
		# CORES
		#
		##########################
		
		self.utilizarCorInversa = True
		self.colorScheme = self.retrieveCurrentColorScheme()
		self.colorsTab = QtWidgets.QWidget()
		
		## TOKENS
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

		colorsTokensLayout = QtWidgets.QVBoxLayout()
		colorsTokensLayout.addWidget(self.changeKnownColor)
		colorsTokensLayout.addWidget(self.changeUnknownColor)
		colorsTokensLayout.addWidget(self.changeTagsColor)
		colorsTokensLayout.addWidget(self.changeCommandsColor)

		colorsTokensGroup = QtWidgets.QGroupBox("Tokens")
		colorsTokensGroup.setLayout(colorsTokensLayout)
		
		## MARCADORES
		
		self.utilizarCorInversaCheck = QtWidgets.QCheckBox("Utilizar fonte na cor inversa do fundo")
		self.utilizarCorInversaCheck.setChecked(self.utilizarCorInversa)
		self.utilizarCorInversaCheck.stateChanged.connect(self.colorMarkerCheckBoxChanged)
		
		self.changeSubWordFontColor = QtWidgets.QPushButton("Fonte das palavras para trocar")
		self.changeSubWordBackgroundColor = QtWidgets.QPushButton("Fundo  das palavras para trocar")
		
		self.changeSubWordFontColor.setEnabled(not self.utilizarCorInversa)
		
		self.changeSubWordFontColor.setStyleSheet("text-align:left; padding:3px")
		self.changeSubWordBackgroundColor.setStyleSheet("text-align:left; padding:3px")
		
		self.changeSubWordFontColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.SubWordFont))
		self.changeSubWordBackgroundColor.clicked.connect(lambda : self.newColorSelectionMenu(GColorScheme.SubWordBackground))
		
		colorsMarkersLayout = QtWidgets.QVBoxLayout()
		colorsMarkersLayout.addWidget(self.changeSubWordBackgroundColor)
		colorsMarkersLayout.addWidget(self.utilizarCorInversaCheck)
		colorsMarkersLayout.addWidget(self.changeSubWordFontColor)
		
		colorsMarkersGroup = QtWidgets.QGroupBox("Marcadores")
		colorsMarkersGroup.setLayout(colorsMarkersLayout)
		
		## FINALIZAR
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

		colorsExitGroup = QtWidgets.QGroupBox()
		colorsExitGroup.setLayout(colorsExitLayout)

		## LAYOUT PRINCIPAL MENU DE CORES
		colorsMainLayout = QtWidgets.QVBoxLayout()
		colorsUpperLayout = QtWidgets.QHBoxLayout()
		
		colorsUpperLayout.addWidget(colorsTokensGroup)
		colorsUpperLayout.addWidget(colorsMarkersGroup)
		
		colorsMainLayout.addLayout(colorsUpperLayout)
		colorsMainLayout.addWidget(colorsExitGroup)

		self.updateButtons()
		colorsMainLayout.addWidget(colorsExitGroup)
		
		self.colorsTab.setLayout(colorsMainLayout)


		###############################
		#
		# LAYOUT DAS TABS
		#
		###############################
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
		self.cl_subWordFont	= GDefaultValues.cl_subWordFont
		self.cl_subWordBackground = GDefaultValues.cl_subWordBackground
		
		print(self.cl_subWordFont.getRgb())
		print(self.cl_subWordBackground.getRgb())
		
		return GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont))

	def getColorScheme(self):
		return self.colorScheme
		
		
	def colorMarkerCheckBoxChanged(self, state):
		self.utilizarCorInversa = state
		self.changeSubWordFontColor.setEnabled(not state)

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
		
		subWordBackgroundPixmap = QtGui.QPixmap(16, 9)
		subWordBackgroundPixmap.fill(self.cl_subWordBackground)
		self.changeSubWordBackgroundColor.setIcon(QtGui.QIcon(subWordBackgroundPixmap))
		
		subWordFontPixmap = QtGui.QPixmap(16, 9)
		subWordFontPixmap.fill(self.cl_subWordFont)
		self.changeSubWordFontColor.setIcon(QtGui.QIcon(subWordFontPixmap))
	
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
			elif target == GColorScheme.SubWordBackground:
				self.dialog.setCurrentColor(self.cl_subWordBackground)
			elif target == GColorScheme.SubWordFont:
				self.dialog.setCurrentColor(self.cl_subWordFont)

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
		elif target == GColorScheme.SubWordBackground:
			self.cl_subWordBackground = color
		elif target == GColorScheme.SubWordFont:
			self.cl_subWordFont = color
				
		self.updateButtons()

		
	def commitColorChanges(self):
		self.colorScheme = GColorScheme(known = self.cl_known, unknown = self.cl_unknown, tags = self.cl_tag, commands = self.cl_cmd, subWordBackground = self.cl_subWordBackground, subWordFont = (GColorScheme().getInverseColor(self.cl_subWordBackground) if self.utilizarCorInversa else self.cl_subWordFont))
		self.newColorScheme.emit(self.colorScheme)

	def cancelColorChanges(self):
		print("UAAAI")
		self.cl_known	= self.colorScheme.knownColor()
		self.cl_unknown	= self.colorScheme.unknownColor()
		self.cl_tag	= self.colorScheme.tagsColor()
		self.cl_cmd	= self.colorScheme.commandsColor()
		self.cl_subWordBackground = self.colorScheme.subWordBackgroundColor()
		self.cl_subWordFont	  = self.colorScheme.subWordFontColor()
		
		self.updateButtons()

	def resetDefaultValues(self):
		self.cl_known	= GDefaultValues.cl_known
		self.cl_unknown	= GDefaultValues.cl_unknown
		self.cl_tag	= GDefaultValues.cl_tag
		self.cl_cmd	= GDefaultValues.cl_cmd
		self.cl_subWordBackground = GDefaultValues.cl_subWordBackground
		self.cl_subWordFont	  = GDefaultValues.cl_subWordFont
		
		self.updateButtons()

	def onSaveButtonPressed(self):
			self.commitColorChanges()
			self.hide()

	def onCancelButtonPressed(self):
			self.cancelColorChanges()
			self.hide()
