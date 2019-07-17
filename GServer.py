import socket
import GSyntax

from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from subprocess import Popen, PIPE

HOST = '0.0.0.0'
PORT = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def getServerWidget(title):
#	if serverWidget is not None:
#		return serverWidget
	
	tries = 0
	stdout = b''
	while stdout == b'':
		sleep(1)
		if tries == 10:
			raise Exception("Servidor Xephyr não encontrado!")
		tries += 1
		p1 = Popen(["xwininfo", "-name", title], stdout=PIPE)
		p2 = Popen(["grep", "-o", "-E", "0x[0-9a-fA-F]+"], stdin=p1.stdout, stdout=PIPE)
		stdout = p2.communicate()[0]
		
	stdout = stdout.splitlines()[0]
	winId = int(stdout, 16)
	new_window = QtGui.QWindow.fromWinId(winId)
	new_window.setFlags(Qt.FramelessWindowHint);
	
	game_widget = QtWidgets.QWidget.createWindowContainer(new_window)
	serverWidget = QtWidgets.QGraphicsView()
	
	game_box = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, serverWidget)
	game_box.addWidget(game_widget)
	
	return serverWidget

def startCommunication():
	try:
		print("Connectando em %s %d" % (HOST, PORT))
		sock.connect((HOST, PORT))
	except:
		print("Servidor não encontrado")
	
def send(text):
	text = GSyntax.cleanText(text)
	blocks = GSyntax.getCommandBlocks(text)
	#try:
	i = 0
	for msg in blocks:
		i += 1
		print(str(i) + ":", end="")
		print(msg)
		sock.send(msg.encode('utf-8'))
		sock.recv(2048)
	#except:
	#	print("Não há conexação com o servidor")
