import multiprocessing as mp
import Data_Getter_Realsense as dg
import Data_Interpreter as di
import Data_Visualizer as dv
import Settings_Manager as sm 
import os
from pyqtgui import Ui_MainWindow
from threading import Thread 

#Main Class, start this file to start the program
class Main_Manager:
    def __init__(self):
        self.Raw_Queue = mp.Queue()
        self.FrontendQueue = mp.Queue()

        self.Interpreted_Queue = mp.Queue()

        self.Data_Getter = dg.Data_Getter(3,self.Raw_Queue)

        self.Getter_Process = mp.Process(target = self.Data_Getter.get_Data)
        self.Getter_Process.start()
        

        self.Data_Interpreter = di.Data_Interpreter(self.Raw_Queue, self.Interpreted_Queue, self.FrontendQueue)
        self.Interpret_Process = mp.Process(target=self.Data_Interpreter.run)
        self.Interpret_Process.start()

        self.Data_Visualizer = dv.Data_Visualizer(self.Interpreted_Queue)
        self.Visualize_Process = mp.Process(target=self.Data_Visualizer.visualizer_runner)
        self.Visualize_Process.start()
        
        self.latest_color_img = 0
       # self.Settings_Manager, self.FrontendQueue
        self.Settings_Manager = sm.Settings_Manager(self)
        self.gui = Ui_MainWindow(self.Settings_Manager, self.FrontendQueue)

        
    #called by settings manager to make alterations to the running subprocesses (i.e. Data Interpreter)
    def update_settings_hook(self,settings_dict):
        for item in settings_dict.items():
            self.Raw_Queue.put_nowait((item[0],item[1]))
        self.Data_Getter.update_refresh_rate(settings_dict['refreshRate'])
        self.Interpreted_Queue.put_nowait(("SHOW_MARKERS",settings_dict['displayMarkers']))
        self.Interpreted_Queue.put_nowait(("MARKER_SIZE",settings_dict['markerSize']))
        self.Interpreted_Queue.put_nowait(("BRIGHTNESS",settings_dict['addBrightness']))






if __name__ == '__main__':
    print("Program Start")
    m = Main_Manager()

        