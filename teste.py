import struct 
from enlace import *
from server import *
from client import *
import time
import binascii
import threading
import io
from tkinter import Tk
from tkinter.filedialog import askopenfilename

nome = str(input("Client(C) ou Server(S)? "))

if(nome == "C"):
  client = Client(name="/dev/cu.usbmodem14101")
  with open('Server_Log.txt', 'w') as serverLog:
    serverLog.write('INICIALIZANDO:\n')
  client.enable()
  while client.ocioso:
    client.ocioso = client.initConnection()
    time.sleep(1)
  client.getPackage()
  client.disable()
else:
  Tk().withdraw()
  filePath = askopenfilename()
  server = Server()
  server.enable()
  with open(filePath, 'rb') as image:
    imageBytes = image.read()
  inicia = False
  with open('Client_Log.txt', 'w') as clientLog:
    clientLog.write('INICIALIZANDO: \n')
  while(not inicia):
    inicia = server.initConnection()
  print("START SENDING PACKAGES")
  timer = time.time()
  server.sendPackages(imageBytes)
  TotalTime = time.time() - timer
  print("\n Throughput: {}".format(len(imageBytes)/TotalTime))
  server.disable()