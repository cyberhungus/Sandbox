
from serial import Serial, tools , SerialException

from threading import Thread 
from time import sleep
import sys


class SerialConnector:
    def __init__(self,port='COM9',baud=115200):
        self.port = port
        self.baud = baud
        self.serialStarted = False
        self.ser = None
        
    
    def getAvailableComPorts(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]

        result = []
        for port in ports:
            try:
                s = Serial(port)
                s.close()
                result.append(port)
            except (OSError, SerialException):
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

        self.ser = Serial(self.port, self.baud,timeout=2)
        self.serialStarted = True
        self.readThread = Thread(target=self.receive)
        self.readThread.start()

    def receive(self):
        while 1 and self.serialStarted == True:
            try:
                bytes = self.ser.read(self.ser.inWaiting())
                if len(bytes)>0:
                    pass
                    #print("Arduino is sending:", bytes)
                sleep(0.01)
            except:
                self.serialStarted = False
                self.ser.close()
                
                print("Exception with serial port")

    def send(self, msg):
        try:
            if self.serialStarted==False:
                self.openSerialPort()
                sleep(0.1)
            
            message = "<"+msg+">"
            self.ser.write(bytes(message,"ASCII"))
        except Exception as ex:
            print("SerialConnector:" , ex)
            self.serialStarted = False
            self.ser.close()
    def sendLightMessage(self, lednum, red, green, blue):
        try: 
            if self.serialStarted==False:
                self.openSerialPort()
                sleep(0.1)
            message ="<"+ str("{0:03}".format(red))+"-"+str("{0:03}".format(green))+"-"+str("{0:03}".format(blue))+"-"+str("{0:03}".format(lednum))+">"
            self.ser.write(bytes(message,"ASCII"))
        except Exception as ex:
            print("SerialConnector:" , ex)
            self.serialStarted = False
            self.ser.close()

