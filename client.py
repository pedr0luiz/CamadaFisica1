from enlace import *
from protocol import *
import time
import struct

class Client:
    def __init__(self, name="/dev/ttyACM0"):
        self.com = enlace("/dev/ttyACM0")
        self.protocol = Protocol()

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

    def readEOP(self):
        EOPBuffer = b''
        while self.protocol.EOP not in EOPBuffer and len(EOPBuffer) < len(self.protocol.EOP):
            dataEOP, lenEOP = self.com.getData(1)
            EOPBuffer += dataEOP
        if EOPBuffer == self.protocol.EOP:
            return True
        return False
    
    def response(self, lenRecieved, erro):
        buffer = self.protocol.createBuffer(struct.pack("I", lenRecieved), erro)
        self.com.sendData(buffer)
        while(self.com.tx.getIsBussy()):
            pass

    #Get Image
    def getImage(self):
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
        if(self.protocol.isEOPInPayload(dataBuffer)):
            #Enviar erro 
            print("EOP NO PAYLOAD")
            self.protocol.createBuffer(b'', 'EOP IN PAYLOAD')
            pass
        else:
            if(self.readEOP()):
                print('FOUND EOP')
                self.response(lenDataRecieved, 'OK')
                dataBuffer = self.protocol.unStuffPayload(dataBuffer)
                with open('newImage.txt','wb') as image:
                    image.write(dataBuffer)
            else:
                print('EOP NOT FOUND')
                self.protocol.createBuffer(b'', 'EOP NOT FOUND')
                #ERRROR
                pass 
    