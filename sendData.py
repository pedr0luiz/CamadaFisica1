
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

from enlace import *
import time

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "/dev/ttyACM0"  # Mac    (variacao de)

def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()
    bitStart = b'ok'
    with open('1055687.png','rb') as image:
        imageRead = image.read()
        #imageRead = imageRead.replace(b'\r', b'').replace(b'\n', b'')
        #txImageBuffer = bytearray(imageRead)

    print(imageRead)

    sendData = imageRead + b'end'

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("Porta : {}".format(com.fisica.name))
    print("-------------------------")

    # rxBitStart, nBitStart = com.getData(len(bitStart))
    # print(rxBitStart, nBitStart)
    # if rxBitStart == bitStart:
    print('Sending image data')
    com.sendData(sendData)
    while(com.tx.getIsBussy()):
        pass
        
    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    print ("Transmitido {} bytes ".format(txSize))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
