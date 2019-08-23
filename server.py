
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
            dataEOP, lenEOP = self.com.getData(1)
            EOPBuffer += dataEOP
        if EOPBuffer == self.protocol.EOP:
            return True
        return False

    def sendImage(self, imageName):

        with open (imageName, 'rb') as imageData:
            payload = bytearray(imageData.read())

        buffer = self.protocol.createBuffer(payload, "OK", 0, 1)

        print("-----------------------------------------------")
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

    def getResponse(self, size):
        #------------------------------------------#
        print("########################################")
        print("INIT RECIEVER")
        print("########################################")
        #------------------------------------------#
        #Get Head
        headBuffer, lenHead = self.com.getData(self.protocol.headSize)
        #------------------------------------------#
        print("--------------------------------------->")
        print("HEAD: {}".format(headBuffer))
        #------------------------------------------#
        #Separate Len from Head
        head = self.protocol.readHead(headBuffer)
        #------------------------------------------#
        print("--------------------------------------->")
        print("IMAGE LEN: {}".format(head["lenghtData"]))
        #------------------------------------------#
        #Get Data
        dataBuffer, lenDataRecieved = self.com.getData(head["lenghtData"])
        #------------------------------------------#
        print("--------------------------------------->")
        print("PAYLOAD LEN: {}".format(lenDataRecieved))
        #------------------------------------------#
        print("-----------------------------------------------------------")
        print("RESPONSE STATUS: ")
        print(head["error"])
        print("-----------------------------------------------------------")

        return head["error"], lenDataRecieved
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
        packages = self.createPackages(totalBuffer)
        for pk in packages:
            self.com.sendData(pk)
            while(self.com.tx.getIsBussy()):
                pass
            error, lenRecieved = self.getResponse(self.protocol.payloadSize)
            print("-------------------------------------")
            print(error)
            print("-------------------------------------")
            if(error != "OK"):
                print("################################## \n")
                print("Error in package")
                print("################################### \n")
                break;

    def createPackages(self, payload):
        numberOfPackages = math.ceil(len(payload)/self.protocol.payloadSize)
        packages = []
        for i in range(0, numberOfPackages - 1):
            if((i+1) * self.protocol.payloadSize > len(payload)):
                packagePayload = payload[i*self.protocol.payloadSize :]
                print("LAST PACKAGE")
                print("LEN PAYLOAD: {}".format(len(packagePayload)))
                print("----------------->")
            else:
                
                packagePayload = payload[i*self.protocol.payloadSize : (i+1) * self.protocol.payloadSize]
                print("LEN PAYLOAD: {}".format(len(packagePayload)))
                print("----------------->")
            package = self.protocol.createBuffer(packagePayload, "OK", i, numberOfPackages)
            packages.append(package)
        return packages



