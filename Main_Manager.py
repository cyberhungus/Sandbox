import multiprocessing as mp
import Data_Getter_Realsense as dg
import Data_Interpreter as di
import Data_Visualizer as dv
import Settings_Manager as sm 
import os
import GUI_Manager as gm
from threading import Thread 

#Main Class, start this file to start the program
class Main_Manager:
    def __init__(self):
        self.Raw_Queue = mp.Queue()
        self.Interpreted_Queue = mp.Queue()
        self.Data_Getter = dg.Data_Getter(1,self.Raw_Queue,self.Interpreted_Queue)
        self.Settings_Manager = sm.Settings_Manager(self)

        self.Data_Interpreter = di.Data_Interpreter(self.Raw_Queue, self.Interpreted_Queue, is_mock=True)
        self.Interpret_Process = mp.Process(target=self.Data_Interpreter.run)
        self.Interpret_Process.start()
        self.Data_Visualizer = dv.Data_Visualizer(self.Interpreted_Queue)
        self.Visualize_Process = mp.Process(target=self.Data_Visualizer.visualizer_runner)
        self.Visualize_Process.start()

        self.gui = gm.GUI_Manager(self.Settings_Manager)

        
    #called by settings manager to make alterations to the running subprocesses (i.e. Data Interpreter)
    def update_settings_hook(self,settings_dict):
        for item in settings_dict.items():
            self.Raw_Queue.put_nowait((item[0],item[1]))
        self.Data_Getter.update_refresh_rate(settings_dict['refreshRate'])
        
    #turns the color correction function on or off 
    def toggle_color_correct(self, state):
        self.Data_Getter.toggle_color_correct(state)



if __name__ == '__main__':

    try:
        #gives program maximum ressources 
        os.nice(19)
    except:
        print("Not on UNIX, nice isnt needed")
    print("program start")
    m = Main_Manager()

        
        


