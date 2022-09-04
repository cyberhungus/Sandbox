
from logging import captureWarnings
from pickle import FALSE

import pyrealsense2 as rs
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
    def __init__(self, freq, output_queue_interpreter,output_data_vis,manager, is_mock = False, resolution = (640,480),color_correct=False ):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue_interpreter
        self.visualizer_output = output_data_vis
        self.next_capture_time = 0 
        self.is_mock = is_mock
        self.resolution = resolution 
        self.color_correct = color_correct
        self.image_buffer = []
        self.interpolation_number = 10
        self.manager = manager

        if self.is_mock==False:
            try:
                #activated the realsense sensor 
                self.pipeline = rs.pipeline()       
                config = rs.config()
                #use max resolution 
                config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
                config.enable_stream(rs.stream.color, 1920,1080, rs.format.bgr8, 15)
                self.device_manager =self.pipeline.start(config)

                self.hole_filler = rs.hole_filling_filter(0)
                self.temporal_filter = rs.temporal_filter()
            except Exception as ex:
                print("Data getter error in construction", ex)
                self.is_mock=True



        #starts data gathering thread 
        self.runner = Thread(target=self.get_Data)
        self.runner.start()      


    #get data gets the depth and RGB data from kinect (or two regular images from a webcam) and puts them into a queue so the data_interpreter can receive them
    def get_Data(self):
            if self.is_mock == False:

                while 1:
                    #normal function (check time, if time larger than next capture time,
                    #capture data and put in queue
                    if self.current_milli_time() > self.next_capture_time:
                        try:
                            self.next_capture_time = self.current_milli_time()+self.ms_delay
                            frames = self.pipeline.wait_for_frames()
                            #align color and depth data 
                            self.align = rs.align(rs.stream.color)                
                            aligned_frames = self.align.process(frames)
                            color_frame = aligned_frames.first(rs.stream.color)
                            depth_frame = aligned_frames.get_depth_frame()
                            #add image to image buffer, if imagebuffer is overcrowded, remove the oldest element, then average the data in the buffer
                            self.image_buffer.append(depth_frame)
                            if len(self.image_buffer)>self.interpolation_number:
                                self.image_buffer.pop(0)
                            for image in self.image_buffer:
                                 depth_frame_temp_filter = self.temporal_filter.process(image)
                            #perform hole filling on data 
                            depth_frame = self.hole_filler.process(depth_frame_temp_filter)
                            #extracts frame data as numpy array 
                            depth_data = np.asanyarray(depth_frame.get_data())
                       
                            color_data = np.asanyarray(color_frame.get_data())
                            
                            #sends raw color data to visualizer for display 
                            self.visualizer_output.put_nowait(("RAW_RGB",color_data))
                            #looks at top right pixel and sends the calue to data interpreter, where it is used to find AR-tokens 
                            if self.color_correct == True:
                                capture_color_reference = color_data[10][10]
                                self.output.put_nowait(("color_correct",capture_color_reference))
                            #sends depth and color data to visualizer for analysis 
                            self.output.put_nowait((depth_data,color_data))
                            self.manager.register_latest_image(color_data)
                        except Exception as ex:
                            print("exception in data getter",ex)
            #test function to get normal webcam img 
            else:
                vid = cv.VideoCapture(0)
                vid.set(cv.CAP_PROP_FRAME_WIDTH,self.resolution[0])
                vid.set(cv.CAP_PROP_FRAME_HEIGHT,self.resolution[1])
                while 1:
                    if self.current_milli_time() > self.next_capture_time:
                        self.next_capture_time = self.current_milli_time()+self.ms_delay
                        info, captured_data = vid.read()
                        if captured_data is not None:
                            output_data_grey = cv.cvtColor(captured_data, cv.COLOR_BGR2GRAY)
                            if self.color_correct == True:
                                capture_color_reference = captured_data[10][10]
                                print("color correct reference:", capture_color_reference)
                                self.output.put_nowait(("color_correct",capture_color_reference))
                            self.output.put_nowait((output_data_grey,captured_data))
          
    #helper function for time in milliseconds       
    def current_milli_time(self):
        return round(t.time()*1000)

    #alters refresh rate 
    def update_refresh_rate(self, new_rate):
        self.ms_delay = 1000/int(new_rate)

    #turns color correct on and off 
    def toggle_color_correct(self, new_status):
        self.color_correct = new_status
        print("color correct is now ", self.color_correct)

            
        
                
        
        
        
                
        
