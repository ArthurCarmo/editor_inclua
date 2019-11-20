import sys
from PyQt5 import QtWidgets

QtWidgets.QApplication(sys.argv)
QtWidgets.QFileDialog().getOpenFileName(caption="Abrir documento", filter="Documentos (*.pdf *.odt *.doc *.docx *.ppt *.pptx *.rtf *.pps *.ppsx *.odp);; Todos os arquivos (*.*)")