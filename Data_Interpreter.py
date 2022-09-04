
from cgitb import lookup
from threading import Thread 
from multiprocessing import Queue
from turtle import color
import frame_convert2 as fc
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
#from cv2 import aruco
import timeit
import imutils as imu
import os
from Object_Manager import Tree_Manager as tm

#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue,is_mock=False, has_trees = False):
        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 4000
        self.is_mock = is_mock

        self.shapes =[]

        self.tree_state = has_trees
        if self.tree_state == True:
            self.tree_manager = tm(10, 480,640)



              
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
        self.shapeThreshLow = (70,0,70)
        self.shapeThreshHigh = (100,45,100)
        self.minShapeSize = 40

        self.thresholdval = 20 

        self.shape_offset= 20

        filepath = os.getcwd()+"/assets/testfile.png"
        self.houseIMG = cv.imread(filepath,cv.IMREAD_COLOR)


        filepath = os.getcwd()+"/assets/tree.png"
        self.treeIMG = cv.imread(filepath,cv.IMREAD_UNCHANGED)
  # 
        self.lookup_table = self.generate_LUT()

        self.displaysize =(1920,1080)
        self.displayoffset = 50 

    def run(self):
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                #this section of the code is used to alter parameters in the data_interpreter from a diffent process 
                if type(new_data[0]) == str:
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
                    elif new_data[0]=="shapeThreshLow":
                        self.shapeThreshLow = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))

                    elif new_data[0]=="shapeThreshHigh":
                        self.shapeThreshHigh = (int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2]))      
                    
                    elif new_data[0]=="minShapeSize":
                        self.minShapeSize = int(new_data[1])  

                    elif new_data[0]=="newTrees":
                        if self.tree_state==True:
                            self.tree_manager.generate_new_tree_pos(int(new_data[1]))  

                    elif new_data[0]=="color_correct":
                        print("performing color correct")
                        self.calculate_color_correct((int(new_data[1][0]),int(new_data[1][1]),int(new_data[1][2])))
                    
                #this section checks for new image data and then runs the neccessary functions on that data 
                else:
                    #starttime = timeit.default_timer()
                    #processed_data_depth = self.c_height_calc(new_data[0])w


                    processed_data_depth = self.height_transform_lut(new_data[0])
                    line_data_depth = self.draw_height_lines(processed_data_depth)
                    aruco_list = self.read_aruco(new_data[1])
                    #analysis_result_list = self.analyze_data_rgb(new_data[1])
                    full_img = self.aruco_obj_placer(line_data_depth, aruco_list)
                    #self.shape_comparator(analysis_result_list)
                    #full_img = self.composite_depth_and_rgb(line_data_depth,analysis_result_list)

                    if self.tree_state == True:
                        full_img = self.tree_placer(full_img, self.tree_manager.get_Tree_Positions())


                    self.output.put_nowait(("ANALYZED",full_img))
                   # print("Time for color convert algorithm :", timeit.default_timer() - starttime)

    def read_aruco(self,img):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        aruco_dict = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_250)
        parameters =  cv.aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = cv.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        output=[]
        if ids is not None:
            for x in range(len(ids)):
               output.append((ids[x],corners[x]))
        return output

    def aruco_obj_placer(self, img, resultlist):
        data = img.copy()
        if resultlist is not None:
            if len(resultlist)>0:
                for item in resultlist:

                    for point in item[1][0]:
                        print("POINT",point)
                        cv.circle(data,(int(point[0]),int(point[1])),2,(0,0,222))
        return data

    def package_for_display(self):
        pass
        


    def generate_LUT(self):
        lookup_table = np.zeros((256,1,3),dtype=np.uint8)
        
        color_table=[]
        remainder = (255-self.waterlevel)/6
        for num in range(256):
            if num in range(0,int(self.waterlevel/2)):
                color_table.append(self.colorDeepWater)
            elif num in range(int(self.waterlevel/2),self.waterlevel):
                color_table.append(self.colorWater)            
            elif num in range(int(self.waterlevel),int(self.waterlevel+remainder)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel),int(self.waterlevel+remainder),self.colorA,self.colorB))  
                #color_table.append(self.colorA)
            elif num in range(int(self.waterlevel+remainder),int(self.waterlevel+remainder*2)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder),int(self.waterlevel+remainder*2),self.colorB,self.colorC))    
            elif num in range(int(self.waterlevel+remainder*2),int(self.waterlevel+remainder*3)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*2),int(self.waterlevel+remainder*3),self.colorC,self.colorD))   
            elif num in range(int(self.waterlevel+remainder*3),int(self.waterlevel+remainder*4)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*3),int(self.waterlevel+remainder*4),self.colorD,self.colorE))
            elif num in range(int(self.waterlevel+remainder*4),int(self.waterlevel+remainder*5)):
                 color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*4),int(self.waterlevel+remainder*5),self.colorE,self.colorF)) 
            elif num in range(int(self.waterlevel+remainder*5),int(self.waterlevel+remainder*6)):
                color_table.append(self.make_gradient_color(num, int(self.waterlevel+remainder*5),int(self.waterlevel+remainder*6),self.colorF, self.colorG))
                
            elif num in range(int(self.waterlevel+remainder*6),int(255)):
                color_table.append(self.colorG)   
            else:
                color_table.append([255,255,255])

       #     print(num, ":::",lookup_table[num],":::",color_table[num])
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
      #  print(percentage)
        newRed = colorMin[2] + percentage * (colorMax[2]- colorMin[2]);
        newGreen = colorMin[1] + percentage * (colorMax[1]- colorMin[1]);
        newBlue = colorMin[0] + percentage * (colorMax[0]- colorMin[0]);

        return (newRed,newGreen,newBlue)

    def height_transform_lut(self, data):
        
        data = cv.convertScaleAbs(data,alpha=0.06)
        data = Image.fromarray(data,"L").convert("RGB")
        data = np.array(data)
        return cv.LUT(data,self.lookup_table)



    def draw_height_lines(self,data):
        data_grey = Image.fromarray(data,"RGB").convert("L")
        data_grey = np.array(data_grey)
        canny = cv.Canny(data_grey, 0,255)
        line_pixels = canny[:,:]>0
        data[line_pixels]=self.lineBrown
        return data

    

    #todo: if the system remains shape based, this should prevent "flickering" in the shape detection 
    def shape_comparator(self, new_shapes):
        if len(self.shapes)==0:
            self.shapes=new_shapes
        else:
            for old_shape in self.shapes:
                for new_shape in new_shapes:
                    if (new_shape[1][0] <= old_shape[1][0]+self.shape_offset or new_shape[1][0] >= old_shape[1][0]-self.shape_offset) and (new_shape[1][1] <= old_shape[1][1]+self.shape_offset or new_shape[1][1] >= old_shape[1][1]-self.shape_offset):
                        print("same shape detected")



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
            pass


    def rgba_help(self, color, a_val):
        return (color[0],color[1],color[2],a_val)