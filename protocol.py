import struct 

class Protocol:
    def __init__(self):
        self.headSize = 12
        self.EOP = b'kjgpoiymf'
        self.stuffedEOP = b'1k2j3g4p5o6i7y8m9f0g'
        self.errors = {
                        'ok': struct.pack("I", 0),
                        'EOPNotFound': struct.pack("I", 1),
                        'EOPInPayload': struct.pack("I", 2),
                        'payloadLenght': struct.pack("I", 3),
                        'idxError': struct.pack("I", 4),
                        'headError': struct.pack("I", 5)
                      }
        self.invertedErrors = {
                        struct.pack("I", 0): 'ok',
                        struct.pack("I", 1): 'EOPNotFound',
                        struct.pack("I", 2): 'EOPInPayload',
                        struct.pack("I", 3): 'PayloadLenght',
                        struct.pack("I", 4): 'idxError',
                        struct.pack("I", 5): 'headError'  
                      }
        self.payloadSize = 128

    def createHead(self, lenght, error, idxPackage, numberOfPackages):
        print("CREATE HEAD")
        print(struct.pack("I", 0) + struct.pack("I", lenght))
        total = numberOfPackages.to_bytes(2, byteorder="little") 
        index = idxPackage.to_bytes(2, byteorder="little")
        erro = self.errors[error]
        size = struct.pack("I", lenght)
        print(erro)
        print(total)
        print(index)
        print(size)
        return  erro + total + index + size

    def createBuffer(self, payload, erro, idxPackage, numberOfPackages):
        payload = self.stuffPayload(payload)
        head = self.createHead(len(payload), erro, idxPackage, numberOfPackages)
        buffer = head + payload  + self.EOP
        print(buffer.count(self.EOP))
        return buffer

    def stuffPayload(self, payload):
        return payload.replace(self.EOP, self.stuffedEOP)

    def unStuffPayload(self, payload):
        return payload.replace(self.stuffedEOP, self.EOP)

    def readHead(self, head):
        print("READ HEAD")
        if len(head) == self.headSize:
            lenData = struct.unpack("I",head[-4:])[0]
            erro = head[:4]
            packageIdx = int.from_bytes(head[6 : 8], byteorder="little")
            packageTotal = int.from_bytes(head[4 : 6], byteorder="little")
            return { "error": self.invertedErrors[erro], "lenghtData": lenData, "packageIdx": packageIdx, "packageTotal": packageTotal }
        else:
            return False

    def isEOPInPayload(self, payload):
        if payload.count(self.EOP) > 0:
            print('{} EOP IN PAYLOAD'.format(payload.count(self.EOP)))
            print('EOP IN BYTE: {}'.format(payload.index(self.EOP) + self.headSize))
            return True
        return False 

    def response(self, com, lenRecieved, erro, head):
        totalPackages = head["packageTotal"]
        idxReceived = head["packageIdx"]
        buffer = self.createBuffer(struct.pack("I", lenRecieved), erro, idxReceived, totalPackages)
        com.sendData(buffer)
        while(com.tx.getIsBussy()):
            pass

    def readEOP(self, com):
        EOPBuffer = b''
        while self.EOP not in EOPBuffer and len(EOPBuffer) < len(self.EOP):
            dataEOP, lenEOP = com.getData(1)
            EOPBuffer += dataEOP
        if EOPBuffer == self.EOP:
            return True
        return False

    def handlePackage(self, com, head, dataBuffer):
        lenDataRecieved = len(dataBuffer)
        lenghtData = head["lenghtData"]
        if lenghtData == lenDataRecieved:
            if(self.isEOPInPayload(dataBuffer)):
                #Enviar erro 
                print("EOP NO PAYLOAD")
                print('Sending ERROR')
                self.response(com, lenDataRecieved, 'EOPInPayload', head)
                return False
            else:
                if(self.readEOP(com)):
                    print('FOUND EOP at byte {}'.format(self.headSize + lenDataRecieved))
                    self.response(com, lenDataRecieved, 'ok', head)
                    dataBuffer = self.unStuffPayload(dataBuffer)
                    return dataBuffer
                else:
                    print('EOP NOT FOUND')
                    print('Sending ERROR')
                    self.response(com, lenDataRecieved, 'EOPNotFound', head)
                    return False
                    #ERRROR
        else:
            print('ERROR PAYLOAD LENGHT')
            print('Sending ERROR')
            self.response(com, lenDataRecieved, 'PayloadLenght', head)
            return False
            #ERRO
    
