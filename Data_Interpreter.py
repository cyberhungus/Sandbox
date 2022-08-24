from threading import Thread 
from multiprocessing import Queue
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
import timeit
import imutils as imu

import testcy 
#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue,is_mock=False):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 200
        self.is_mock = is_mock
        self.qrHelp = cv.QRCodeDetector()
                

    def run(self):
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                processed_data_depth = self.interpret_data_depth(new_data[0])
                analysis_result_list = self.analyze_data_rgb(new_data[1])
                #analysis_result_list = self.analyze_data_rgb_qr(new_data[1])

                full_img = self.composite_depth_and_rgb(processed_data_depth,analysis_result_list)
                #processed_data_depth = cv.resize(processed_data_depth,dsize=None,fx=1.5,fy=1.5)


                #self.output.put_nowait(processed_data_depth)
                #self.output.put_nowait(processed_data_rgb)
                self.output.put_nowait(full_img)


    def analyze_data_rgb_qr(self, data):
        rval, info, points, qr = self.qrHelp.detectAndDecodeMulti(np.hstack([data,data]))
        print("QR CODE:",rval,info)
        cv.imshow("TEST",data)
        if cv.waitKey(10)==27:
            pass

    def composite_depth_and_rgb(self, depth, results):
        for item in results:
            cv.circle(depth,item[1],10,(255,0,255))
            cv.putText(depth,item[2],(item[1][0]-20,item[1][1]),0,0.5,(255,255,255))

        return depth


    def interpret_data_depth(self, data):
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

    def analyze_data_rgb(self, data):
        work_data_rgb = fc.video_cv(data)
        processed_data_rgb = self.find_contours(work_data_rgb)
        return processed_data_rgb

    def find_contours(self, data):
        print("type of data for rgb:",type(data),"---",data.shape)
        
        #greyscale = cv.cvtColor(data, cv.COLOR_BGR2GRAY)
        #blurred_greyscale = cv.GaussianBlur(data,(5,5),0)
        #thresh_blur_grey=cv.threshold(blurred_greyscale,(0,0,0),(100,255,100),0)[1]
        thresh_blur_grey = cv.inRange(data, (70, 0, 70), (100, 45, 100))
        contours = cv.findContours(thresh_blur_grey.copy(),cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = imu.grab_contours(contours)
        print("length of contours list:" , len(contours))
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

                

        #cv.drawContours(thresh_blur_grey,contours,-1,120,3)
        test_img = np.concatenate((data,np.array(Image.fromarray(thresh_blur_grey,"L").convert("RGB"))),axis=1)
        cv.imshow("TEST",test_img)
        if cv.waitKey(10)==27:
            pass
        #return thresh_blur_grey
        #return greyscale
        #return data
        return result_list

    def contour_processor(self, shape):
        if len(shape)>1:
            shape_name = "unk"
            perimeters = cv.arcLength(shape,True)
            corners = cv.approxPolyDP(shape,0.04*perimeters,True)
            return len(corners)
        else:
            return 0 

    def find_contour_center(self, contour):
        try:
            moment = cv.moments(contour)
            x_center = int(moment["m10"] / moment["m00"])
            y_center = int(moment["m01"] / moment["m00"])
            return (x_center, y_center)
        except:
            return (0,0)
        

