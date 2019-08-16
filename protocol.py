import struct 

class Protocol:
    def __init__(self):
        self.head = None
        self.headSize = 8
        self.EOP = b'kjgpoiymf'
        self.stuffedEOP = b'1k2j3g4p5o6i7y8m9f0g'

    def createHead(self, lenght):
        self.head = b'0010' + struct.pack("I", lenght)

    def createBuffer(self, payload: bytes):
        payload = self.stuffPayload(payload)
        self.createHead(len(payload))
        buffer = self.head + payload + self.EOP
        return buffer

    def stuffPayload(self, payload):
        return payload.replace(self.EOP, self.stuffedEOP)

    def unStuffPayload(self, payload):
        return payload.replace(self.stuffedEOP, self.EOP)
    
    def readHead(self, head):
        lenData = struct.unpack("I",head[:4])
        x = str(head[4:].decode())
        return { "x": x, "lenghtData": lenData }

    def isEOPInPayload(self, payload):
        if payload.count(self.EOP > 0):
            print('EOP IN PAYLOAD')
            return True
        return False 
