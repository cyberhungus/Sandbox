

from queue import Empty
from threading import Thread 
from multiprocessing import Queue
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
import cv2.aruco as aruco
import timeit
import imutils as imu
import os
from Object_Manager import Tree_Manager as tm

#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue, pipe, has_trees = False):

        self.queue = pipe 
       

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
        self.houseIMG = cv.imread(filepath,cv.IMREAD_COLOR)

        filepath = os.getcwd()+"/assets/garten.png"
        self.gardenIMG = cv.imread(filepath,cv.IMREAD_COLOR)


        filepath = os.getcwd()+"/assets/tree.png"
        self.treeIMG = cv.imread(filepath,cv.IMREAD_UNCHANGED)
  #     
        self.lookup_table = self.generate_LUT()

        self.displaysize =(1920,1080)

        self.displayoffset = 50 


        self.maskpoints = [[0,0],[1080,1920]]
        self.lastMaskPoints = 0 
        self.standardmask = [[0,0],[1920,0],[0,1080],[1920,1080]]

        self.depthBrightness = 0.01


        self.realArucoSizeMM = 26.28
        self.focal_length = 1233.24
        self.markerSizePixel = 0 
        self.camera_height = 1 

        self.heightLineMode = True

        self.firstOffset = -50
        self.secondOffset = 0 


    def run(self):
        """
        This is the main function of this class. It receives data via a queue from a Data_Getter, then interprets it and sends it to the Data_Visualizer. 
        This function is run in its' own process for performance reasons. See Main_Manager for more information. 
        This function may also receive instructions to change the classes' property via the abovementioned queue. 

        """
        while 1:
            if not self.input.empty():
                new_data = self.input.get_nowait()
                if type(new_data[0]) == str:
                    self.argDecoder(new_data)

                else:
                    starttime = timeit.default_timer()
                    self.findmask(new_data[1])
                    self.output.put_nowait(("RAW_RGB",new_data[1]))
                    #cv.imshow("test",cv.resize(self.four_point_transform(new_data[1],self.maskpoints),(500,500)))
                    #cv.waitKey(1)
                   # depth = self.four_point_transform(new_data[0],self.maskpoints)
                    depth=new_data[0]
                    processed_data_depth = self.height_transform_lut(depth)
                    if self.heightLineMode==True:
                        processed_data_depth = self.draw_height_lines(processed_data_depth)
                    full_img = self.process_aruco(new_data[1],processed_data_depth)
                 
                    self.output.put_nowait(("ANALYZED",self.applymask(full_img)))
                   # self.output.put_nowait(("ANALYZED",full_img))
                    print("Time for color convert algorithm :", timeit.default_timer() - starttime)



    def four_point_transform(self, image, pts):
        # obtain a consistent order of the points and unpack them
        # individually
        rect = self.sortpoints(pts)
        (tl, tr, br, bl) = rect
        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
	        [0, 0],
	        [maxWidth - 1, 0],
	        [maxWidth - 1, maxHeight - 1],
	        [0, maxHeight - 1]], dtype = "float32")
        # compute the perspective transform matrix and then apply it
        M = cv.getPerspectiveTransform(rect, dst)
        warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))
        # return the warped image
        return warped




    def findmask(self, img):
        """ Finds the masking points circumscribing the display area - i.e. ArUco Markers 0 through 3. 
            The center of said markers is the determined, and the four markers are sorted to be used as a mask. 

            :param np.array img: The image to be examined for ArUco markers. 
        
        """
        self.lastMaskPoints= self.maskpoints
        self.maskpoints = []
        arucofound = self.findArucoMarkers(img)
        if arucofound:
            if len(arucofound[0])>=4:
                for bbox, codeID in zip(arucofound[0], arucofound[1]):
                    if codeID in range(0,4):
                        center_calc_arr = []
                        for point in bbox[0]:
                            center_calc_arr.append([int(point[0]),int(point[1])])
                        sorted_points = self.sortpoints(center_calc_arr)
 
                        if codeID == 0: 
                            mid = sorted_points[0]
                        elif codeID==1:
                            mid = sorted_points[3]
                        elif codeID==2:
                            mid = sorted_points[2]
                        elif codeID==3:
                            mid = sorted_points[1]
                        #mid = self.calc_middle(center_calc_arr)
                        self.maskpoints.append(mid)
            self.maskpoints = self.sortpoints(self.maskpoints)
        else:
            self.maskpoints = self.standardmask


    def sortpoints(self,pts):
        """Sorts points into the shape of "TopLeft TopRight BottomRight BottomLeft". This is done for ArUco marking purposes.
        If sorting the points is not possible, the variable self.lastMaskPoints is returned. 

        :param list pts: Points to be sorted. 

        :return: The sorted list of points 
        :rtype: np.array
        """
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

 
    def applymask(self, imgAug):
        """
        Places the generated image onto the area marked by arucos. 

        :param np.array imgAug: The image to be projected unto the masking area. 

        
        :return: The image to be shown by the projector.
        :rtype: np.array
        
        """
        self.maskpoints += (self.firstOffset,self.secondOffset)

        img = np.ones((1080,1920,3),dtype=np.uint8)
        h, w, c = imgAug.shape
        pts1 = np.array(np.array(self.maskpoints))
        pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
        matrix, _ = cv.findHomography(pts1, pts2)
        imgout = cv.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
        cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
        imgout = img + imgout
        return imgout

    def process_aruco(self, img_rgb, img_depth):
        """Wraps the Aruco detection and augmentation functionalities in a single function. Places the augmentation images on the depth data image. 
        This is not used for corner detection, but solely for placing graphics unto the image that is to be projected. 

        :param np.array img_rgb: The RGB data received via Queue from a Data_Getter. This image acts as the source of the aruco markers. 
        :param np.array img_depth: The depth data received via Queue from a Data_Getter. This image acts as the destination for the augmentation images. 

        :return: The augmented (or not, in case there were no markers in the image) image. 
        :rtype: np.array

        """
        img = img_rgb.copy()
        new_img=img_depth
        arucofound = self.findArucoMarkers(img)
        if arucofound:
            if len(arucofound[0])!=0:
                for bbox, id in zip(arucofound[0], arucofound[1]):

                    if id not in range(0,4):
                        print("Proces Aruco" , bbox,id)
                        if id == 10 :   
                            new_img = self.arucoAug(bbox, new_img, self.houseIMG, expandSize=0)
                        elif id == 9:
                            new_img = self.arucoAug(bbox, new_img, self.gardenIMG, expandSize= 40)
                return new_img
            else:
                return new_img
        else:
            return new_img
    
    def findArucoMarkers(self,img, markerSize = 4, totalMarkers=100):      
        """Detects aruco markers in an image. 
        :param np.array img: The image in which to detect the aruco markers. 
        :param int markerSize: The size of the markers. This value can be determine by the aruco generator you use.
        :param int totalMarkers: The size of the marker library you used. This value can be determine by the aruco generator you use.
        :return: A list of bounding boxes and ids that were found in the image. 
        :rtype: list   
        """

        try:
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
            arucoDict = aruco.Dictionary_get(key)
            arucoParam = aruco.DetectorParameters_create()
            bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
           # print("SENDING MARKERS", ids)
            self.queue.put_nowait(("FOUNDMARKERS",ids))
            return [bboxs, ids]
        except Exception as ex:
            print("aruco finder exception",ex)
            return []

    def arucoAug(self,bbox, img, imgAug, expandSize = 0):
        """Draws an image over the area marked by an aruco marker.
        :param bbox np.array(): The bounding box of the aruco marker. 
        :param img np.array(): The image unto which to draw the augmentation image. 
        :param imgAug np.array(): The augmentation image which shall be drawn unto the image. 
        :param expandSize int: The length by which the augmentation image shall surpass the marker. 
        :return: The augmented image. 
        :rtype: np.array() 
        
        
        """
        tl = bbox[0][0][0]-expandSize, bbox[0][0][1]-expandSize
        tr = bbox[0][1][0]+expandSize, bbox[0][1][1]-expandSize
        br = bbox[0][2][0]+expandSize, bbox[0][2][1]+expandSize
        bl = bbox[0][3][0]-expandSize, bbox[0][3][1]+expandSize
        h, w, c = imgAug.shape
        pts1 = np.array([tl, tr, br, bl])
        pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
        matrix, _ = cv.findHomography(pts2, pts1)
        imgout = cv.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
        cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
        imgout = img + imgout
        return imgout

    def calc_middle(self, points):
        """Determines the middle of either an aruco marker, or any number of points.

        :param list points: The points from which the middle shall be calculated.

        :return: The average of the points passed.
        :rtype: tuple
        
        """

        try:
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            centroid = (int(sum(x) / len(points)),int( sum(y) / len(points)))
            return centroid
        except:
                tl = points[0][0][0], points[0][0][1]
                tr = points[0][1][0], points[0][1][1]
                br = points[0][2][0], points[0][2][1]
                bl = points[0][3][0], points[0][3][1]
                points = [tl,tr,br,bl]
                x = [p[0] for p in points]
                y = [p[1] for p in points]
                centroid = (int(sum(x) / len(points)),int( sum(y) / len(points)))
                return centroid

    def draw_height_lines(self,data_lut):
        """Draws height lines onto the height data.
        :param np.array data_lut: Height data 
        :return: The array with drawn on height lines generated by canny. 
        :rtype: np.array
        """
        try:

            canny = cv.Canny(data_lut, 0,255)
            line_pixels = canny[:,:]>0
            data_lut[line_pixels]=self.lineBrown
            return data_lut
        except Exception as ex:
            print("Canny Error",ex)
            return data_lut


    def greyscale_for_height_lines(self, arr):
        """Returns an greyscale image of an RGB Image. This greyscale image is to be analysed with Canny. """
        output = cv.convertScaleAbs(arr,alpha=0.5)
        return output

    #generates a Lookup Table 
    def generate_LUT(self):
        """Generates a lookup table based on chosen colors and the chose value of self.waterlevel.
           Calls make_gradient_color.
           Lookup table is used to transform height data. 
        """
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

            lookup_table[num,0,0]= color_table[num][0]
            lookup_table[num,0,1]=color_table[num][1]
            lookup_table[num,0,2]=color_table[num][2]
        return lookup_table


    
    def make_gradient_color(self,value,rangeMin,rangeMax, colorMin, colorMax):
        """Generates gradient colors between two threshold values.
        This function is called by generate_LUT().

        :param int value: The current 1-byte value that the generate_LUT function is at. 
        :param int rangeMin: The lower end of the current color-range. 
        :param int rangeMax: The upper end of the current color-range.
        :param int colorMin: The three values making up a color associated with the value of rangeMin.
        :param int colorMax: The three calues making up a color associated with the value of rangeMax. 

        :return: A three value list containing the new color calculated from colorMin and colorMax 
        :rtype: tuple
        
        """
        scale = rangeMax-rangeMin
        distance = value-rangeMin
        percentage = 100 * float(distance)/float(scale)
        percentage = percentage/100
        newRed = colorMin[2] + percentage * (colorMax[2]- colorMin[2]);
        newGreen = colorMin[1] + percentage * (colorMax[1]- colorMin[1]);
        newBlue = colorMin[0] + percentage * (colorMax[0]- colorMin[0]);

        gradientColor = (newRed,newGreen,newBlue)
        return gradientColor



    def height_transform_lut(self, data): 
        """Transforms the height data from a Data_Getter Instance into a colour image by using a lookup table."""
      #  data = data.astype(np.uint8)
        data = cv.convertScaleAbs(data,alpha=self.depthBrightness)
        print("HEIHGT TRANSFROM SHAPRE ", data.shape, data)
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
        """Adds an Alpha Channel to an RGB-Color"""
        return (color[0],color[1],color[2],a_val)

    def argDecoder(self, datatuple):
            """The arg decoder is a multiprocessing communication helper.
               The Data_Interpreter receives all new data as a tuple via a queue.
               If the first element of said tuple is a string, the arg decoder changes parameters
               of the instance of this class. 
               :param tuple datatuple: A key-value pair to alter configurations for this class. 
            """
            new_data=datatuple
            if new_data[0]=="waterlevel":
                self.waterlevel = int(new_data[1])
                        
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="depthBrightness":
                self.depthBrightness = int(new_data[1])/100

            elif new_data[0]=="heightlineState":
                self.heightLineMode = bool(new_data[1])

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
            elif new_data[0]=="xoffset":
                self.firstOffset = new_data[1]

            elif new_data[0]=="yoffset":
                self.secondOffset = new_data[1]

