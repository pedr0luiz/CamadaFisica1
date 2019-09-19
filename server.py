
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

from enlace import *
from protocol import *
import time
import math
import datetime
import crc16

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python3 -m serial.tools.list_ports

class Server:
    def __init__(self):
        self.serialName = "/dev/ttyACM0"
        self.com = enlace(self.serialName)
        self.protocol = Protocol()
        self.crc = 0

    def enable(self):
        print("-------------------------")
        print("Comunicação inicializada")
        print("-------------------------")
        self.com.enable()
        #self.com.fisica.flush()

    def disable(self):
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        #self.com.fisica.flush()
        self.com.disable()

    def readEOP(self):
        EOPBuffer = b''
        while self.protocol.EOP not in EOPBuffer or len(EOPBuffer) < len(self.protocol.EOP):
            dataEOP, lenEOP = self.com.getData(1, 10)
            EOPBuffer += dataEOP
        if EOPBuffer == self.protocol.EOP:
            return True
        return False

    # def sendImage(self, imageName):

    #     with open (imageName, 'rb') as imageData:
    #         payload = bytearray(imageData.read())

    #     buffer = self.protocol.createBuffer(payload, "ok", 0, 1, 'data' , self.protocol.clientId)

    #     print("---------------------------------------------------")
    #     print("OVERHEAD: {:.4f} ".format((len(buffer)/len(payload))))
    #     print("------------------------------------------------ \n")

    #     self.com.sendData(buffer)
    #     start = time.time()
    #     while(self.com.tx.getIsBussy()):
    #         pass
    #     end = time.time()

    #     bitRate = round(len(payload)/(end - start), 2)
    #     print("Transmitido {} bytes ".format(len(payload)))
    #     print('Taxa de transmição: {} bytes/segundo'.format(bitRate))
    #     return len(payload), bitRate

    def getResponse(self):
        print("GETTING RESPONSE")
        headBuffer, lenHead = self.com.getData(self.protocol.headSize, 5)
        head = self.protocol.readHead(headBuffer)

        if head:
            dataBuffer, lenDataRecieved = self.com.getData(head["lenghtData"], 5)
            print("RESPONSE STATUS: {}".format(head["error"]))
            print("RESPONSE TYPE: {} \n".format(head["msgType"]))
            if(self.protocol.readEOP(self.com)):
                return True, head, lenDataRecieved
            else:
                return False, head, lenDataRecieved
        else:
            return False, False, 0
    
    def sendPackages(self, totalBuffer):
        totalBuffer = self.protocol.stuffPayload(totalBuffer)
        packages = self.createPackages(totalBuffer)
        idx = 0
        timer2 = time.time()
        while idx < len(packages):
            print("------------------------------------")
            print("SENDING PACKAGE {}/{}".format(idx, len(packages)))
            self.com.sendData(packages[idx])
            self.log({"msgType": "data", "target": self.protocol.serverId}, "sending")
            while(self.com.tx.getIsBussy()):
                pass
            timer1 = time.time()
            status, head, lenRecieved = self.getResponse()
            if head:
                self.log(head, "recieving")
                if(not status or head["error"] != 'ok' or head["msgType"] == 'dataError'):
                    idx = head['packageIdx']
                    print('RESENDING PACKAGE: {}'.format(idx))
                   
                else:
                    if(head['msgType'] == 'gotData'): 
                        timer2 = time.time()
                        idx += 1
                    else:
                        if(time.time() - timer2 > 20):
                            packageType5 = self.protocol.createBuffer(b'', 'timeOut', 0, 1, 'timeOut', self.protocol.clientId, self.crc)
                            self.com.sendData(packageType5)
                            self.log({"msgType": "timeOut", "target": self.protocol.serverId}, "sending")
                            while(self.com.tx.getIsBussy()):
                                pass
                            break
                        else:
                            status, head, lenRecieved = self.getResponse()
                            if head:
                                self.log(head, "sending")
                                if(head['error'] == 'ok'  and head['msgType'] == 'dataError'):
                                    timer2 = time.time()
                                    idx = head['packageIdx']
            else:
                if(time.time() - timer2 > 20):
                    print("TimeOut Timer 2 (20sec)")
                    packageType5 = self.protocol.createBuffer(b'', 'timeOut', 0, 1, 'timeOut', self.protocol.clientId, self.crc)
                    self.com.sendData(packageType5)
                    self.log({"msgType": "timeOut", "target": self.protocol.serverId}, "sending")
                    while(self.com.tx.getIsBussy()):
                        pass
                    break
                            
    def createPackages(self, payload):
        numberOfPackages = math.ceil(len(payload)/self.protocol.payloadSize)
        self.crc = crc16.crc16xmodem(payload)
        print('CRC: {}'.format(self.crc))
        packages = []
        for i in range(0, numberOfPackages):
            if((i+1) * self.protocol.payloadSize > len(payload)):
                packagePayload = payload[i*self.protocol.payloadSize :]
            else: 
                packagePayload = payload[i*self.protocol.payloadSize : (i+1) * self.protocol.payloadSize]
                
            package = self.protocol.createBuffer(packagePayload, "ok", i, numberOfPackages, 'data', self.protocol.clientId, self.crc)
            packages.append(package)
        return packages

    def initConnection(self):
        buffer = self.protocol.createBuffer(b'', 'ok', 1, 1, 'connect', self.protocol.serverId, self.crc)
        self.com.sendData(buffer)
        self.log({"msgType": "connect", "target": self.protocol.serverId}, "sending")
        while(self.com.tx.getIsBussy()): 
            pass
        time.sleep(5)
        status, head, lenData = self.getResponse()
        if(status):
            self.log(head, "recieving")
            if(head["target"] == self.protocol.clientId and head["msgType"] == 'connected'):
                return True
        return False

    def log(self,head,action):
        agora = datetime.datetime.now().time()
        if action == 'sending':
            text = "<{}> - Enviada: {} - Destinatario: {}\n".format(head['msgType'], agora, head['target'])
        else:
            text = "<{}> - Recebida: {} - Remetente: {}\n".format(head['msgType'], agora, self.protocol.serverId)#head['target'])

        with open("Client_Log.txt", "a") as clientLog:
            clientLog.write(text)
