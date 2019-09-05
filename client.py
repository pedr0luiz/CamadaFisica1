from enlace import *
from protocol import *
import time
import struct

class Client:
    def __init__(self, name="/dev/ttyACM0"):
        self.com = enlace("/dev/ttyACM0")
        self.protocol = Protocol()
        self.ocioso = True

    #Enable Com
    def enable(self):
        #------------------------------------------#
        print("########################################")
        print("ENABLE COM")
        print("########################################")
        #------------------------------------------#
        self.com.enable()
        #Flush Trash Bits
        self.com.fisica.flush()
    
    #Disable Com
    def disable(self):
        #------------------------------------------#
        print("########################################")
        print("DISABLE COM")
        print("########################################")
        #------------------------------------------#
        self.com.disable()

    #Get Image
    def getPackage(self):
        #------------------------------------------#
        print("########################################")
        print("INIT RECIEVER")
        print("########################################")
        #------------------------------------------#
        totalPackages = None
        packageIdx = 0
        payloadReceived = b''
        timer1 = time.time()
        timer2 = time.time()
        while totalPackages == None or packageIdx < totalPackages:
            headBuffer, lenHead = self.com.getData(self.protocol.headSize, 10)
            head = self.protocol.readHead(headBuffer)
            if head:
                totalPackages = head["packageTotal"]
                lenghtData = head["lenghtData"] 
                idxReceived = head["packageIdx"]
                print('HEAD LIDO: {}'.format(head)) 
                if head["error"] == 'ok' and head['msgType'] == 'data':
                    timer1 = time.time()
                    timer2 = time.time()
                    dataBuffer, lenDataRecieved = self.com.getData(lenghtData, 10)
                    dataBuffer = self.protocol.handlePackage(self.com, head, dataBuffer, self.protocol.serverId, False)
                    if(dataBuffer and packageIdx == idxReceived):
                        payloadReceived += dataBuffer
                        packageIdx += 1
                    else:
                        print('SENDING ERROR AND WAITING FOR PACKAGE: {}'.format(idxReceived))
                        self.protocol.response(self.com, lenghtData, 'idxError', head, 'dataError' , self.protocol.serverId)
                elif head["error"] == 'ok':
                    self.protocol.response(self.com, 0, 'typeError', {"packageTotal": totalPackages, "packageIdx": packageIdx}, 'gotData' , self.protocol.serverId)
                    actual = time.time()
                    if(actual - timer1 >= 20):
                        self.protocol.response(self.com, 0, 'timeOut', {"packageTotal": totalPackages, "packageIdx": packageIdx}, 'timeOut' , self.protocol.serverId)
                        self.ocioso = True
                        break
            else:
                actual = time.time()
                if(actual - timer2 >= 20):
                    self.protocol.response(self.com, 0, 'timeOut', {"packageTotal": totalPackages, "packageIdx": packageIdx}, 'timeOut' , self.protocol.serverId)
                    self.ocioso = True
                    break  
                print('SENDING ERROR AND WAITING')
                self.protocol.response(self.com, 0, 'headError', {"packageTotal": 0, "packageIdx": packageIdx}, 'dataError' , self.protocol.serverId)
        payloadReceived = self.protocol.unStuffPayload(payloadReceived)
        with open('teste.png', 'wb') as image:
            image.write(payloadReceived)
    
    def initConnection(self):
        packageIdx = 1
        headBuffer, lenHead = self.com.getData(self.protocol.headSize, 10)
        head = self.protocol.readHead(headBuffer)
        if head:
            totalPackages = head["packageTotal"]
            lenghtData = head["lenghtData"]
            idxReceived = head["packageIdx"]
            if head['error'] == 'ok':
                dataBuffer, lenDataRecieved = self.com.getData(lenghtData, 10)
                dataBuffer = self.protocol.handlePackage(self.com, head, dataBuffer, self.protocol.serverId, True)
            if((dataBuffer or dataBuffer == b'') and packageIdx == idxReceived and head['target'] == self.protocol.serverId and head['msgType'] == 'connect'):
                self.protocol.response(self.com, head['lenghtData'], 'ok', {'packageTotal': 1, 'packageIdx': 1}, 'connected', self.protocol.clientId)
                return False
        return True
  