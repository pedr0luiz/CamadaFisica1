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
        while totalPackages == None or packageIdx < totalPackages:
            headBuffer, lenHead = self.com.getData(self.protocol.headSize)
            head = self.protocol.readHead(headBuffer)
            if head:
                totalPackages = head["packageTotal"]
                lenghtData = head["lenghtData"]
                idxReceived = head["packageIdx"]
                print('HEAD LIDO: {}'.format(head))
                if head["error"] == 'ok':
                    dataBuffer, lenDataRecieved = self.com.getData(lenghtData)
                    dataBuffer = self.protocol.handlePackage(self.com, head, dataBuffer)
                    if(dataBuffer and packageIdx == idxReceived):
                        payloadReceived += dataBuffer
                        packageIdx += 1
                    else:
                        print('SENDING ERROR AND WAITING FOR PACKAGE: {}'.format(idxReceived))
                        self.protocol.response(self.com, lenghtData, 'idxError', head)
            else:
                self.protocol.response(self.com, 0, 'headError', {"packageTotal": 0, "packageIdx": packageIdx})
        payloadReceived = self.protocol.unStuffPayload(payloadReceived)
        with open('teste.png', 'wb') as image:
            image.write(payloadReceived)
    