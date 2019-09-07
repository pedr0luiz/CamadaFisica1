
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

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python3 -m serial.tools.list_ports

class Server:
    def __init__(self):
        self.serialName = "/dev/ttyACM0"
        self.com = enlace(self.serialName)
        self.protocol = Protocol()

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

    def sendImage(self, imageName):

        with open (imageName, 'rb') as imageData:
            payload = bytearray(imageData.read())

        buffer = self.protocol.createBuffer(payload, "ok", 0, 1, 'data' , self.protocol.clientId)

        print("---------------------------------------------------")
        print("OVERHEAD: {:.4f} ".format((len(buffer)/len(payload))))
        print("------------------------------------------------ \n")

        print('Sending image data')
        self.com.sendData(buffer)
        start = time.time()
        while(self.com.tx.getIsBussy()):
            pass
        end = time.time()

        bitRate = round(len(payload)/(end - start), 2)
        print("Transmitido {} bytes ".format(len(payload)))
        print('Taxa de transmição: {} bytes/segundo'.format(bitRate))

        return len(payload), bitRate

        #print('END APARECE: {} VEZ(ES)'.format(buffer.count(b'end')))

    def getResponse(self):
        #------------------------------------------#
        print("########################################")
        print("GETTING RESPONSE")
        print("########################################")
        #------------------------------------------#
        #Get Head
        headBuffer, lenHead = self.com.getData(self.protocol.headSize, 10)
        print('pegou head')
        print(headBuffer)
        #------------------------------------------#-----#
        #Separate Len from Head
        head = self.protocol.readHead(headBuffer)
        print('leu head')
        print(head)
        #------------------------------------------#
        #------------------------------------------#
        #Get Data
        if head:
            dataBuffer, lenDataRecieved = self.com.getData(head["lenghtData"], 10)
            #------------------------------------------#
            print("--------------------------------------->")
            print("PAYLOAD LEN: {}".format(lenDataRecieved))
            #------------------------------------------#
            print("--------------------------------------->")
            print("RESPONSE STATUS: ")
            print(head["error"])
            print("------------ --------------------------->")
            if(self.protocol.readEOP(self.com)):
                return True, head, lenDataRecieved
            else:
                return False, head, lenDataRecieved
        else:
            print("ELSE IF HEAD RESPOONSE")
            return False, False, 0

        

        
        # if(self.protocol.isEOPInPayload(dataBuffer)):
        #     #Enviar erro 
        #     pass
        # else:
        #     if(self.readEOP()):
        #         return size == lenDataRecieved, lenDataRecieved
        #     else:
        #         #ERRROR
        #         print('ERRO NA RESPONSE')
        #         pass 
    
    def sendPackages(self, totalBuffer):
        totalBuffer = self.protocol.stuffPayload(totalBuffer)
        packages = self.createPackages(totalBuffer)
        idx = 0
        while idx < len(packages):
            print("SENDING PACKAGE {}/{} \n".format(idx, len(packages)))
            self.com.sendData(packages[idx])
            while(self.com.tx.getIsBussy()):
                pass
            timer1 = time.time()
            timer2 = time.time()
            status, head, lenRecieved = self.getResponse()
            print(status, head, lenRecieved)
            print("###################################################")
            if(head):
                print("ENTROU HEAD")
                if(not status or head["error"] != 'ok' or head["msgType"] == 'dataError'):
                    idx = head['packageIdx']
                    print('RESENDING PACKAGE: {}'.format(idx))
                   
                else:
                    if(head['msgType'] == 'gotData'):
                        idx += 1
                    else:
                        if(timer1 - time.time() > 5):
                            self.com.sendData(packages[idx])
                            while(self.com.tx.getIsBussy()):
                                pass
                            timer1 = time.time()
                        if(timer2 - time.time() > 20):
                            packageType5 = self.protocol.createBuffer(b'', 'timeOut', 0, 1, 'timeOut', self.protocol.clientId)
                            self.com.sendData(packageType5)
                            while(self.com.tx.getIsBussy()):
                                pass
                            break;
                        else:
                            status, head, lenRecieved = self.getResponse()
                            if(head['error'] == 'ok'  and head['msgType'] == 'dataError'):
                                idx = head['packageIdx']
                            
                                
                                
                        



                        

    def createPackages(self, payload):
        numberOfPackages = math.ceil(len(payload)/self.protocol.payloadSize)
        packages = []
        for i in range(0, numberOfPackages):
            if((i+1) * self.protocol.payloadSize > len(payload)):
                packagePayload = payload[i*self.protocol.payloadSize :]
                print("LAST PACKAGE")
                print("LEN PAYLOAD: {}".format(len(packagePayload)))
                print("--------------------------------------->")
            else: 
                packagePayload = payload[i*self.protocol.payloadSize : (i+1) * self.protocol.payloadSize]
                print(" \n LEN PAYLOAD: {}".format(len(packagePayload)))
                print("--------------------------------------->")
                
            package = self.protocol.createBuffer(packagePayload, "ok", i, numberOfPackages, 'data', self.protocol.clientId)
            packages.append(package)
        return packages

    def initConnection(self):
        buffer = self.protocol.createBuffer(b'', 'ok', 1, 1, 'connect', self.protocol.serverId)
        self.com.sendData(buffer)
        while(self.com.tx.getIsBussy()):
            pass
        time.sleep(5)
        status, head, lenData = self.getResponse();
        if(status):
            print(head)
            if(head["target"] == self.protocol.clientId and head["msgType"] == 'connected'):
                return True
        return False