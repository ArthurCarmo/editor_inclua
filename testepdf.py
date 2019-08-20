import sys
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

PDFJS = 'file:///home/arthur/editor_inclua/pdfjs/web/viewer.html'
PDF = 'file:///home/arthur/editor_inclua/fisica.pdf'
app = QtWidgets.QApplication(sys.argv)
pdf_web_page = QtWebEngineWidgets.QWebEngineView()
pdf_web_page.load(QtCore.QUrl.fromUserInput('%s?file=%s' % (PDFJS, PDF)))
pdf_web_page.show()
sys.exit(app.exec_())