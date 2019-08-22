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
                      }
        self.invertedErrors = {
                        struct.pack("I", 0) : 'OK',
                        struct.pack("I", 1) : 'EOP NOT FOUND',
                        struct.pack("I", 2) : 'EOP IN PAYLOAD',
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