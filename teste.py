import struct 
from enlace import *
from server import *
from client import *
import time
import binascii
import threading
import io

nome = str(input("Client(C) ou Server(S)? "))

if(nome == "C"):
  client = Client()
  client.enable()
  client.getImage()
  client.disable()
else:
  server = Server()
  server.enable()
  txImageBufferLen, bitRate = server.sendImage('sendData.png')
  status, recieved = server.getResponse(txImageBufferLen)
  server.disable()
