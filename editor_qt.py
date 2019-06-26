import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QProcess, QUrl
from popplerqt5 import Poppler

class Editor(QtWidgets.QTextEdit):
    def __init__(self, parent = None):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.setMinimumSize(400, 300)

class PdfViewer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.document = Poppler.Document.load("docs/fisica.pdf")
        self.setMinimumSize(400, 300)

class Main(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.xephyr_process = QProcess()
        self.xeyes = QProcess()
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
        self.splitter = QtWidgets.QSplitter(self)
        self.text = Editor()
        self.pdf_viewer = PdfViewer()
        
        self.setCentralWidget(self.splitter)
        self.splitter.addWidget(self.text)
        self.splitter.addWidget(self.pdf_viewer)
        self.splitter.setCollapsible(1, True)
        self.initToolbar()
        self.initFormatbar()
        self.initMenubar()

        self.statusbar = self.statusBar()

        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Inclua")
 
        self.xephyr_process = QProcess(self)
        program = "Xephyr"
        params  = ["-ac", "-br", "-screen", "640x480", ":100"]
        self.xephyr_process.finished.connect(self.onFinished)
        self.xephyr_process.start(program, params)
        print(self.xephyr_process.pid())

 
    def onFinished(self):
        print("Exit")
        exit()

    def __del__(self):
        print("Destrutor")
        self.xephyr_process.kill()
        exit()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
