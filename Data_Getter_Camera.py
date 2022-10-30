
from logging import captureWarnings
from pickle import FALSE
import cv2 as cv 
from threading import Thread 
import time as t 
import numpy as np
import frame_convert2 as fc



#freq = how many refreshes per second
#output_queue = queue to pass data to data visualizer 
#is_mock: if true uses normal camera, if false uses kinect
#resulotion: capture resolution for normal camera
#color_correct: Uses the pixels on the top right of the image to set the color of tokens used for AR-functionality 
class Data_Getter:

    def __init__(self, freq, output_queue_interpreter, resolution = (640,480),color_correct=False ):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue_interpreter

        self.next_capture_time = 0 
        self.resolution = resolution 
        self.color_correct = color_correct
        self.image_buffer = []
        self.interpolation_number = 10

        #starts data gathering thread 
  

    def get_Data(self):
        vid = cv.VideoCapture(0)
        vid.set(cv.CAP_PROP_FRAME_WIDTH,self.resolution[0])
        vid.set(cv.CAP_PROP_FRAME_HEIGHT,self.resolution[1])
        while 1:
            if self.current_milli_time() > self.next_capture_time:
                self.next_capture_time = self.current_milli_time()+self.ms_delay
                info, captured_data = vid.read()
                if captured_data is not None:
                    output_data_grey = cv.cvtColor(captured_data, cv.COLOR_BGR2GRAY)
                    output_data_grey = cv.cvtColor(captured_data, cv.COLOR_BGR2RGB)
                    self.output.put_nowait((output_data_grey,captured_data))
                else:
                    print("Captured Data None")

    #helper function for time in milliseconds       
    def current_milli_time(self):
        return round(t.time()*1000)

    #alters refresh rate 
    def update_refresh_rate(self, new_rate):
        self.ms_delay = 1000/int(new_rate)