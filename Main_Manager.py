import multiprocessing as mp
import Data_Getter as dg
import Data_Interpreter as di
import Data_Visualizer as dv
import os
from threading import Thread

class Main_Manager:
    def __init__(self):
        self.Raw_Queue = mp.Queue()
        self.Data_Getter = dg.Data_Getter(5,self)       
        self.Interpreted_Queue = mp.Queue()
        self.Data_Interpreter = di.Data_Interpreter(self.Raw_Queue, self.Interpreted_Queue)
        self.Data_Visualizer = dv.Data_Visualizer(self.Interpreted_Queue)
        self.latest_raw_data = 0 
        self.latest_processed_data=0
        
    def register_new_data(self, data):
        self.latest_raw_data = data
        self.latest_processed_data = self.Data_Interpreter.interpret_data(self.latest_raw_data)
        self.Data_Visualizer.receive_new_data(self.latest_processed_data)
        

        
#gives program maximum ressources 
os.nice(19)
print("program start")
m = Main_Manager()
        
        
        