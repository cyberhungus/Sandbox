from multiprocessing import Queue
from threading import Thread 
import cv2 
import numpy as np 

class Data_Visualizer:
    def __init__(self, inputQueue, placemarkers= True):
        self.input = inputQueue
        self.current_image_full = 0 
        self.current_image_rgb_raw = 0 
        self.current_image_depth = 0
        self.markerMode = placemarkers
        self.markersize = 250
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
        self.brightness_add = 0

    #the main function of the Data_Getter 
    def visualizer_runner(self):
        """
                
        This is the main function of this class. It receives data via a queue from the Data_Interpreter, then displays it. 
        This function is run in its' own process for performance reasons. See Main_Manager for more information. 
        This function may not only receive the final image for display, but also Debug-Images. 
        The type of image at hand is determined by the first position of the received tuple, as seen below.
        Via this mechanism, configuration options such as wether to display the ArUco markers and their size and brightness can be manipulated. 
  
        """

        while 1:
            if not self.input.empty():
                current_data = self.input.get_nowait()
                if current_data[0]=="ANALYZED":
                    self.current_image_full = current_data[1]
                    if self.markerMode==True:
                        self.current_image_full = self.place_ar_corners(self.current_image_full)
                elif current_data[0]=="RAW_RGB":
                    self.current_image_rgb_raw = current_data[1]
                elif current_data[0]=="DEPTH":
                    self.current_image_depth = current_data[1]
                elif current_data[0]=="SHOW_MARKERS":
                    self.markerMode = bool(current_data[1])
                elif current_data[0]=="MARKER_SIZE":
                    self.markersize=int(current_data[1])
                    self.ar0 = cv2.imread("ar0.png",cv2.IMREAD_COLOR)
                    self.ar0 = cv2.resize(self.ar0,(self.markersize,self.markersize))
                    self.ar0 = cv2.rotate(self.ar0, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    self.ar1 = cv2.imread("ar1.png",cv2.IMREAD_COLOR)
                    self.ar1 = cv2.resize(self.ar1,(self.markersize,self.markersize))
                    self.ar1 = cv2.rotate(self.ar1, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    self.ar2 = cv2.imread("ar2.png",cv2.IMREAD_COLOR)
                    self.ar2 = cv2.resize(self.ar2,(self.markersize,self.markersize))
                    self.ar2 = cv2.rotate(self.ar2, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    self.ar3 = cv2.imread("ar3.png",cv2.IMREAD_COLOR)
                    self.ar3 = cv2.resize(self.ar3,(self.markersize,self.markersize))
                   # self.ar3 = cv2.rotate(self.ar3, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif current_data[0]=="BRIGHTNESS":
                    self.brightness_add = int(current_data[1])
                try:

                    cv2.namedWindow("OUTPUT_FULLSCREEN", cv2.WND_PROP_FULLSCREEN)
                  #  cv2.moveWindow("OUTPUT_FULLSCREEN", 3840,0)
                    cv2.setWindowProperty("OUTPUT_FULLSCREEN",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                    cv2.imshow("OUTPUT_FULLSCREEN",self.current_image_full)
                    cv2.imshow("OUTPUT_CONTROL",cv2.resize(self.current_image_full,(400,400)))
                    cv2.imshow("RGB_Control",cv2.resize(self.current_image_rgb_raw,(400,400)))
                    cv2.imshow("Depth_Control",cv2.resize(self.current_image_depth,(400,400)))
                    cv2.moveWindow("RGB_Control", 800,0)
                    cv2.moveWindow("Depth_Control", 400,0)
                    cv2.moveWindow("OUTPUT_CONTROL", 0,0)
                except Exception as ex:
                    print("Error in Visualizer: ", ex)
                if cv2.waitKey(10) == 27:
                    break
    
    def place_ar_corners(self, image):
        """
        This function places ArUco-markers in the corners of an image. 
        This can be turned on and off in the UI. 

        :param np.array image: The image on which the ArUco markers shall be drawn. 

        :returns: The image with the added ArUco markers. 
        :rtype: np.array
        
        """

        try:
            if np.max(image,axis=-2).all()== np.min(image,axis=-2).all():
                print(np.max(image,axis=-2)[0])
                image[np.where((image==np.max(image,axis=-2)[0]).all(axis=2))] = [255,255,255]

            image[np.where((image==[0,0,0]).all(axis=2))] = [255,255,255]
            image = cv2.resize(image,(self.output_width,self.output_height))
            w,h,c = image.shape
            image[0:self.markersize,0:self.markersize] = self.increase_brightness(self.ar0,value=self.brightness_add)
            image[w-self.markersize:w,0:self.markersize] = self.increase_brightness(self.ar1,value=self.brightness_add)
            image[0:self.markersize, h-self.markersize:h] = self.increase_brightness(self.ar2,value=self.brightness_add)
            image[w-self.markersize:w,h-self.markersize:h] = self.increase_brightness(self.ar3,value=self.brightness_add)
            self.current_image_full = np.zeros((1920,1080,3),dtype=np.uint8)
            return image 
        except Exception as ex:
            print("DATA VIS ERROR", ex)
            image = np.zeros((self.output_height,self.output_width,3),dtype=np.uint8)
            image[np.where((image==[0,0,0]).all(axis=2))] = [255,255,255]
            w,h,c = image.shape
            image[0:self.markersize,0:self.markersize] = self.ar0
            image[w-self.markersize:w,0:self.markersize] = self.ar1
            image[0:self.markersize, h-self.markersize:h] = self.ar2
            image[w-self.markersize:w,h-self.markersize:h] = self.ar3
            return image 


                

    def increase_brightness(self,img, value=30):
        """
        This function can alter the brightness of an np.array image. 

        :param np.array img: The image which is to be altered. 
        :param int value: The amount by which the image is to be brightened. 


        :returns: The brightened image. 
        :rtype: np.array
        
        """

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return img