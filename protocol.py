import struct 
import datetime

class Protocol:
    def __init__(self):
        self.headSize = 16
        self.EOP = b'kjgp'
        self.stuffedEOP = b'iopg'
        self.errors = {
                        'ok': struct.pack("I", 0),
                        'EOPNotFound': struct.pack("I", 1),
                        'EOPInPayload': struct.pack("I", 2),
                        'payloadLenght': struct.pack("I", 3),
                        'idxError': struct.pack("I", 4),
                        'headError': struct.pack("I", 5),
                        'typeError': struct.pack("I", 6),
                        'timeOut': struct.pack("I", 7)
                      }
        self.invertedErrors = {
                        struct.pack("I", 0): 'ok',
                        struct.pack("I", 1): 'EOPNotFound',
                        struct.pack("I", 2): 'EOPInPayload',
                        struct.pack("I", 3): 'payloadLenght',
                        struct.pack("I", 4): 'idxError',
                        struct.pack("I", 5): 'headError',
                        struct.pack("I", 6): 'typeError',
                        struct.pack("I", 7): 'timeOut'
                      }
        self.types = {
                        'connect': int(1).to_bytes(1, byteorder="little"),
                        'connected': int(2).to_bytes(1, byteorder="little"),
                        'data': int(3).to_bytes(1, byteorder="little"),
                        'gotData': int(4).to_bytes(1, byteorder="little"),
                        'timeOut': int(5).to_bytes(1, byteorder="little"),
                        'dataError': int(6).to_bytes(1, byteorder="little")
                      }
        self.invertedTypes = {
                        int(1).to_bytes(1, byteorder="little"): 'connect',
                        int(2).to_bytes(1, byteorder="little"): 'connected',
                        int(3).to_bytes(1, byteorder="little"): 'data',
                        int(4).to_bytes(1, byteorder="little"): 'gotData',
                        int(5).to_bytes(1, byteorder="little"): 'timeOut',
                        int(6).to_bytes(1, byteorder="little"): 'dataError' 
                      }
        self.payloadSize = 128
        self.clientId = 1
        self.serverId = 2

    def createHead(self, lenght, error, idxPackage, numberOfPackages, msgType, target, crc):
        crc = crc.to_bytes(2, byteorder="little")
        total = numberOfPackages.to_bytes(2, byteorder="little") 
        index = idxPackage.to_bytes(2, byteorder="little")
        erro = self.errors[error]
        size = struct.pack("I", lenght)
        msgType = self.types[msgType]
        target = target.to_bytes(1, byteorder="little")
        return target + msgType + erro + total + index + size + crc

    def createBuffer(self, payload, erro, idxPackage, numberOfPackages, msgType, target, crc):
        head = self.createHead(len(payload), erro, idxPackage, numberOfPackages, msgType, target, crc)
        buffer = head + payload  + self.EOP
        return buffer

    def stuffPayload(self, payload):
        return payload.replace(self.EOP, self.stuffedEOP)

    def unStuffPayload(self, payload):
        return payload.replace(self.stuffedEOP, self.EOP)

    def readHead(self, head):
        if len(head) == self.headSize:
            lenData = struct.unpack("I",head[10:14])[0]
            erro = head[2:6]
            try:
                msgType = self.invertedTypes[head[1:2]]
                target = int.from_bytes(head[0:1], byteorder="little")
                packageIdx = int.from_bytes(head[8 : 10], byteorder="little")
                packageTotal = int.from_bytes(head[6 : 8], byteorder="little")
                crc = int.from_bytes(head[14:16], byteorder="little")
                return { "error": self.invertedErrors[erro], 
                        "lenghtData": lenData, 
                        "packageIdx": packageIdx, 
                        "packageTotal": packageTotal,
                        "msgType": msgType,
                        "target": target,
                        "crc": crc
                    }
            except:
                return False
        else:
            return False

    def isEOPInPayload(self, payload):
        if payload.count(self.EOP) > 0:
            print('{} EOP IN PAYLOAD'.format(payload.count(self.EOP)))
            print('EOP IN BYTE: {}'.format(payload.index(self.EOP) + self.headSize))
            return True
        return False  
    
    def log(self, head, action):
        with open('Server_Log.txt', 'a') as serverLog:
            agora = datetime.datetime.now().time()
            if action == 'sending':
                text = "<{}> - Enviada: {} - Destinatario: {}\n".format(head['msgType'], agora, self.clientId)#head['target'])
            else:
                text = "<{}> - Recebida: {} - Remetente: {}\n".format(head['msgType'], agora, self.clientId)#head['target'])
            serverLog.write(text)

    def response(self, com, lenRecieved, erro, head, msgType, target):
        totalPackages = head["packageTotal"]
        idxReceived = head["packageIdx"]
        buffer = self.createBuffer(struct.pack("I", lenRecieved), erro, idxReceived, totalPackages, msgType, target, 0)
        com.sendData(buffer)
        self.log({'msgType': msgType, 'target': target}, 'sending')

        while(com.tx.getIsBussy()):
            pass

    def readEOP(self, com):
        EOPBuffer = b''
        while self.EOP not in EOPBuffer and len(EOPBuffer) < len(self.EOP):
            dataEOP, lenEOP = com.getData(1, 10)
            EOPBuffer += dataEOP
        if EOPBuffer == self.EOP:
            return True
        return False

    def handlePackage(self, com, head, dataBuffer, target, connecting, actualIdx):
        lenDataRecieved = len(dataBuffer)
        lenghtData = head["lenghtData"]
        if lenghtData == lenDataRecieved:
            if(self.isEOPInPayload(dataBuffer)):
                #Enviar erro 
                print("EOP NO PAYLOAD")
                print('Sending ERROR')
                self.response(com, lenDataRecieved, 'EOPInPayload', head, 'dataError', target)
                return False
            else: 
                if(self.readEOP(com)):
                    print('FOUND EOP at byte {}'.format(self.headSize + lenDataRecieved))
                    if not connecting:
                        packageIdx = head["packageIdx"]
                        if actualIdx == packageIdx:
                            print("SENDING RESPONSE PACKAGE: {}".format(head["packageIdx"]))
                            print('----------------------------------------------------------\n')
                            self.response(com, lenDataRecieved, 'ok', head, 'gotData', target)
                        else:
                            print('SENDING ERROR AND WAITING FOR PACKAGE: {} \n'.format(actualIdx))
                            self.response(com, lenghtData, 'idxError', {'packageTotal':head["packageTotal"], 'packageIdx': actualIdx}, 'dataError' , self.serverId)
                            return False
                    return dataBuffer
                else:
                    print('EOP NOT FOUND')
                    print('Sending ERROR')
                    print('----------------------------------------------------------\n')
                    self.response(com, lenDataRecieved, 'EOPNotFound', head, 'dataError', target)
                    return False
                    #ERRROR
        else:
            print('ERROR PAYLOAD LENGHT')
            print('Sending ERROR')
            print('----------------------------------------------------------\n')
            self.response(com, lenDataRecieved, 'payloadLenght', head, 'dataError', target)
            return False
            #ERRO
    
