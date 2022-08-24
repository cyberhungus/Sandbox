from logging import captureWarnings
try:
    import freenect
except:
    print("Couldnt find freenect library - add is_mock=True to Data Getter Constructor ")
    import cv2 as cv 
from threading import Thread 
import time as t 
import numpy as np
import frame_convert2 as fc

#freq = how many refreshes per second
#output_queue = queue to pass data to data visualizer 
class Data_Getter:
    def __init__(self, freq, output_queue, is_mock = False ):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue
        self.next_capture_time = 0 
        self.num_to_average = 15 
        self.is_mock = is_mock
        self.runner = Thread(target=self.get_Data_Depth)
        self.runner.start()
        #print(np.get_include())
        
        

    def get_Data_Depth(self):
            if self.is_mock == False:
                while 1:
        #normal function (check time, if time larger than next capture time,
        #capture data and put in queue
                    if self.current_milli_time() > self.next_capture_time:
                        try:
                            self.next_capture_time = self.current_milli_time()+self.ms_delay
                            captured_data_depth = freenect.sync_get_depth()[0]
                            captured_data_rgb = freenect.sync_get_video()[0]
                            self.output.put_nowait((captured_data_depth,captured_data_rgb))
                            print("New Data")
                        except Exception as ex:
                            print("exception in data getter",ex)
            else:
                vid = cv.VideoCapture(0)    
                while 1:
                    if self.current_milli_time() > self.next_capture_time:
                        self.next_capture_time = self.current_milli_time()+self.ms_delay
                        print("New Data")
                        info, captured_data = vid.read()
                        #print(captured_data.shape)
                        if captured_data is not None:
                            output_data = cv.cvtColor(captured_data, cv.COLOR_BGR2GRAY)
                            self.output.put_nowait(output_data)


          
        
    def current_milli_time(self):
        return round(t.time()*1000)
            
        
        
        
        
                
        
