from enlace import *
import time
import binascii

serialName = "/dev/cu.usbmodem14401"


def main():

    print("Init Reciever")
    print("----------------------------")
    com = enlace(serialName)
    com.enable()

    # Variaveis Iniciais
    connected = False
    bitStart = b'ok'

    # Recieve Data Len
    endDataTransfer = False
    dataBuffer = b''
    while not endDataTransfer:
        rxBuffer, nRxBuffer = com.getData(1)
        dataBuffer += rxBuffer
        if(b'end' in dataBuffer):
            endDataTransfer = True

    print("Received: {}bits".format(len(dataBuffer)))
    dataBuffer = dataBuffer.split(b'end')[0]
    with open('teste2.png', 'wb') as image:
        image.write(dataBuffer)

    # Fim da transferencia
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()


if __name__ == "__main__":
    main()
