import struct 

class Protocol:
    def __init__(self):
        self.headSize = 8
        self.EOP = b'kjgpoiymf'
        self.stuffedEOP = b'1k2j3g4p5o6i7y8m9f0g'
        self.errors = {
                        'OK': struct.pack("I", 0),
                        'EOP NOT FOUND': struct.pack("I", 1),
                        'EOP IN PAYLOAD': struct.pack("I", 2),
                        'PAYLOAD LENGHT': struct.pack("I", 3)
                      }
        self.invertedErrors = {
                        struct.pack("I", 0): 'OK',
                        struct.pack("I", 1): 'EOP NOT FOUND',
                        struct.pack("I", 2): 'EOP IN PAYLOAD',
                        struct.pack("I", 3): 'PAYLOAD LENGHT' 
                      }

    def createHead(self, lenght, erro):
        print("CREATE HEAD")
        print(struct.pack("I", 0) + struct.pack("I", lenght))
        return self.errors[erro] + struct.pack("I", lenght)

    def createBuffer(self, payload, erro):
        payload = self.stuffPayload(payload) + self.EOP
        head = self.createHead(len(payload ), erro)
        buffer = head + payload  + self.EOP
        return buffer

    def stuffPayload(self, payload):
        return payload.replace(self.EOP, self.stuffedEOP)

    def unStuffPayload(self, payload):
        return payload.replace(self.stuffedEOP, self.EOP)

    def readHead(self, head):
        print("READ HEAD")
        print(head)
        lenData = struct.unpack("I",head[4:])[0]
        erro = struct.unpack("I",head[:4])[0]
        print(lenData, head[:4])
        return { "error": head[:4], "lenghtData": lenData }

    def isEOPInPayload(self, payload):
        if payload.count(self.EOP) > 0:
            print('{} EOP IN PAYLOAD'.format(payload.count(self.EOP)))
            print('EOP IN BYTE: {}'.format(payload.index(self.EOP) + self.headSize))
            return True
        return False 

    def response(self, com, lenRecieved, erro):
        buffer = self.createBuffer(struct.pack("I", lenRecieved), erro)
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

    def handlePackage(self, com, lenghtData, dataBuffer):
        lenDataRecieved = len(dataBuffer)
        if lenghtData == lenDataRecieved:
            if(self.isEOPInPayload(dataBuffer)):
                #Enviar erro 
                print("EOP NO PAYLOAD")
                print('Sending ERROR')
                self.response(com, lenDataRecieved, 'EOP IN PAYLOAD')
                return False
            else:
                if(self.readEOP(com)):
                    print('FOUND EOP at byte {}'.format(self.headSize + lenDataRecieved))
                    self.response(com, lenDataRecieved, 'OK')
                    dataBuffer = self.unStuffPayload(dataBuffer)
                    with open('newImage.png','wb') as image:
                        image.write(dataBuffer)
                    return True
                else:
                    print('EOP NOT FOUND')
                    print('Sending ERROR')
                    self.response(com, lenDataRecieved, 'EOP NOT FOUND')
                    return False
                    #ERRROR
        else:
            print('ERROR PAYLOAD LENGHT')
            print('Sending ERROR')
            self.response(com, lenDataRecieved, 'PAYLOAD LENGHT')
            return False
            #ERRO