from flask import Flask, render_template, redirect, url_for, session, request
from enlace import *
import asyncio
import atexit
import time
import binascii
import threading
import io

# Init app
app = Flask(__name__)

# Protocol Vars
Start = False
rxBuffer = b""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recebendo')
def RecieveData():
    serialName = "/dev/cu.usbmodem1421"
    com = enlace(serialName)
    com.enable()
    GotType = False
    GotData = False
    rxBuffer = b""
    fileType = ""
    data = b''
    # while not(GotType):
    #     tempBuffer, nBuffer = com.getData(1)
    #     rxBuffer += tempBuffer
    #     if(b"&" in rxBuffer):
    #         fileType = rxBuffer.replace(b"&", "").decode("hex")
    #         print(fileType)
    #         rxBuffer = b""
    #         GotType = True
    # com.sendData(b"&&")
    # render_template('transmission.html', type=fileType)
    # while(com.tx.getIsBussy()):
    #     pass
    # render_template('transmission.html', type=fileType, getData=True)
    while not(GotData):
        tempBuffer, nBuffer = com.getData(1)
        rxBuffer += tempBuffer
        if(b'end' in rxBuffer):
            print("---------------------------")
            print("Size: {}".format(len(rxBuffer)))
            print("---------------------------")
            GotData = True
            data = rxBuffer.split(b'end')[0]
            with open('./static/images/imgFlask.png', 'wb') as image:
                image.write(data)
    print("SENDING RESPONSE")
    print("-----------------------")
    com.sendData(bytes(len(data))+b'end')
    while(com.tx.getIsBussy()):
        pass
    return redirect(url_for('index'))


@app.route('/selecionar-arquivo', methods=["GET", "POST"])
def SelectFile():
    if(request.method == "GET"):
        return render_template('select-file.html')
    elif(request.method == "POST"):
        image = request.files["fileName"]
        image = image.read()

        return redirect(url_for('SendingData', image=image))


@app.route("/mandando")
def SendingData():
    image = request.args["image"]
    txImageBuffer = bytearray(image, encoding='utf-8')

    serialName = "/dev/cu.usbmodem14201"
    com = enlace(serialName)
    com.enable()
    bitStart = b'ok'
    endBit = b'end'

    sendData = txImageBuffer + endBit

    print("-------------------------")
    print("Comunicação inicializada")
    print("Porta : {}".format(com.fisica.name))
    print("-------------------------")

    # rxBitStart, nBitStart = com.getData(len(bitStart))
    # print(rxBitStart, nBitStart)
    # if rxBitStart == bitStart:
    print('Sending image data')
    com.sendData(sendData)
    start = time.time()
    while(com.tx.getIsBussy()):
        pass
    end = time.time()

    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    print("Transmitido {} bytes ".format(txSize))
    print('Taxa de transmição: {} bytes/segundo'.format(round(txSize/(end - start), 2)))

    print('Recieving data size')
    endDataTransfer = False
    dataBuffer = b''
    while not endDataTransfer:
        rxBuffer, nRxBuffer = com.getData(1)
        dataBuffer += rxBuffer
        if(endBit in dataBuffer):
            endDataTransfer = True

    success = len(dataBuffer) == txSize

    print("Received: {} bytes \n STATUS: {}".format(len(dataBuffer), success))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    return render_template('select-file.html', success=success)


if __name__ == '__main__':
    app.run(debug=True)
