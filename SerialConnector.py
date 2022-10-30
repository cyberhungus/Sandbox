
import serial 

from threading import Thread 
from time import sleep
import sys


class SerialConnector:
    def __init__(self,port='COM17',baud=2000000, ):
        self.port = port
        self.baud = baud
        self.serialStarted = False
        self.ser = None
    
    def getAvailableComPorts(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def openSerialByName(self, port):
        try:
            self.port = port
            self.openSerialPort()
            return True
        except Exception as ex:
            print(ex)
            return False



    #create serial connection 
    def openSerialPort(self):

        self.ser = serial.Serial(self.port, self.baud,timeout=2)
        self.serialStarted = True
        self.readThread = Thread(target=self.receive)
        self.readThread.start()

    def receive(self):
        while 1:
            
            bytes = self.ser.read(self.ser.inWaiting())
            if len(bytes)>0:
                print("Arduino is sending:", bytes)
            sleep(0.01)

    def send(self, msg):
        try:
            #you know the drill, this is for opening serial in new thread 
            if self.serialStarted==False:
                self.openSerialPort()
                sleep(0.1)
            #the message needs to be in this format to be recognizable to the arduino 
            # then actually send the message to the arduino 
            
            message = "<"+msg+">"
            self.ser.write(bytes(message,"ASCII"))
        except Exception as ex:
            print("SerialConnector:" , ex)

    def sendLightMessage(self, lednum, red, green, blue):
        try:
            #you know the drill, this is for opening serial in new thread 
            if self.serialStarted==False:
                self.openSerialPort()
                sleep(0.1)
            #the message needs to be in this format to be recognizable to the arduino 
            # then actually send the message to the arduino 
            message = str("{0:03}".format(red))+"-"+str("{0:03}".format(green))+"-"+str("{0:03}".format(blue))+"-"+str("{0:03}".format(lednum))
            self.ser.write(bytes(message,"ASCII"))
        except Exception as ex:
            print("SerialConnector:" , ex)


