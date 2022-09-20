
from cgitb import lookup
from ctypes.wintypes import SIZE
from queue import Empty
from threading import Thread 
from multiprocessing import Queue
from turtle import color
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
import cv2.aruco as aruco
#from cv2 import aruco
import timeit
import imutils as imu
import os
from Object_Manager import Tree_Manager as tm

#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue, has_trees = False):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 30

        self.shapes =[]

        self.tree_state = has_trees
        if self.tree_state == True:
            self.tree_manager = tm(10, 480,640)


        self.borders_set = False
        self.border_mask = 0
              
        #Region storing variables 
        self.lineBrown = (10,55,100)
        self.colorA = (0,50,0)
        self.colorB = (0,100,100)
        self.colorC = (0,150,100)
        self.colorD = (0,200,100)
        self.colorE = (120,150,100)
        self.colorF = (200,200,100)
        self.colorF = (250,200,200)
        self.colorG = (250,250,0)
        self.colorWater = (200,50,0)
        self.colorDeepWater = (250,50,0)

        filepath = os.getcwd()+"/assets/newTopoItem.png"
        self.houseIMG = cv.imread(filepath,cv.IMREAD_UNCHANGED)


        filepath = os.getcwd()+"/assets/tree.png"
        self.treeIMG = cv.imread(filepath,cv.IMREAD_UNCHANGED)
  #     
        self.lookup_table = self.generate_LUT()

        self.displaysize =(1920,1080)

        self.displayoffset = 50 


        self.maskpoints = [[0,0],[1080,1920]]
        self.lastMaskPoints = 0 
        self.standardmask = [[0,0],[1920,0],[0,1080],[1920,1080]]


        self.realArucoSizeMM = 26.28
        self.focal_length = 1233.24
        self.markerSizePixel = 0 
        self.camera_height = 1 

    #main function, checks for settings alteration, then takes new image data, analyses it, and sends it on to the Data_Visualizer 
    def run(self):
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                #this section of the code is used to alter parameters in the data_interpreter from a diffent process 
                if type(new_data[0]) == str:
                    self.argDecoder(new_data)
                #this section takes new image data and then runs the neccessary functions on that data 
                else:
                    starttime = timeit.default_timer()
                    
                    

                    self.findmask(new_data[1])
                    print(self.maskpoints)
          
                    processed_data_depth = self.height_transform_lut(new_data[0])

                    line_data_depth = self.draw_height_lines(new_data[0],processed_data_depth)

                    full_img = self.process_aruco(new_data[1],line_data_depth)
                   
                    self.output.put_nowait(("ANALYZED",self.applymask(full_img)))
                    print("Time for color convert algorithm :", timeit.default_timer() - starttime)




    #Finds the masking points shown by the projector
    #img= an np.array styled image - in this case the raw RGB photo
    def findmask(self, img):
            self.lastMaskPoints= self.maskpoints
            self.maskpoints = []
            arucofound = self.findArucoMarkers(img)
            # loop through all the markers and augment each one
            if arucofound:
                if len(arucofound[0])>=4:
                    for bbox, codeID in zip(arucofound[0], arucofound[1]):
                        if codeID in range(0,4):
                            center_calc_arr = []
                            for point in bbox[0]:
                                center_calc_arr.append([int(point[0]),int(point[1])])
                            sorted_points = self.sortpoints(center_calc_arr)
                            length = sorted_points[1]-sorted_points[0]                   
                            mid = self.calc_middle(center_calc_arr)
                            self.maskpoints.append(mid)
                self.maskpoints = self.sortpoints(self.maskpoints)
            else:

                self.maskpoints = self.standardmask





    #Sorts points so they are usable in the Aruco-AR Function 
    def sortpoints(self,pts):
        try:
            pts = np.array(pts)
            rect = np.zeros((4, 2), dtype = "float32")
            s = pts.sum(axis = 1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis = 1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            return rect
        except Exception as ex:
            return self.sortpoints(self.lastMaskPoints)

    #Places the generated image onto the area marked by arucos 
    def applymask(self, imgAug):
        img = np.ones((1080,1920,3),dtype=np.uint8)
        h, w, c = imgAug.shape
        pts1 = np.array(np.array(self.maskpoints))
       # print("applymask new points", pts1)
        pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
        matrix, _ = cv.findHomography(pts1, pts2)
        imgout = cv.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
        cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
        imgout = img + imgout
        return imgout

    #wraps the Aruco detection and placements functionalities 
    def process_aruco(self, img_rgb, img_depth):
        img = img_rgb.copy()
        new_img=img_depth
        arucofound = self.findArucoMarkers(img)
        if arucofound:
            if len(arucofound[0])!=0:
                for bbox, id in zip(arucofound[0], arucofound[1]):
                    if id == 10 :   
                        new_img = self.arucoAug(bbox, id, img_depth, self.houseIMG)
                return new_img
            else:
                return new_img
        else:
            return new_img
    

    #detects arucomarkers 
    def findArucoMarkers(self,img, markerSize = 4, totalMarkers=100, draw=False):         
        try:
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
            arucoDict = aruco.Dictionary_get(key)
            arucoParam = aruco.DetectorParameters_create()
            bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
            print(ids)
            if draw:
                aruco.drawDetectedMarkers(img, bboxs)
            return [bboxs, ids]
        except Exception as ex:
            print("aruco finder exception",ex)
            return []


    #draws an image on the area marked by aruco 
    def arucoAug(self,bbox, id, img, imgAug, drawId = True):
        tl = bbox[0][0][0], bbox[0][0][1]
        tr = bbox[0][1][0], bbox[0][1][1]
        br = bbox[0][2][0], bbox[0][2][1]
        bl = bbox[0][3][0], bbox[0][3][1]
        h, w, c = imgAug.shape
        pts1 = np.array([tl, tr, br, bl])
        pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
        matrix, _ = cv.findHomography(pts2, pts1)
        imgout = cv.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
        cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
        imgout = img + imgout
        return imgout

    #determines the middle of an aruco marker ( or any number of points)
    #points = list of 2D vectors 
    def calc_middle(self, points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid = (int(sum(x) / len(points)),int( sum(y) / len(points)))
        return centroid

        
    #draws the height lines found in color image onto the height data 
    def draw_height_lines(self,data,data_lut):
        data = data.astype("uint8")
        try:

            canny = cv.Canny(data, 0,255)
            line_pixels = canny[:,:]>0
            data_lut[line_pixels]=self.lineBrown
            return data_lut
        except Exception as ex:
            print("Canny Error",ex)
            return data

    #generates an greyscale image to be analysed with Canny 
    def greyscale_for_height_lines(self, arr):
        output = cv.convertScaleAbs(arr,alpha=0.5)
        return output

    #generates a Lookup Table 
    def generate_LUT(self):
        lookup_table = np.zeros((256,1,3),dtype=np.uint8)
        
        color_table=[]
        remainder = (255-self.waterlevel)/6
        for num in range(256):
            if num in range(0,int(self.waterlevel/2)):
                color_table.append(self.colorG)   
                
            elif num in range(int(self.waterlevel/2),self.waterlevel):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel/2),int(self.waterlevel),self.colorG, self.colorF))
                
                         
            elif num in range(int(self.waterlevel),int(self.waterlevel+remainder)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel),int(self.waterlevel+remainder),self.colorF,self.colorE)) 
            elif num in range(int(self.waterlevel+remainder),int(self.waterlevel+remainder*2)):
                 color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*1),int(self.waterlevel+remainder*2),self.colorE,self.colorD))
            elif num in range(int(self.waterlevel+remainder*2),int(self.waterlevel+remainder*3)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*2),int(self.waterlevel+remainder*3),self.colorD,self.colorC))   
            elif num in range(int(self.waterlevel+remainder*3),int(self.waterlevel+remainder*4)):
               color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*3),int(self.waterlevel+remainder*4),self.colorC,self.colorB))    
            elif num in range(int(self.waterlevel+remainder*4),int(self.waterlevel+remainder*5)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*4),int(self.waterlevel+remainder*5),self.colorB,self.colorA))  
            elif num in range(int(self.waterlevel+remainder*5),int(self.waterlevel+remainder*6)):
                color_table.append(self.colorWater)   
            elif num in range(int(self.waterlevel+remainder*6),int(255)):
                color_table.append(self.colorDeepWater)
            else:
                color_table.append([255,0,255])
            #red
            lookup_table[num,0,0]= color_table[num][0]
            #green
            lookup_table[num,0,1]=color_table[num][1]
            #blue
            lookup_table[num,0,2]=color_table[num][2]
        return lookup_table

    def make_gradient_color(self,value,rangeMin,rangeMax, colorMin, colorMax):
        scale = rangeMax-rangeMin
        distance = value-rangeMin
        percentage = 100 * float(distance)/float(scale)
        percentage = percentage/100
        newRed = colorMin[2] + percentage * (colorMax[2]- colorMin[2]);
        newGreen = colorMin[1] + percentage * (colorMax[1]- colorMin[1]);
        newBlue = colorMin[0] + percentage * (colorMax[0]- colorMin[0]);
        return (newRed,newGreen,newBlue)


    #transforms the height data into a colour image by using a lookup table 
    def height_transform_lut(self, data): 
        data = cv.convertScaleAbs(data,alpha=0.07)
        self.output.put_nowait(("DEPTH_TEST",data))

        data = Image.fromarray(data,"L").convert("RGB")
        data = np.array(data)
        return cv.LUT(data,self.lookup_table)

    #places trees 
    def tree_placer(self,img, pos_list):
        rimg = Image.fromarray(img,"RGB").convert("RGBA")
        return_img = np.array(rimg)

        for item in pos_list:
            color_at_pos = (return_img[item[0]][item[1]][0],return_img[item[0]][item[1]][1],return_img[item[0]][item[1]][2],return_img[item[0]][item[1]][3])
            if color_at_pos == self.rgba_help(self.colorA,255):
                self.plant_tree(5,item,return_img)
            elif color_at_pos == self.rgba_help(self.colorB,255):
                self.plant_tree(10,item,return_img)
            elif color_at_pos == self.rgba_help(self.colorC,255):
                self.plant_tree(15,item,return_img)
            elif color_at_pos == self.rgba_help(self.colorD,255):
                self.plant_tree(20,item,return_img)


            cv.circle(return_img,item,5,(0,220,0))
            #cv.putText(img,str(color_at_pos),item,0,0.5,(255,255,255))
        return return_img




    def plant_tree(self,size,pos,img):
        x_offset = size
        y_offset = size
        x_min,y_min = pos[0]-x_offset,pos[1]-y_offset
        x_max,y_max = pos[0]+x_offset,pos[1]+y_offset
        tree = self.treeIMG.copy()
        resized = cv.resize(tree, (2*x_offset,2*y_offset), interpolation = cv.INTER_AREA)
        try:
            #superimposes image with transparency
            alpha_s = resized[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s
            for c in range(3):
                img[y_min:y_max,x_min:x_max,c] = (alpha_s * resized[:, :, c] + alpha_l * img[y_min:y_max,x_min:x_max, c])
        except Exception as ex :
            print(ex)


    def rgba_help(self, color, a_val):
        return (color[0],color[1],color[2],a_val)

    def argDecoder(self, datatuple):
            new_data=datatuple
            if new_data[0]=="waterlevel":
                self.waterlevel = int(new_data[1])
                        
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="colorA":
                self.colorA = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorB":
                self.colorB = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorC":
                self.colorC = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorD":
                self.colorD = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                        
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="colorE":
                self.colorE = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorF":
                self.colorF = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorWater":
                self.colorWater = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorDeepWater":
                self.colorWater = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorA":
                self.colorA = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
        
            elif new_data[0]=="arrcolorB":
                self.colorB = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorC":
                self.colorC = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorD":
                self.colorD = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="arrcolorE":
                self.colorE = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorF":
                self.colorF = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorWater":
                self.colorWater = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="arrcolorDeepWater":
                self.colorDeepWater = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                self.lookup_table = self.generate_LUT()                      


            elif new_data[0]=="newTrees":
                if self.tree_state==True:
                    self.tree_manager.generate_new_tree_pos(int(new_data[1]))  
