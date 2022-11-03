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
    def __init__(self, freq, output_queue_interpreter, resolution = (640,480)):
        self.freq = freq
        self.ms_delay = 1000/self.freq 
        print("Capture Delay", self.ms_delay)
        self.output = output_queue_interpreter

        self.next_capture_time = 0 
        self.resolution = resolution 

        self.image_buffer = []
        self.interpolation_number = 10
       # self.manager = manager

        #activated the realsense sensor 

        #starts data gathering thread 
       # self.runner = Thread(target=self.get_Data)
      #  self.runner.start()      
        
    def get_Data(self):
        """
        This is the main function of this class. First it checks wether the time is right to send a new image to Data_Interpreter. 
        Then the actual image and depth data is taken from the camera. This data is then aligned and filtered, using temporal filtering (average between several pictures)
        and a hole filling algorithm is also applied. The data is then converted to a numpy array. Those arrays are passed to data_interpreter

        
        """
        self.pipeline = rs.pipeline()       
        config = rs.config()
        #use max resolution 
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))
        if device_product_line == 'L500':
            config.enable_stream(rs.stream.depth, 1024,768, rs.format.z16, 30)
            print("L500 detected")
        else:
            config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 1920,1080, rs.format.bgr8, 15)
        self.device_manager =self.pipeline.start(config)

        self.hole_filler = rs.hole_filling_filter(0)
        self.temporal_filter = rs.temporal_filter(.001,100,8)

        while 1:

            if self.current_milli_time() > self.next_capture_time:
                try:
                    self.next_capture_time = self.current_milli_time()+self.ms_delay
                    frames = self.pipeline.wait_for_frames()
                    self.align = rs.align(rs.stream.color)                
                    aligned_frames = self.align.process(frames)
                    color_frame = aligned_frames.first(rs.stream.color)
                    depth_frame = aligned_frames.get_depth_frame()

                    depth_frame_temp_filter = self.temporal_filter.process(depth_frame)
                    #depth_frame = self.hole_filler.process(depth_frame)
                    depth_frame = self.hole_filler.process(depth_frame_temp_filter)
                    #depth_frame = rs.threshold_filter(min_dist = 0.5, max_dist =  4).process(depth_frame) 

                    depth_data = np.asanyarray(rs.colorizer(2).colorize(depth_frame).get_data())
                    color_data = np.asanyarray(color_frame.get_data())  

                    depth_data = cv.rotate(depth_data, cv.ROTATE_90_COUNTERCLOCKWISE)
                    color_data = cv.rotate(color_data, cv.ROTATE_90_COUNTERCLOCKWISE)
                   # print("RAW DEPTH MIN", np.min(depth_data))
                    self.output.put_nowait((depth_data,color_data))

                except Exception as ex:
                    print("exception in data getter",ex)

               
          
        
    def current_milli_time(self):
        """Returns time in milliseconds. Use to regulate capture frequency. 
        
        :returns: The current time in milliseconds. 
        :rtype : int
        
        """
        return round(t.time()*1000)

   
    def update_refresh_rate(self, new_rate):
        """Changes the refresh rate
        
        :param int new_rate: How many images should be passed to Data_Visualizer per second. 
        
        """
        self.ms_delay = 1000/int(new_rate)


            
        
                
        
        
        
                
        
