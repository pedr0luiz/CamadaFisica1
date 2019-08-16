from flask import Flask, render_template, redirect, url_for, session, request
from enlace import *
from server import *
from client import *
import asyncio
import atexit
import time
import binascii
import threading
import io

# Init app
app = Flask(__name__)

server = Server()
client = Client()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recebendo')
def RecieveData():
    client.enable()
    client.getImage()
    client.disable()
    return redirect(url_for('EndReciever'))

@app.route('/fim-receber')
def EndReciever():
    return render_template('transmission.html')

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

    server.enable()
    txImageBufferLen, bitRate = server.sendImage('sendData.png')
    status, recieved = server.getResponse(txImageBufferLen)
    server.disable()

    return render_template('verification.html', status=status, velocity=txImageBufferLen, send=txImageBufferLen, recieved=recieved)

if __name__ == '__main__':
    app.run(debug=True)
