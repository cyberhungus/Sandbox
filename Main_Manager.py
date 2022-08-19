import multiprocessing as mp
import Data_Getter as dg
import Data_Interpreter as di
import Data_Visualizer as dv
import os

class Main_Manager:
    def __init__(self):
        self.Raw_Queue = mp.Queue()
        self.Data_Getter = dg.Data_Getter(20,self.Raw_Queue)
        self.Interpreted_Queue = mp.Queue()
        self.Data_Interpreter = di.Data_Interpreter(self.Raw_Queue, self.Interpreted_Queue)
        self.Interpret_Process = mp.Process(target=self.Data_Interpreter.run)
        self.Interpret_Process.start()
        self.Data_Visualizer = dv.Data_Visualizer(self.Interpreted_Queue)
        self.Visualize_Process = mp.Process(target=self.Data_Visualizer.visualizer_runner)
        self.Visualize_Process.start()
        
        
#gives program maximum ressources 
os.nice(19)
print("program start")
m = Main_Manager()
        
        
        