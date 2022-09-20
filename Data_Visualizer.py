from multiprocessing import Queue
from threading import Thread 
import cv2 
import numpy as np 

class Data_Visualizer:
    def __init__(self, inputQueue, placemarkers= True):
        self.input = inputQueue
        self.current_image_full = 0 
        self.current_image_rgb_raw = 0 
        self.depth_control = 0
        self.markerMode = placemarkers
        self.markersize = 75
        self.ar0 = cv2.imread("ar0.png",cv2.IMREAD_COLOR)
        self.ar0 = cv2.resize(self.ar0,(self.markersize,self.markersize))
        self.ar1 = cv2.imread("ar1.png",cv2.IMREAD_COLOR)
        self.ar1 = cv2.resize(self.ar1,(self.markersize,self.markersize))
        self.ar2 = cv2.imread("ar2.png",cv2.IMREAD_COLOR)
        self.ar2 = cv2.resize(self.ar2,(self.markersize,self.markersize))
        self.ar3 = cv2.imread("ar3.png",cv2.IMREAD_COLOR)
        self.ar3 = cv2.resize(self.ar3,(self.markersize,self.markersize))
        self.output_width=1920
        self.output_height=1080
        self.brightness_add = 90 

    #the main function of the Data_Getter 
    def visualizer_runner(self):
        while 1:
            if not self.input.empty():
                current_data = self.input.get_nowait()
                #the data_visualizer may receive different images apart frotm the "normal" depth/color tuple. a String at [0] position denotes this 
                if current_data[0]=="ANALYZED":
                    self.current_image_full = current_data[1]
                    if self.markerMode==True:
                        self.current_image_full = self.place_ar_corners(self.current_image_full)
                elif current_data[0]=="RAW_RGB":
                    self.current_image_rgb_raw = current_data[1]
                elif current_data[0]=="DEPTH_TEST":
                    self.depth_control = current_data[1]
                elif current_data[0]=="SHOW_MARKERS":
                    self.markerMode = bool(current_data[1])
                elif current_data[0]=="MARKER_SIZE":
                    self.markersize=int(current_data[1])
                    self.ar0 = cv2.imread("ar0.png",cv2.IMREAD_COLOR)
                    self.ar0 = cv2.resize(self.ar0,(self.markersize,self.markersize))
                    self.ar1 = cv2.imread("ar1.png",cv2.IMREAD_COLOR)
                    self.ar1 = cv2.resize(self.ar1,(self.markersize,self.markersize))
                    self.ar2 = cv2.imread("ar2.png",cv2.IMREAD_COLOR)
                    self.ar2 = cv2.resize(self.ar2,(self.markersize,self.markersize))
                    self.ar3 = cv2.imread("ar3.png",cv2.IMREAD_COLOR)
                    self.ar3 = cv2.resize(self.ar3,(self.markersize,self.markersize))
                elif current_data[0]=="MARKER_SIZE":
                    self.markersize=int(current_data[1])
                try:
                    cv2.namedWindow("OUTPUT_FULLSCREEN", cv2.WND_PROP_FULLSCREEN)
                    cv2.moveWindow("OUTPUT_FULLSCREEN", 3840,0)
                    cv2.setWindowProperty("OUTPUT_FULLSCREEN",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                    cv2.imshow("OUTPUT_FULLSCREEN",self.get_current())
                    cv2.imshow("OUTPUT_CONTROL",cv2.resize(self.get_current(),(400,400)))
                    cv2.imshow("RGB_Control",cv2.resize(self.current_image_rgb_raw,(400,400)))
                    cv2.imshow("Depth_Control",cv2.resize(self.depth_control,(400,400)))
                    cv2.moveWindow("RGB_Control", 800,0)
                    cv2.moveWindow("Depth_Control", 400,0)
                    cv2.moveWindow("OUTPUT_CONTROL", 0,0)
                except Exception as ex:
                    print("Error in Visualizer: ", ex)
                if cv2.waitKey(10) == 27:
                    break

    def get_current(self):
        return self.current_image_full

    #puts aruco markers in the corner of the displayed image. this can be toggled in the UI 
    def place_ar_corners(self, image):
        try:
            image[np.where((image==[1,1,1]).all(axis=2))] = [255,255,255]
            image = cv2.resize(image,(self.output_width,self.output_height))
            w,h,c = image.shape
            image[0:self.markersize,0:self.markersize] = self.increase_brightness(self.ar0,value=self.brightness_add)
            image[w-self.markersize:w,0:self.markersize] = self.increase_brightness(self.ar1,value=self.brightness_add)
            image[0:self.markersize, h-self.markersize:h] = self.increase_brightness(self.ar2,value=self.brightness_add)
            image[w-self.markersize:w,h-self.markersize:h] = self.increase_brightness(self.ar3,value=self.brightness_add)
            return image 
        except Exception as ex:
            image = np.zeros((self.output_width,self.output_height,3),dtype=np.uint8)
            image[np.where((image==[0,0,0]).all(axis=2))] = [255,255,255]
            w,h,c = image.shape
            image[0:self.markersize,0:self.markersize] = self.ar0
            image[w-self.markersize:w,0:self.markersize] = self.ar1
            image[0:self.markersize, h-self.markersize:h] = self.ar2
            image[w-self.markersize:w,h-self.markersize:h] = self.ar3
            return image 


                

    def increase_brightness(self,img, value=30):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img