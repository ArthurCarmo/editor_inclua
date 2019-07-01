import sys
import ahocorasick
import subprocess

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices

import re

class EHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        self.parent = parent
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self.known_words= ahocorasick.Automaton()
        f = open("palavras")
        for w in f.read().splitlines():
            self.known_words.add_word(w, len(w))
        self.known_words.make_automaton()
        self.tags = ["<", ">", "[", "]"]
        self.commands = ["__save", "__stop", \
            "__rec", "__last"]
        self.incomplete_keywords = ["i", "im", "img"]
        self.keywords = ["img0", "img1", "img2", "img3"]
        
    def highlightBlock(self, text):
        cl_known	= QtGui.QColor(0x000000)
        cl_unknown	= QtGui.QColor(0xFF0000)
        cl_tag	    = QtGui.QColor(0x000088)
        cl_cmd      = QtGui.QColor(0x2200FF)
        cl_wkblue   = QtGui.QColor(0x000077)

        known       = QtGui.QTextCharFormat()
        unknown     = QtGui.QTextCharFormat()
        tag         = QtGui.QTextCharFormat()
        cmd         = QtGui.QTextCharFormat()
        hitting     = QtGui.QTextCharFormat()

        known.setForeground(cl_known)
        unknown.setForeground(cl_unknown)
        tag.setForeground(cl_tag)
        cmd.setForeground(cl_cmd)
        hitting.setForeground(cl_wkblue)

        cmd.setFontWeight(QtGui.QFont.Bold)

        word  = QtCore.QRegularExpression("[^<>\\[\\]=\\(\\).,;\\s\\n]+")
        tags  = QtCore.QRegularExpression("[<>\\[\\]]")
        links = QtCore.QRegularExpression("=.+?>")

        i = word.globalMatch(text)
        while i.hasNext():
            match = i.next()
            end = match.capturedStart() + match.capturedLength()
            w = text[match.capturedStart():end]
            if w in self.known_words:
                self.setFormat(match.capturedStart(), match.capturedLength(), known)
            elif w in self.commands:
                self.setFormat(match.capturedStart(), match.capturedLength(), cmd)
            elif w in self.keywords:
                self.setFormat(match.capturedStart(), match.capturedLength(), tag)
            elif w in self.incomplete_keywords:
                self.setFormat(match.capturedStart(), match.capturedLength(), hitting)
            else:
                self.setFormat(match.capturedStart(), match.capturedLength(), unknown)
        
        i = tags.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), tag)
        
        i = links.globalMatch(text)
        while i.hasNext():
            match = i.next()
            self.setFormat(match.capturedStart()+1, match.capturedLength()-1, cmd)
        #print(text)




class Main(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.xephyr 		= QProcess(self)
        self.xeyes 		    = QProcess(self)
        self.window_manager	= QProcess(self)
        
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
        self.text	    = QtWidgets.QTextEdit()
        highlighter     = EHighlighter(self.text.document())
        self.btn_box	= QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self.text)

        btn_open	= QtWidgets.QPushButton()
        btn_text 	= QtWidgets.QPushButton()
        btn_show_cursor	= QtWidgets.QPushButton()
        
        btn_open.setText("Abrir Visualizador")
        btn_text.setText("Enviar Texto")
        btn_show_cursor.setText("Posições do cursor")
        
        btn_open.clicked.connect(self.runProcess)
        btn_text.clicked.connect(self.getText)
        btn_show_cursor.clicked.connect(self.print_cursor)
        
        self.btn_box.addWidget(btn_open)
        self.btn_box.addWidget(btn_text)
        self.btn_box.addWidget(btn_show_cursor)
        
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
        else:
                text = self.text.toPlainText()
        print(text)
    
    def is_whole_word(self, text, start, end):
        if start > 0 and (text[start-1].isalpha() or text[start-1] == "_") :
            return False
        if end+1 < len(text) and (text[end+1].isalpha() or text[end+1] == "_") :
            return False
        return True

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
    global app
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
