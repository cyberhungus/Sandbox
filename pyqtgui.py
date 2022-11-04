

from PyQt5 import QtCore, QtGui, QtWidgets
from SerialConnector import SerialConnector

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QFileDialog
from PyQt5.QtGui import QIcon , QColor 
from PIL import Image
from PyQt5 import QtWidgets, QtGui

from PIL import Image, ImageQt
import numpy as np
import cv2 as cv
from time import sleep


class Ui_MainWindow(object):

    def __init__(self, manager, pipe):
        self.setting_manager = manager
        self.latest_color_img = 0
        self.newWindow_status = False
        self.selected_points = []
        self.queue = pipe 
        self.xoffset = -30
        self.yoffset = 20
        self.serial = SerialConnector()

        self.imgmode = True


        self.upperRow = []
        self.lowerRow = []
        
        self.rowOffset = 200
        self.number_leds = 27



        app = QApplication(sys.argv)
        window = QWidget()
        self.setupUi(window)
        window.show() 
        app.exec()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ColorA = QtWidgets.QPushButton(self.centralwidget)
        self.ColorA.setGeometry(QtCore.QRect(160, 0, 141, 41))
        self.ColorA.setObjectName("ColorA")
        self.ColorB = QtWidgets.QPushButton(self.centralwidget)
        self.ColorB.setGeometry(QtCore.QRect(160, 40, 141, 31))
        self.ColorB.setObjectName("ColorB")
        self.ColorC = QtWidgets.QPushButton(self.centralwidget)
        self.ColorC.setGeometry(QtCore.QRect(160, 70, 141, 41))
        self.ColorC.setObjectName("ColorC")
        self.ColorD = QtWidgets.QPushButton(self.centralwidget)
        self.ColorD.setGeometry(QtCore.QRect(160, 110, 141, 41))
        self.ColorD.setObjectName("ColorD")
        self.ColorE = QtWidgets.QPushButton(self.centralwidget)
        self.ColorE.setGeometry(QtCore.QRect(160, 150, 141, 41))
        self.ColorE.setObjectName("ColorE")
        self.ColorF = QtWidgets.QPushButton(self.centralwidget)
        self.ColorF.setGeometry(QtCore.QRect(160, 190, 141, 41))
        self.ColorF.setObjectName("ColorF")
        self.ColorG = QtWidgets.QPushButton(self.centralwidget)
        self.ColorG.setGeometry(QtCore.QRect(160, 230, 141, 51))
        self.ColorG.setObjectName("ColorG")
        self.HeightLines = QtWidgets.QCheckBox(self.centralwidget)
        self.HeightLines.setEnabled(True)
        self.HeightLines.setGeometry(QtCore.QRect(380, 10, 71, 16))
        self.HeightLines.setChecked(True)
        self.HeightLines.setObjectName("HeightLines")
        self.ShowMarkerCheck = QtWidgets.QCheckBox(self.centralwidget)
        self.ShowMarkerCheck.setGeometry(QtCore.QRect(380, 30, 91, 16))
        self.ShowMarkerCheck.setChecked(True)
        self.ShowMarkerCheck.setObjectName("ShowMarkerCheck")
        self.ColorWater = QtWidgets.QPushButton(self.centralwidget)
        self.ColorWater.setGeometry(QtCore.QRect(160, 280, 141, 41))
        self.ColorWater.setObjectName("ColorWater")
        self.ColorDeepWater = QtWidgets.QPushButton(self.centralwidget)
        self.ColorDeepWater.setGeometry(QtCore.QRect(160, 320, 141, 51))
        self.ColorDeepWater.setObjectName("ColorDeepWater")
        self.ResetButton = QtWidgets.QPushButton(self.centralwidget)
        self.ResetButton.setGeometry(QtCore.QRect(490, 0, 91, 41))
        self.ResetButton.setObjectName("ResetButton")
        self.XOffsetSlider = QtWidgets.QScrollBar(self.centralwidget)
        self.XOffsetSlider.setGeometry(QtCore.QRect(370, 300, 160, 16))
        self.XOffsetSlider.setMinimum(-200)
        self.XOffsetSlider.setMaximum(200)
        self.XOffsetSlider.setOrientation(QtCore.Qt.Horizontal)
        self.XOffsetSlider.setObjectName("XOffsetSlider")
        self.YOffsetSlider = QtWidgets.QScrollBar(self.centralwidget)
        self.YOffsetSlider.setGeometry(QtCore.QRect(320, 130, 16, 160))
        self.YOffsetSlider.setMinimum(-200)
        self.YOffsetSlider.setMaximum(200)
        self.YOffsetSlider.setOrientation(QtCore.Qt.Vertical)
        self.YOffsetSlider.setObjectName("YOffsetSlider")
        self.YOffsetLabel = QtWidgets.QLabel(self.centralwidget)
        self.YOffsetLabel.setGeometry(QtCore.QRect(320, 300, 39, 11))
        self.YOffsetLabel.setObjectName("YOffsetLabel")
        self.XOffsetLabel = QtWidgets.QLabel(self.centralwidget)
        self.XOffsetLabel.setGeometry(QtCore.QRect(320, 120, 39, 11))
        self.XOffsetLabel.setObjectName("XOffsetLabel")
        self.RefreshLabel = QtWidgets.QLabel(self.centralwidget)
        self.RefreshLabel.setGeometry(QtCore.QRect(30, 190, 39, 11))
        self.RefreshLabel.setObjectName("RefreshLabel")
        self.WaterlevelLabel = QtWidgets.QLabel(self.centralwidget)
        self.WaterlevelLabel.setGeometry(QtCore.QRect(90, 190, 61, 16))
        self.WaterlevelLabel.setObjectName("WaterlevelLabel")
        self.RefreshText = QtWidgets.QLabel(self.centralwidget)
        self.RefreshText.setGeometry(QtCore.QRect(30, 170, 39, 11))
        self.RefreshText.setObjectName("RefreshText")
        self.WaterlevelText = QtWidgets.QLabel(self.centralwidget)
        self.WaterlevelText.setGeometry(QtCore.QRect(90, 170, 61, 16))
        self.WaterlevelText.setObjectName("WaterlevelText")
        self.WaterLevelSlider = QtWidgets.QSlider(self.centralwidget)
        self.WaterLevelSlider.setGeometry(QtCore.QRect(90, 0, 31, 151))
        self.WaterLevelSlider.setMaximumSize(QtCore.QSize(16777215, 179))
        self.WaterLevelSlider.setMaximum(255)
        self.WaterLevelSlider.setOrientation(QtCore.Qt.Vertical)
        self.WaterLevelSlider.setObjectName("WaterLevelSlider")
        self.RefreshSlider = QtWidgets.QSlider(self.centralwidget)
        self.RefreshSlider.setGeometry(QtCore.QRect(40, 0, 31, 151))
        self.RefreshSlider.setMinimum(1)
        self.RefreshSlider.setMaximum(19)
        self.RefreshSlider.setOrientation(QtCore.Qt.Vertical)
        self.RefreshSlider.setObjectName("RefreshSlider")
        self.Mark1Label = QtWidgets.QLabel(self.centralwidget)
        self.Mark1Label.setGeometry(QtCore.QRect(390, 330, 39, 41))
        self.Mark1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Mark1Label.setObjectName("Mark1Label")
        self.Mark2Label = QtWidgets.QLabel(self.centralwidget)
        self.Mark2Label.setGeometry(QtCore.QRect(420, 330, 39, 41))
        self.Mark2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Mark2Label.setObjectName("Mark2Label")
        self.Mark3Label = QtWidgets.QLabel(self.centralwidget)
        self.Mark3Label.setGeometry(QtCore.QRect(450, 330, 39, 41))
        self.Mark3Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Mark3Label.setObjectName("Mark3Label")
        self.Mark4Label = QtWidgets.QLabel(self.centralwidget)
        self.Mark4Label.setGeometry(QtCore.QRect(480, 330, 39, 41))
        self.Mark4Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Mark4Label.setObjectName("Mark4Label")
        self.SaveButton = QtWidgets.QPushButton(self.centralwidget)
        self.SaveButton.setGeometry(QtCore.QRect(490, 110, 91, 51))
        self.SaveButton.setObjectName("SaveButton")
        self.LoadButton = QtWidgets.QPushButton(self.centralwidget)
        self.LoadButton.setGeometry(QtCore.QRect(490, 50, 91, 51))
        self.LoadButton.setObjectName("LoadButton")
        self.ComPortDropDown = QtWidgets.QComboBox(self.centralwidget)
        self.ComPortDropDown.setGeometry(QtCore.QRect(10, 240, 141, 21))
        self.ComPortDropDown.setObjectName("ComPortDropDown")
        self.SerialStatusLabel = QtWidgets.QLabel(self.centralwidget)
        self.SerialStatusLabel.setGeometry(QtCore.QRect(10, 310, 131, 21))
        self.SerialStatusLabel.setObjectName("SerialStatusLabel")
        self.SerialColorLabel = QtWidgets.QLabel(self.centralwidget)
        self.SerialColorLabel.setGeometry(QtCore.QRect(10, 340, 39, 11))
        self.SerialColorLabel.setObjectName("SerialColorLabel")
        self.SerialRefreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.SerialRefreshButton.setGeometry(QtCore.QRect(10, 210, 141, 19))
        self.SerialRefreshButton.setObjectName("SerialRefreshButton")
        self.DepthGraphicView = QtWidgets.QLabel(self.centralwidget)
        self.DepthGraphicView.setGeometry(QtCore.QRect(450, 390, 431, 361))
        self.DepthGraphicView.setObjectName("DepthGraphicView")
        self.RGBGraphicView = QtWidgets.QLabel(self.centralwidget)
        self.RGBGraphicView.setGeometry(QtCore.QRect(10, 390, 431, 361))
        self.RGBGraphicView.setObjectName("RGBGraphicView")
        self.OutputGraphicView = QtWidgets.QLabel(self.centralwidget)
        self.OutputGraphicView.setGeometry(QtCore.QRect(890, 10, 1031, 561))
        self.OutputGraphicView.setObjectName("OutputGraphicView")
        self.SerialConnectButton = QtWidgets.QPushButton(self.centralwidget)
        self.SerialConnectButton.setGeometry(QtCore.QRect(10, 270, 141, 19))
        self.SerialConnectButton.setObjectName("SerialConnectButton")


        self.retranslateUi(self)
        self.RefreshSlider.valueChanged['int'].connect(self.FPSchanged) # type: ignore
        self.WaterLevelSlider.valueChanged['int'].connect(self.WaterLevelChanged) # type: ignore
        self.ResetButton.clicked.connect(self.Reset) # type: ignore
        self.HeightLines.toggled['bool'].connect(self.HeightLineToggle) # type: ignore
        self.ShowMarkerCheck.toggled['bool'].connect(self.MarkerToggle) # type: ignore
        self.XOffsetSlider.valueChanged['int'].connect(self.XOffsetChange) # type: ignore
        self.YOffsetSlider.valueChanged['int'].connect(self.YOffsetChange) # type: ignore
        self.ColorA.clicked.connect(self.ColorAChange) # type: ignore
        self.ColorB.clicked.connect(self.ColorBChange) # type: ignore
        self.ColorC.clicked.connect(self.ColorCChange) # type: ignore
        self.ColorD.clicked.connect(self.ColorDChange) # type: ignore
        self.ColorE.clicked.connect(self.ColorEChange) # type: ignore
        self.ColorF.clicked.connect(self.ColorFChange) # type: ignore
        self.ColorG.clicked.connect(self.ColorGChange) # type: ignore
        self.ColorWater.clicked.connect(self.ColorWChange) # type: ignore
        self.ColorDeepWater.clicked.connect(self.ColorDWChange) # type: ignore
        self.LoadButton.clicked.connect(self.loadFile) # type: ignore
        self.SaveButton.clicked.connect(self.saveToFile) # type: ignore
        self.SerialRefreshButton.clicked.connect(self.configureComPortDropDown)
        self.SerialConnectButton.clicked.connect(self.openComport)



        self.configureComPortDropDown()
        self.updateUIFromSettings()
        self.startPipeWorker()

    def openComport(self):
        connectionResult = self.serial.openSerialByName(self.ComPortDropDown.currentText())
        if connectionResult == True:
            self.SerialColorLabel.setStyleSheet("background-color: {} ;".format("green"))
        else:
            self.SerialColorLabel.setStyleSheet("background-color: {} ;".format("red"))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
 #       MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ColorA.setText(_translate("MainWindow", "ColorA"))
        self.ColorB.setText(_translate("MainWindow", "ColorB"))
        self.ColorC.setText(_translate("MainWindow", "ColorC"))
        self.ColorD.setText(_translate("MainWindow", "ColorD"))
        self.ColorE.setText(_translate("MainWindow", "ColorE"))
        self.ColorF.setText(_translate("MainWindow", "ColorF"))
        self.ColorG.setText(_translate("MainWindow", "ColorG"))
        self.HeightLines.setText(_translate("MainWindow", "HeightLines"))
        self.ShowMarkerCheck.setText(_translate("MainWindow", "Show Markers"))
        self.ColorWater.setText(_translate("MainWindow", "ColorWater"))
        self.ColorDeepWater.setText(_translate("MainWindow", "ColorDeepWater"))
        self.ResetButton.setText(_translate("MainWindow", "Reset"))
        self.YOffsetLabel.setText(_translate("MainWindow", "TextLabel"))
        self.XOffsetLabel.setText(_translate("MainWindow", "TextLabel"))
        self.RefreshLabel.setText(_translate("MainWindow", "1"))
        self.WaterlevelLabel.setText(_translate("MainWindow", "TextLabel"))
        self.RefreshText.setText(_translate("MainWindow", "FPS"))
        self.WaterlevelText.setText(_translate("MainWindow", "Waterlevel"))
        self.Mark1Label.setText(_translate("MainWindow", "1"))
        self.Mark2Label.setText(_translate("MainWindow", "2"))
        self.Mark3Label.setText(_translate("MainWindow", "3"))
        self.Mark4Label.setText(_translate("MainWindow", "4"))
        self.SaveButton.setText(_translate("MainWindow", "Save As"))
        self.LoadButton.setText(_translate("MainWindow", "LoadFromFile"))
        self.SerialStatusLabel.setText(_translate("MainWindow", "SerialStatus"))
        self.SerialColorLabel.setStyleSheet("background-color: {} ;".format("red"))
        self.SerialConnectButton.setText(_translate("MainWindow", "Serial connect"))
        self.SerialRefreshButton.setText(_translate("MainWindow", "Refresh Serial Ports"))

    def configureComPortDropDown(self):
        for port in  self.serial.getAvailableComPorts():
            self.ComPortDropDown.addItem(port)


    def startPipeWorker(self):
        self.thread = QThread()
        self.worker = PipeWorker()
        self.worker.set_q(self.queue)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportMarkers)
        self.worker.image.connect(self.receiveRGBImage)
        self.thread.start()


    def receiveRGBImage(self, img):
        self.upperRow = []
        self.lowerRow = []
        if self.imgmode == True:
            for led in range(0,self.number_leds+1):
                try:
                    w, h , d = img.shape
                    upColor = img[int((w/self.number_leds)*led)-1][int(self.rowOffset)-1]
                    self.upperRow.append(upColor)
                    downColor =  img[int((w/self.number_leds)*led)-1][int(h-self.rowOffset)-1]
                    self.lowerRow.append(downColor)
                    if self.serial.serialStarted == True:
                       # print(led)
                        self.serial.sendLightMessage(led,upColor[2], upColor[1], upColor[0])
                        sleep(0.005)
                        self.serial.sendLightMessage(led+self.number_leds,upColor[2], upColor[1], upColor[0])
                except Exception as ex:
                    print("Catch" , ex)


    def reportMarkers(self, value):
        if type(value)==type("String"):
            if value.__contains__("0"):
                    self.Mark1Label.setStyleSheet("background-color: {} ;".format("green"))
            else:                
                    self.Mark1Label.setStyleSheet("background-color: {} ;".format("red"))
            if value.__contains__("1"):
                    self.Mark2Label.setStyleSheet("background-color: {} ;".format("green"))
            else:                
                    self.Mark2Label.setStyleSheet("background-color: {} ;".format("red"))
            if value.__contains__("2"):
                    self.Mark3Label.setStyleSheet("background-color: {} ;".format("green"))
            else:                
                    self.Mark3Label.setStyleSheet("background-color: {} ;".format("red"))
            if value.__contains__("3"):
                    self.Mark4Label.setStyleSheet("background-color: {} ;".format("green"))
            else:                
                    self.Mark4Label.setStyleSheet("background-color: {} ;".format("red"))

    def ColorAChange(self):
        print("A Change")
        sel_color = self.changeColor()
        self.ColorA.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorA",[sel_color.red(),sel_color.green(),sel_color.blue()])

    def ColorBChange(self):
        print("B Change")
        sel_color = self.changeColor()
        self.ColorB.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorB",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorCChange(self):
        print("C Change")
        sel_color = self.changeColor()
        self.ColorC.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorC",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorDChange(self):
        print("D Change")
        sel_color = self.changeColor()
        self.ColorD.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorD",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorEChange(self):
        print("E Change")
        sel_color = self.changeColor()
        self.ColorE.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorE",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorFChange(self):
        print("F Change")
        sel_color = self.changeColor()
        self.ColorF.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorF",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorGChange(self):
        print("G Change")
        sel_color = self.changeColor()
        self.ColorG.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorG",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorWChange(self):
        print("W Change")
        sel_color = self.changeColor()
        self.ColorWater.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorWater",[sel_color.red(),sel_color.green(),sel_color.blue()])
    def ColorDWChange(self):
        print("DW Change")
        sel_color = self.changeColor()
        self.ColorDeepWater.setStyleSheet("background-color: {} ;".format( sel_color.name()))
        self.setting_manager.alter_setting("arrcolorDeepWater",[sel_color.red(),sel_color.green(),sel_color.blue()])

    
    def FPSchanged(self, value):
       # print("FPS Change" , value)
        self.setting_manager.alter_setting("refreshRate",value)
        self.RefreshLabel.setText(str(value))

    def WaterLevelChanged(self, value):
        print("Waterlevel Change" , value)
        self.setting_manager.alter_setting("waterlevel",value)
        self.WaterlevelLabel.setText(str(value))

    def Reset(self):
        print("Reset")
        self.setting_manager.write_standards()
        self.setting_manager.read()
        self.updateUIFromSettings()

    def HeightLineToggle(self, value):
        print("HLT", value)
        self.setting_manager.alter_setting("heightlineState",value)

    def MarkerToggle(self, value):
        self.setting_manager.alter_setting("displayMarkers",value)

    def XOffsetChange(self, value):
        print("X", value)
        self.setting_manager.alter_setting("xoffset",value)
        self.XOffsetLabel.setText(str(value))

    def YOffsetChange(self, value):
        print("Y", value)
        self.setting_manager.alter_setting("yoffset",value)        
        self.YOffsetLabel.setText(str(value))

    def changeColor(self):
        color = QColorDialog.getColor()
        return color

    def loadFile(self):
        print("LoadFile")
        path = self.openFileNameDialog()
        self.setting_manager.read(path)
        self.setting_manager.passSettings()
        self.updateUIFromSettings()

    def saveToFile(self):
        print("SaveFile")
        path = self.saveFileNameDialog()
        self.setting_manager.write(path)


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self.LoadButton   ,"QFileDialog.getOpenFileName()", os.getcwd() ,"JSON Files (*.json)", options=options)
        if fileName:
            return fileName

    def saveFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.SaveButton,"QFileDialog.getSaveFileName()",os.getcwd(),"Files (*.json)", options=options)
        if fileName:
            return fileName

    def updateUIFromSettings(self):
        set_dict = self.setting_manager.get_settings()
        col = set_dict.get('colorA')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorA.setStyleSheet("background-color: {} ;".format( col.name()))

        col = set_dict.get('colorB')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorB.setStyleSheet("background-color: {} ;".format( col.name()))
        col = set_dict.get('colorC')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorC.setStyleSheet("background-color: {} ;".format( col.name()))
        col = set_dict.get('colorD')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorD.setStyleSheet("background-color: {} ;".format( col.name()))
        col = set_dict.get('colorE')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorE.setStyleSheet("background-color: {} ;".format( col.name()))
        col = set_dict.get('colorF')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorF.setStyleSheet("background-color: {} ;".format( col.name()))


        col = set_dict.get('colorG')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorG.setStyleSheet("background-color: {} ;".format( col.name()))

        col = set_dict.get('colorWater')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorWater.setStyleSheet("background-color: {} ;".format( col.name()))


        col = set_dict.get('colorDeepWater')
        col = QtGui.QColor().fromRgb(col[0],col[1],col[2])
        self.ColorDeepWater.setStyleSheet("background-color: {} ;".format( col.name()))


        value = set_dict.get("waterlevel")
        self.WaterLevelSlider.setValue(value)

        value = set_dict.get("refreshRate")
      #  print("refresh", value)
        self.RefreshSlider.setValue(value)

        value = set_dict.get("xoffset")
        self.XOffsetSlider.setValue(value)
        value = set_dict.get("yoffset")
        self.YOffsetSlider.setValue(value)


    def array_color_hex(self,array):
        """
        Helper function which transforms a three value list representing an RGB color into a string that can be used to color tkinter elements. 
        This is the RGB version of that function. 

        :param list array: A three value list representing a color - [RED, GREEN, BLUE]

        :returns: A String representing the input color.  
        :rtype: String 
        """

        try:
            return '#%02x%02x%02x' % (array[0], array[1], array[2])
        except:
            return "#000000"



class PipeWorker(QObject):

    finished = pyqtSignal()    
    progress = pyqtSignal(str)
    image = pyqtSignal(np.ndarray)




    def set_q(self, q):
        self.queue = q 

    def run(self,):
        while 1:
            if not self.queue.empty():
                rec = self.queue.get_nowait()
               # print("qt gui received", rec)
                if rec[0] == "FOUNDMARKERS":
                    seenString =""
                    try:
                        for item in rec[1]:
                            seenString+=str(item)
                            seenString+="-"
                            self.progress.emit(seenString)
                    except:
                        pass

                elif rec[0] == "FULL":
                    try:
                        array = rec[1]


                        self.image.emit(array)
                    except Exception as ex:
                        print(ex)
                        pass
        self.finished.emit()


