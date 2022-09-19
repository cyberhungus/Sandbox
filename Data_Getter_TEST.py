
import cv2 as cv 
from threading import Thread 
import time as t 
import numpy as np
import os 


#freq = how many refreshes per second
#output_queue = queue to pass data to data visualizer 
#is_mock: if true uses normal camera, if false uses kinect
#resulotion: capture resolution for normal camera
#color_correct: Uses the pixels on the top right of the image to set the color of tokens used for AR-functionality 
class Data_Getter:

    def __init__(self, freq, output_queue_interpreter,output_data_vis,manager, resolution = (640,480),color_correct=False ):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue_interpreter
        self.visualizer_output = output_data_vis
        self.next_capture_time = 0 
        self.resolution = resolution 
        self.color_correct = color_correct
        self.image_buffer = []
        self.interpolation_number = 10
        self.manager = manager
        #starts data gathering thread 
        self.runner = Thread(target=self.get_Data)
        self.runner.start()      

    def get_Data(self):
        testImg = cv.imread(os.getcwd()+"/assets/test6.png")
        while 1:
            if self.current_milli_time() > self.next_capture_time:
                self.next_capture_time = self.current_milli_time()+self.ms_delay
                captured_data=testImg
                if captured_data is not None:
                    output_data_grey = cv.cvtColor(captured_data, cv.COLOR_BGR2GRAY)
                    self.output.put_nowait((output_data_grey,captured_data))
                    self.visualizer_output.put_nowait(("RAW_RGB",captured_data))
                else:
                    print("Captured Data None")

    #helper function for time in milliseconds       
    def current_milli_time(self):
        return round(t.time()*1000)

    #alters refresh rate 
    def update_refresh_rate(self, new_rate):
        self.ms_delay = 1000/int(new_rate)