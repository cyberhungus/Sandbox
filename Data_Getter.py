import freenect as fn
from threading import Thread 
import time as t 
import cv2

#freq = how many refreshes per second
#output_queue = queue to pass data to data visualizer 
class Data_Getter:
    def __init__(self, freq, output_queue):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue
        self.next_capture_time = 0 
        self.runner = Thread(target=self.get_Data)
        self.runner.start()
        
        

    def get_Data(self):
        while 1:
        #normal function (check time, if time larger than next capture time,
        #capture data and put in queue

            if self.current_milli_time() > self.next_capture_time:
                try:
                    captured_data =fn.sync_get_depth()[0]
                    
                    self.next_capture_time = self.current_milli_time()+self.ms_delay

                    self.output.put_nowait(captured_data)
                    print("NEW DATA")
                    #cv2.imshow("RAW DATA",captured_data)
                except Exception as ex:
                    print("exception in data getter",ex)
                    
                #print("performed data capture and broadcast")            
        
    def current_milli_time(self):
        return round(t.time()*1000)
            
        
        
        
        
                
        
