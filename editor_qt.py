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
        self.unique_meaning	= ahocorasick.Automaton()
        self.multiple_meaning	= ahocorasick.Automaton()
        
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
        
        self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)
        btn_open	= QtWidgets.QPushButton()
        btn_text 	= QtWidgets.QPushButton()
        show_cursor	= QtWidgets.QPushButton()
        
        btn_open.setText("Abrir Visualizador")
        btn_text.setText("Enviar Texto")
        show_cursor.setText("Posições do cursor")
        
        btn_open.clicked.connect(self.runProcess)
        btn_text.clicked.connect(self.getText)
        show_cursor.clicked.connect(self.print_cursor)
        
        self.btn_box.addWidget(btn_open)
        self.btn_box.addWidget(btn_text)
        self.btn_box.addWidget(show_cursor)
        
        self.text.setLayout(self.btn_box)
        
        self.setCentralWidget(self.splitter)
        self.splitter.addWidget(self.text)
        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        self.statusbar = self.statusBar()

        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Inclua")

    def print_cursor(self):
    	cursor = self.text.textCursor()
    	print("position:%2d\nachor:%5d\n" % (cursor.position(), cursor.anchor()))

    def getText(self):
        cursor = self.text.textCursor()
        if cursor.hasSelection():
    	        text = cursor.selection().toPlainText()
        else: #Deixa o texto alternando vermelho e preto
                text = self.text.toPlainText()
                init_pos = cursor.position()
                cursor.movePosition(cursor.Start)
                k = 1
                while cursor.movePosition(cursor.NextWord, cursor.KeepAnchor) :
                        cursor.movePosition(cursor.StartOfWord)
                        if k % 2 == 1:
                            cursor.select(cursor.WordUnderCursor)
                            self.text.setTextCursor(cursor)
                            red = QtGui.QColor(0xFF0000)
                            self.text.setTextColor(red)
                       	else :
                      	    cursor.select(cursor.WordUnderCursor)
                      	    self.text.setTextCursor(cursor)
                      	    black = QtGui.QColor(0x0)
                      	    self.text.setTextColor(black)
                        print("word:", cursor.selection().toPlainText(), end="|")
                        print(cursor.anchor(), cursor.position())
                        cursor.clearSelection()
                        k+=1
                cursor.setPosition(init_pos)
                self.text.setFocus()
                self.text.setTextCursor(cursor)
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
