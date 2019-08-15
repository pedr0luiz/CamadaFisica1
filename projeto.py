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
    serialName = "/dev/ttyACM0"
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
    com.fisica.flush()
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
        with open ('sendData.png', 'wb') as imageData:
            imageData.write(image)
        return redirect(url_for('SendingData'))


@app.route("/mandando")
def SendingData():
    # image = request.args["image"].replace('%', '')
    # txImageBuffer = bytearray(image, encoding='utf-8').replace(b'%', b'')

    with open ('sendData.png', 'rb') as imageData:
        txImageBuffer = bytearray(imageData.read())

    serialName = "/dev/ttyACM0"
    com = enlace(serialName)
    com.enable()
    endBit = b'end'

    sendData = str(len(txImageBuffer)).encode() + endBit + txImageBuffer

    com.fisica.flush()

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
    # print("Transmitido {} bytes ".format(txSize))
    velocity = round(txSize/(end - start), 2)
    print('END APARECE: {} VEZ(ES)'.format(sendData.count(b'end')))
    print('Taxa de transmição: {} bytes/segundo'.format(velocity))

    print('Recieving data size')
    endDataTransfer = False
    dataBuffer = b''
    while not endDataTransfer:
        rxBuffer, nRxBuffer = com.getData(1)
        dataBuffer += rxBuffer
        if(endBit in dataBuffer):
            endDataTransfer = True

    lenBuffer = dataBuffer.split(b'end')[0]

    status = int(lenBuffer.decode()) == len(txImageBuffer)

    send = len(txImageBuffer)
    recieved = int(lenBuffer.decode())

    print("Received: {} bytes \n STATUS: {}".format(len(dataBuffer), status))

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    return render_template('verification.html', status=status, velocity=velocity, send=send, recieved=recieved)

if __name__ == '__main__':
    app.run(debug=True)
