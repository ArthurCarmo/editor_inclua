
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap

class GImageButton(QLabel):
    def __init__(self, img_url, index, parent=None):
        QLabel.__init__(self, parent)
        self.image = img_url
        self.index = index
        self.parent = parent
        self.setScaledContents(True)
        self.setFixedSize(90, 90)
        pixmap = QPixmap(img_url)
        self.setPixmap(pixmap)

    def mousePressEvent(self, ev):
        lc = self.parent.text.textCursor()
        range_content = lc.selectedText()
        lc.insertText("__IMGX_" + str(self.index) + " " + range_content + " IMGX__")
