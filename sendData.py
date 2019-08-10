
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

print("comecou")

from enlace import *
import time

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "/dev/tty.usbmodem14201" # Mac    (variacao de)
print("abriu com")

def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()
    bitStart = b'ok'
    with open('teste.png','rb') as image:
        txImageBuffer = bytearray(image.read())
        imageLen = len(txImageBuffer)
        imageLenBytes = bytes(len(txImageBuffer))

    sendData = imageLenBytes + bytes(":", 'utf-8') + txImageBuffer

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # rxBitStart, nBitStart = com.getData(len(bitStart))
    # print(rxBitStart, nBitStart)
    # if rxBitStart == bitStart:
    print('Sending image data')
    com.sendData(sendData)
    while(com.tx.getIsBussy()):
        pass
    
    # txLen = len(txBuffer)
    # print(txLen)

    # # Transmite dado
    # print("tentado transmitir .... {} bytes".format(txLen))
    # com.sendData(txBuffer)

    # # espera o fim da transmissão
    # #while(com.tx.getIsBussy()):
    # #    pass
    
    
    # # Atualiza dados da transmissão
    # txSize = com.tx.getStatus()
    # print ("Transmitido       {} bytes ".format(txSize))

    # # # Faz a recepção dos dados
    # # print ("Recebendo dados .... ")
    
    # # #repare que o tamanho da mensagem a ser lida é conhecida!     
    # # rxBuffer, nRx = com.getData(txLen)

    # # # log
    # # print ("Lido              {} bytes ".format(nRx))
    
    # # print (rxBuffer)
    # # with open('testeFeito.png', 'wb') as pedroimage:
    # #   pedroimage.write(rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
