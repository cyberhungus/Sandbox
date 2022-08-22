from cgi import test
from dis import pretty_flags
from distutils.fancy_getopt import FancyGetopt
from threading import Thread 
from multiprocessing import Queue
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2
import timeit

import testcy 
#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue,is_mock=False):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 150
        self.is_mock = is_mock
                

    def run(self):
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                processed_data = self.interpret_data(new_data)
                processed_data = cv2.resize(processed_data,dsize=None,fx=1.5,fy=1.5)
                self.output.put_nowait(processed_data)


    def interpret_data(self, data):
        #make the grayscale data into a rgb data array and apply filters
        print("interpreting data")
        work_data = self.do_pretty_rgb(data)
        starttime = timeit.default_timer()
        col_data = self.c_height_calc(work_data)
        print("Time for color convert algorithm :", timeit.default_timer() - starttime)
        return col_data
    
    #this function does some neccessary conversions, putting the 
    def do_pretty_rgb(self, data):
        if self.is_mock==False:
            pretty_img = fc.pretty_depth_cv(data)
            img = pretty_img
        else:
            #img = Image.fromarray(data,"L").convert("RGB")
            img=data
        #.filter(ImageFilter.EDGE_ENHANCE)
        rgb_array = np.array(img)
        return rgb_array
        

    
            
            




    def c_height_calc(self,arr):
        output = np.zeros((480,640),dtype=np.uint8)
        mult = self.waterlevel/4
        mult= int(mult)
        print(mult,type(mult))
        water = arr[:,:]>self.waterlevel
        arr[water] = -1 
        landA = arr[:,:]>self.waterlevel-mult
        arr[landA] = -1
        landB = arr[:,:]>self.waterlevel-(mult*2)
        arr[landB] = -1
        landC = arr[:,:]>self.waterlevel-(mult*3)
        arr[landC] = -1
        landD = arr[:,:]>self.waterlevel-(mult*4)
        arr[landD] = -1
        output[landD] = 250
        output[landC] = 200
        output[landB] = 150
        output[landA] = 100
        output[water] = 50
        img = Image.fromarray(output,"L").convert("RGB")
        data = np.array(img)
        #landD
        data[np.all(data == [250,250,250], axis=-1)] = (0,200,100)
        #landC
        data[np.all(data == [200,200,200], axis=-1)] = (0,150,100)
        #landB
        data[np.all(data == [150,150,150], axis=-1)] = (0,100,100)
        #landA
        data[np.all(data == [100,100,100], axis=-1)] = (0,50,0)
        #water
        data[np.all(data == [50,50,50], axis=-1)] = (200,50,0)
        #debug
        data[np.all(data > [50,50,50], axis=-1)] = (200,50,200)

        return data

