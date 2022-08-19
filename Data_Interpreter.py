from threading import Thread 
from multiprocessing import Queue
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter


class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 150         
                

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
        col_data = self.do_height_calc(work_data)
        return col_data
    
    #this function does some neccessary conversions, putting the 
    def do_pretty_rgb(self, data):
        pretty_array = fc.pretty_depth_cv(data)
        img = Image.fromarray(pretty_array,"L").convert("RGB").filter(ImageFilter.EDGE_ENHANCE)
        rgb_array = np.array(img)
        return rgb_array
        
    #this function shall launch sets of threads which perform the neccessary calculations for each row of pixels, thereby speeding up transofrmation 
    def do_height_calc(self, data):
        for row in np.nditer(data):
            print(row)
            row=self.pixel_transform(row)

        return data         

    #function receives a row and analyses for height
    def pixel_transform(self,row):
            print(type(row))
            for pixel in row:
                #initially all pixels have the same value on all colours
                #therefore, check pixel[0] to see what the depth of the pixel ist
                #if pixel is small than waterlevel, it is land. 
                if pixel[0] >= self.waterlevel:
                    pixel[0] = 0
                    pixel[1] = 0
                    pixel[2] = 255
                else:
                    pixel[0] = 255
                    pixel[1] = 0
                    pixel[2] = 0     
                    
            return row
            
                    
