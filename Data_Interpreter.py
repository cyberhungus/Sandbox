from ast import Str
from configparser import Interpolation
from threading import Thread 
from multiprocessing import Queue
from tokenize import String
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
import timeit
import imutils as imu
import os

#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue,is_mock=False):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 200
        self.is_mock = is_mock

        self.shapes =[]



              
        #Region storing variables 
        self.colorA = (0,50,0)
        self.colorB = (0,100,100)
        self.colorC = (0,150,100)
        self.colorD = (0,200,100)
        self.colorWater = (200,50,0)
        self.shapeThreshLow = (70,0,70)
        self.shapeThreshHigh = (100,45,100)
        self.minShapeSize = 40

        self.thresholdval = 20 

        self.shape_offset= 20

        filepath = os.getcwd()+"/assets/testfile.png"
        self.houseIMG = cv.imread(filepath,cv.IMREAD_COLOR)


    def run(self):
#        self.qrHelp = cv.QRCodeDetector()
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                #this section of the code is used to alter parameters in the data_interpreter from a diffent process 
                if type(new_data[0]) == str:
                    if new_data[0]=="waterlevel":
                        self.waterlevel = int(new_data[1])

                    elif new_data[0]=="colorA":
                        self.colorA = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="colorB":
                        self.colorB = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="colorC":
                        self.colorC = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="colorD":
                        self.colorD = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="colorWater":
                        self.colorWater = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                    elif new_data[0]=="arrcolorA":
                        self.colorA = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                    elif new_data[0]=="arrcolorB":
                        self.colorB = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                    elif new_data[0]=="arrcolorC":
                        self.colorC = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                    elif new_data[0]=="arrcolorD":
                        self.colorD = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                    elif new_data[0]=="arrcolorWater":
                        self.colorWater = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                    elif new_data[0]=="shapeThreshLow":
                        self.shapeThreshLow = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="shapeThreshHigh":
                        self.shapeThreshHigh = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))      
                    
                    elif new_data[0]=="minShapeSize":
                        self.minShapeSize = int(new_data[1])  

                    elif new_data[0]=="color_correct":
                        print("performing color correct")
                        self.perform_color_correct((int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2])))
                    
                #this section checks for new image data and then runs the neccessary functions on that data 
                else:
                    starttime = timeit.default_timer()
                    processed_data_depth = self.interpret_data_depth(new_data[0])
                    analysis_result_list = self.analyze_data_rgb(new_data[1])
                    #analysis_result_list = self.analyze_data_rgb_qr(new_data[1])
                    self.shape_comparator(analysis_result_list)
                    full_img = self.composite_depth_and_rgb(processed_data_depth,analysis_result_list)
                    #processed_data_depth = cv.resize(processed_data_depth,dsize=None,fx=1.5,fy=1.5)
                    #self.output.put_nowait(processed_data_depth)
                    #self.output.put_nowait(processed_data_rgb)
                    self.output.put_nowait(full_img)
                  #  self.output.put_nowait(processed_data_depth)
                    print("Time for color convert algorithm :", timeit.default_timer() - starttime)


    def analyze_data_rgb_qr(self, data):
        rval, info, points, qr = self.qrHelp.detectAndDecodeMulti(np.hstack([data,data]))
        print("QR CODE:",rval,info)
        cv.imshow("TEST",data)
        if cv.waitKey(10)==27:
            pass

    #sets threshold values for better image and shape recognition based on a color value 
    def perform_color_correct(self, input_color):
        if input_color[0] >=250 or input_color[0] >=250 or input_color[0] >=250:
            print("illegal color")
        else:
            print("input_color is ", input_color, type(input_color))
            print(type(self.shapeThreshHigh))
            self.shapeThreshLow = ((input_color[2]-self.thresholdval),(input_color[1]-self.thresholdval),(input_color[0]-self.thresholdval))
            self.shapeThreshHigh = ((input_color[2]+self.thresholdval),(input_color[1]+self.thresholdval),(input_color[0]+self.thresholdval))
            print(type(self.shapeThreshHigh),self.shapeThreshHigh)

    #combines regular depth camera data and AR data 
    def composite_depth_and_rgb(self, depth, results):
        for item in results:
            cv.circle(depth,item[1],10,(255,0,255))
            cv.putText(depth,item[2],(item[1][0]-20,item[1][1]),0,0.5,(255,255,255))
            x_offset = 10 
            y_offset = 10 
            x_min,y_min = item[1][0]-x_offset,item[1][1]-y_offset
            x_max,y_max = item[1][0]+x_offset,item[1][1]+y_offset
            housecpy = self.houseIMG.copy()
            resized = cv.resize(housecpy, (2*x_offset,2*y_offset), interpolation = cv.INTER_AREA)
            try:
                depth[y_min:y_max,x_min:x_max] = resized
            except:
                print("error placing ar marker ")
        return depth


    def interpret_data_depth(self, data):
        #make the grayscale data into a rgb data array and apply filters
        #print("interpreting data")
        work_data = self.do_pretty_rgb(data)
        col_data = self.c_height_calc(work_data)
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
        output = np.zeros((arr.shape[0],arr.shape[1]),dtype=np.uint8)
        mult = self.waterlevel/4
        mult= int(mult)
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
        data[np.all(data == [250,250,250], axis=-1)] = self.colorD
        #landC
        data[np.all(data == [200,200,200], axis=-1)] = self.colorC
        #landB
        data[np.all(data == [150,150,150], axis=-1)] = self.colorB
        #landA
        data[np.all(data == [100,100,100], axis=-1)] = self.colorA
        #water
        data[np.all(data == [50,50,50], axis=-1)] = self.colorWater
        #debug
        #data[np.all(data > [50,50,50], axis=-1)] = (200,50,200)

        return data

    def analyze_data_rgb(self, data):
        work_data_rgb = fc.video_cv(data)
        processed_data_rgb = self.find_contours(work_data_rgb)
        return processed_data_rgb

    def find_contours(self, data):
        #print("type of data for rgb:",type(data),"---",data.shape)
        
        #greyscale = cv.cvtColor(data, cv.COLOR_BGR2GRAY)
        #blurred_greyscale = cv.GaussianBlur(data,(5,5),0)
        #thresh_blur_grey=cv.threshold(blurred_greyscale,(0,0,0),(100,255,100),0)[1]
        thresh_blur_grey = cv.inRange(data, self.shapeThreshLow ,self.shapeThreshHigh)
        contours = cv.findContours(thresh_blur_grey.copy(),cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = imu.grab_contours(contours)
        #print("length of contours list:" , len(contours))
        result_list = []
        for contour in contours:
            corn_number = self.contour_processor(contour)
            if corn_number == 0:
                pass
            elif corn_number == 3:
                center_tuple = self.find_contour_center(contour)
                if center_tuple != (0,0):
                    result_list.append([contour,center_tuple,"tri"])
            elif corn_number == 4:
                center_tuple = self.find_contour_center(contour)
                if center_tuple != (0,0):
                    result_list.append([contour,center_tuple,"sqr"])
            elif corn_number == 5:
                center_tuple = self.find_contour_center(contour)
                if center_tuple != (0,0):
                    result_list.append([contour,center_tuple,"pent"])
            elif corn_number == 6:
                center_tuple = self.find_contour_center(contour)
                if center_tuple != (0,0):
                    result_list.append([contour,center_tuple,"hex"])
            elif corn_number == 8:
                center_tuple = self.find_contour_center(contour)
                if center_tuple != (0,0):
                    result_list.append([contour,center_tuple,"oct"])

        test_img = np.concatenate((data,np.array(Image.fromarray(thresh_blur_grey,"L").convert("RGB"))),axis=1)
        cv.imshow("TEST",test_img)
        if cv.waitKey(10)==27:
            pass

        return result_list

    #this function determines the number of corners a shape has 
    def contour_processor(self, shape):
        if len(shape)>self.minShapeSize:
            perimeters = cv.arcLength(shape,True)
            corners = cv.approxPolyDP(shape,0.04*perimeters,True)
            return len(corners)
        else:
            return 0 

    #determines the middle of a shape, which is where superimposed components are placed 
    def find_contour_center(self, contour):
        try:
            moment = cv.moments(contour)
            x_center = int(moment["m10"] / moment["m00"])
            y_center = int(moment["m01"] / moment["m00"])
            return (x_center, y_center)
        except:
            return (0,0)
        


    def shape_comparator(self, new_shapes):
        if len(self.shapes)==0:
            self.shapes=new_shapes
        else:
            for old_shape in self.shapes:
                for new_shape in new_shapes:
                    if (new_shape[1][0] <= old_shape[1][0]+self.shape_offset or new_shape[1][0] >= old_shape[1][0]-self.shape_offset) and (new_shape[1][1] <= old_shape[1][1]+self.shape_offset or new_shape[1][1] >= old_shape[1][1]-self.shape_offset):
                        print("same shape detected")

