from enlace import *
import time
import binascii

serialName = "/dev/cu.usbmodem14101"


def main():

    print("Init Reciever")
    com = enlace(serialName)
    com.enable()

    # repare que o tamanho da mensagem a ser lida é conhecida!
    connected = False
    bitStart = b'ok'
    # encoded = binascii.hexlify(bitStart)
    # print(encoded)
    # print(binascii.unhexlify(encoded))
    # # print(com.getData(len(bitStart)))

    # Start Connection
    # com.sendData(bitStart)
    # while(com.tx.getIsBussy()):
    #     pass

    # Recieve Data Len
    startImageGet = False
    lenImageTxt = b""
    while not startImageGet:
        rxBit, nBit = com.getData(1)
        lenImageTxt += rxBit
        if(b":" in lenImageTxt):
            startImageGet = True

    lenImage = lenImageTxt.split(b":")[0]
    print(len(binascii.hexlify(lenImage)))

    # rxImage, nxImage = com.getData()

    # with open('imagemRecebida.png', 'wb') as image:
    #     image.write(rxImage)

    # # log
    # print("Lido              {} bytes ".format(nRx))
    # print(rxBuffer)
    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()


if __name__ == "__main__":
    main()
