import socket
import GSyntax
import threading

from os import environ
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QProcess
from subprocess import Popen, PIPE, run

HOST = '0.0.0.0'
PORT = 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Inicia o display virtual Xephyr em um widget
def getServerWidget(process, title):
	process.start("Xephyr -ac -br -reset -terminate -screen 640x480 :100 -title " + title)
	tries = 0
	stdout = b''
	
	# Espera inicialização do Xephyr e
	# extrai o winId da janela do display virtual
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
	
	# FramelessWindow permite "colar" a janela do servidor na janela do editor
	new_window.setFlags(Qt.FramelessWindowHint)
	
	game_widget = QtWidgets.QWidget.createWindowContainer(new_window)
	
	# O widget que recebe o vídeo deve ser algum widget que tenha
	# informações visuais, como o textEdit ou o graphicsView
	serverWidget = QtWidgets.QGraphicsView()
	
	# De fato "cola" a janela do servidor dentro de um widget
	game_box = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, serverWidget)
	game_box.addWidget(game_widget)
	
	return serverWidget


# Avatar precisa de uma thread
def startGameThread():
	print("Iniciando o avatar")
	run(["./unityVideo/videoCreator.x86_64", "teste_renderer", "1", "30", "32", "37", "-screen-fullscreen", "0", "-screen-quality", "Fantastic", "-force-opengl", "2>&1", "/dev/null", "&"], shell=False, env=dict(environ, DISPLAY=":100"))

# Thread do avatar
game = threading.Thread(target=startGameThread)

def startCommunication():
	if not game.is_alive():
		game.start()
	tries = 0
	while tries < 5:
		sleep(3)
		try:
			print("Connectando em %s %d" % (HOST, PORT))
			sock.connect((HOST, PORT))
			tries += 5
		except:
			print("Servidor não encontrado")		
		tries += 1
	
def send(text):
	text = GSyntax.cleanText(text)
	blocks = GSyntax.getCommandBlocks(text)
	#try:
	i = 0
	for msg in blocks:
		i += 1
		print("MESSAGE:")
		print(str(i) + ":", end="")
		print(msg.encode('utf-8'))
		print(sock.send(msg.encode('utf-8')))
		sock.recv(2048)
	#except:
	#	print("Não há conexação com o servidor")
