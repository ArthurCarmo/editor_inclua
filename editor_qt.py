import sys
import ahocorasick
import subprocess

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices

class Main(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.xephyr 		= QProcess(self)
        self.xeyes 		= QProcess(self)
        self.window_manager	= QProcess(self)
        self.unique_meaning	= []
        self.multiple_meaning	= []
        self.automaton		= ahocorasick.Automaton()
        
        self.initUI()
        
    def initToolbar(self):
        self.toolbar = self.addToolBar("Options")
        self.addToolBarBreak()

    def initFormatbar(self):
        self.formatBar = self.addToolBar("Format")

    def initMenubar(self):
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        edit = menubar.addMenu("Edit")
        view = menubar.addMenu("View")

    def initUI(self):
        self.splitter	= QtWidgets.QSplitter(self)
        self.text	= QtWidgets.QTextEdit()
        self.cursor	= self.text.textCursor()
        
        self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)
        self.btn_open	= QtWidgets.QPushButton()
        self.btn_text 	= QtWidgets.QPushButton()
        
        self.btn_open.setText("Abrir Visualizador");
        self.btn_text.setText("Enviar Texto");
        
        self.btn_open.clicked.connect(self.runProcess)
        self.btn_text.clicked.connect(self.getText)
        
        self.btn_box.addWidget(self.btn_open)
        self.btn_box.addWidget(self.btn_text)
        
        self.text.setLayout(self.btn_box)
        
        self.setCentralWidget(self.splitter)
        self.splitter.addWidget(self.text)
        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        self.statusbar = self.statusBar()

        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Inclua")

    def getText(self):
        self.cursor = self.text.textCursor()
        if self.cursor.hasSelection():
    	        text = self.cursor.selection().toPlainText()
        else:
                text = self.text.toPlainText()
                self.text.clear()
        print(text)
    
    def runProcess(self):
        print(subprocess.call(["ls", "-l"]))
        self.xeyes.start("xeyes")
        document = QUrl("./docs/fisica.pdf")
        QDesktopServices.openUrl(document)

    def onFinished(self):
        print("Exit")
        exit()

    def __del__(self):
        print("Destrutor")
        self.xeyes.kill()
        self.xephyr.kill()
        exit()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
