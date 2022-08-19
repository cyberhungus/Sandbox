from threading import Thread 
from multiprocessing import Queue
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2


#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 210  
                

    def run(self):
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                processed_data = self.interpret_data(new_data)
                self.output.put_nowait(processed_data)

    def interpret_data(self, data):
        #make the grayscale data into a rgb data array and apply filters
        print("interpreting data")
        work_data = self.do_pretty_rgb(data)
        col_data = self.height_calc_new(work_data)
        return col_data
    
    #this function does some neccessary conversions, putting the 
    def do_pretty_rgb(self, data):
        pretty_array = fc.pretty_depth_cv(data)
        img = Image.fromarray(pretty_array,"L").convert("RGB")
        #.filter(ImageFilter.EDGE_ENHANCE)
        rgb_array = np.array(img)
        return rgb_array
        
    def height_calc_new(self,data):

        data[np.where((data>=[self.waterlevel,self.waterlevel,self.waterlevel]).all(axis=2))] = [250,0,0]
        data[np.where((data<=[self.waterlevel,self.waterlevel,self.waterlevel]).all(axis=2))] = [0,self.waterlevel,0]
        return data
