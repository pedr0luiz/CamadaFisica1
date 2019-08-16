import struct 

class Protocol:
    def __init__(self):
        self.headSize = 8
        self.EOP = b'kjgpoiymf'
        self.stuffedEOP = b'1k2j3g4p5o6i7y8m9f0g'

    def createHead(self, lenght):
        print("CREATE HEAD")
        print(struct.pack("I", 0) + struct.pack("I", lenght))
        return struct.pack("I", 0) + struct.pack("I", lenght)

    def createBuffer(self, payload):
        payload = self.stuffPayload(payload)
        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        head = self.createHead(len(payload))
        buffer = head + payload + self.EOP
        return buffer

    def stuffPayload(self, payload):
        if self.EOP in payload:
            return payload.replace(self.EOP, self.stuffedEOP)
        return payload

    def unStuffPayload(self, payload):
        if self.stuffedEOP in payload:
            return payload.replace(self.stuffedEOP, self.EOP)
        return payload
    
    def readHead(self, head):
        print("READ HEAD")
        print(head)
        lenData = struct.unpack("I",head[:4])[0]
        x = struct.unpack("I",head[4:])[0]
        print(lenData, x)
        return { "x": x, "lenghtData": lenData }

    def isEOPInPayload(self, payload):
        if payload.count(self.EOP > 0):
            print('EOP IN PAYLOAD')
            return True
        return False 
