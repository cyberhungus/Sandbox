

from queue import Empty
from threading import Thread 
from multiprocessing import Queue
import numpy as np
from PIL import Image, ImageFilter
import cv2 as cv
import cv2.aruco as aruco
import timeit

import os
from Object_Manager import Tree_Manager as tm
import LookupTableVisualizer as Lutvis

#this class receives image data via a queue, iterates through the pixels, and changes their colour in accordance with height data 
class Data_Interpreter(Thread):
    def __init__(self,input_queue, output_queue, pipe, has_trees = False):

        self.queue = pipe 
       

        self.input = input_queue
        self.output = output_queue
        self.waterlevel = 120
        self.waterheight = 256

        self.shapes =[]


        self.borders_set = False
        self.border_mask = 0
              
        #Region storing variables 
        self.lineBrown = (1,1,1)
        self.colorA = (255,255,255)
        self.colorB = (255,255,255)
        self.colorC = (255,255,255)
        self.colorD = (255,255,255)
        self.colorE = (255,255,255)
        self.colorF = (255,255,255)
        self.colorF = (255,255,255)
        self.colorG = (255,255,255)
        self.colorWhite = (255,255,255)
        self.colorWater = (255,255,255)
        self.colorDeepWater = (255,255,255)

        filepath = os.getcwd()+"/assets/newTopoItem.png"
        self.houseIMG = cv.imread(filepath,cv.IMREAD_COLOR)

        filepath = os.getcwd()+"/assets/garten.png"
        self.gardenIMG = cv.imread(filepath,cv.IMREAD_COLOR)

        filepath = os.getcwd()+"/assets/okshlogo.png"
        self.logoIMG = cv.imread(filepath,cv.IMREAD_COLOR)

        
        filepath = os.getcwd()+"/assets/asphalt.png"
        self.asphaltIMG = cv.imread(filepath,cv.IMREAD_COLOR)

        filepath = os.getcwd()+"/assets/tree.png"
        self.treeIMG = cv.imread(filepath,cv.IMREAD_UNCHANGED)
  #     


        self.displaysize =(1920,1080)


        self.maskpoints = [[0,0],[1080,1920]]
        self.lastMaskPoints = 0 
        self.standardmask = [[0,0],[1920,0],[0,1080],[1920,1080]]

        self.depthBrightness = 0.035


        self.realArucoSizeMM = 26.28
        self.focal_length = 1233.24
        self.markerSizePixel = 0 
        self.camera_height = 1 

        self.heightLineMode = True

        self.firstOffset =  0
        self.secondOffset = 0 

        self.heightrangeLOW = 0
        self.heightrangeHIGH = 255
        
        self.lookup_table = self.generate_LUT()

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
                    #starttime = timeit.default_timer()
                    self.findmask(new_data[1])

                    self.output.put_nowait(("RAW_RGB",new_data[1]))
                   # self.queue.put_nowait(("RGB",new_data[0]))
                   # self.queue.put_nowait(("DEPTH",new_data[1]))
                    #depth = self.four_point_transform(new_data[0],self.maskpoints)

                    depth=new_data[0]
                    color = new_data[1]
                    depth = self.applymask(depth)
                    
                    processed_data_depth = self.height_transform_lut(depth)
                    if self.heightLineMode==True:
                        processed_data_depth = self.draw_height_lines(processed_data_depth)

                    full_img = self.process_aruco(color,processed_data_depth)
                   # cv.imshow("LUT", Lutvis.showLUT(self.lookup_table))
                    #cv.waitKey(1)
                 
                   
                    self.queue.put_nowait(("FULL",full_img))



                   
                    self.output.put_nowait(("ANALYZED",full_img))

                   # print("Time for color convert algorithm :", timeit.default_timer() - starttime)




    def determineAvgDepth(self, depthimg):
        try:
            aruco_depth = []
            for p in self.maskpoints:     
                depthimg = cv.convertScaleAbs(depthimg,alpha=self.depthBrightness)
                depthimg = cv.resize(depthimg, (1920,1080), interpolation = cv.INTER_AREA)
                aruco_depth.append(depthimg[int(p[1])-1, int(p[0])-1])
            summed = 0 
            for num in aruco_depth:
                summed += num 
            return summed / 4
        except Exception as ex:
            print("avrg depth ex,", ex)
            return 0 


    


    #TODO FIGure this out
    def findmask(self, img):
        """ Finds the masking points circumscribing the display area - i.e. ArUco Markers 0 through 3. 
            The center of said markers is the determined, and the four markers are sorted to be used as a mask. 

            :param np.array img: The image to be examined for ArUco markers. 
        
        """
        self.lastMaskPoints= self.maskpoints
        self.maskpoints = []
        arucofound = self.findArucoMarkers(img)
        if arucofound:
            if len(arucofound[0])>=4 and (x in [0,1,2,3] for x in arucofound[1]):
                print(arucofound[1])
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

        try:
            img = np.zeros((1080,1920,3),dtype=np.uint8)
            img[np.where((img == [0,0,0] ).all(axis = 2))] = [255,255,255]
            h, w, c = imgAug.shape
            pts1 = np.array(np.array(self.maskpoints)+(self.firstOffset,self.secondOffset))
           # pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
            pts2 = np.float32([[0,0], [h,0], [h,w], [0,w]])

            matrix, _ = cv.findHomography(pts1, pts2)
            imgout = cv.warpPerspective(imgAug, matrix, (img.shape[1], img.shape[0]))
           # cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
            imgout = img + imgout
            return imgout
        except Exception as ex:
            img = np.zeros((1080,1920,3),dtype=np.uint8)
            return img

    def process_aruco(self, img_rgb, img_depth):
        """Wraps the Aruco detection and augmentation functionalities in a single function. Places the augmentation images on the depth data image. 
        This is not used for corner detection, but solely for placing graphics unto the image that is to be projected. 

        :param np.array img_rgb: The RGB data received via Queue from a Data_Getter. This image acts as the source of the aruco markers. 
        :param np.array img_depth: The depth data received via Queue from a Data_Getter. This image acts as the destination for the augmentation images. 

        :return: The augmented (or not, in case there were no markers in the image) image. 
        :rtype: np.array

        """
        img = img_rgb.copy()
        img = self.applymask(img)
        new_img=img_depth
        arucofound = self.findArucoMarkers(img)
        if arucofound:
            if len(arucofound[0])!=0:
                for bbox, id in zip(arucofound[0], arucofound[1]):

                    if id < 5:
                        #print("Proces Aruco" , bbox,id)
                        if id == 10 :   
                            new_img = self.arucoAug(bbox, new_img, self.houseIMG, expandSize=50)
                        elif id == 9:
                            new_img = self.arucoAug(bbox, new_img, self.gardenIMG, expandSize= 40)
                        elif id == 8 :   
                            new_img = self.arucoAug(bbox, new_img, self.logoIMG, expandSize=50)
                        elif id == 7 :   
                            new_img = self.arucoAug(bbox, new_img, self.asphaltIMG, expandSize=50)
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
        try:
            tl = bbox[0][0][0]-expandSize, bbox[0][0][1]-expandSize
            tr = bbox[0][1][0]+expandSize, bbox[0][1][1]-expandSize
            br = bbox[0][2][0]+expandSize, bbox[0][2][1]+expandSize
            bl = bbox[0][3][0]-expandSize, bbox[0][3][1]+expandSize
            h, w, c = imgAug.shape
            pts1 = np.array([tl, tr, br, bl])-(self.firstOffset,self.secondOffset)

           # pts2 = np.float32([[0,0], [w,0], [w,h], [0,h]])
            pts2 = np.float32([[0,0], [h,0], [h,w], [0,w]])
            matrix, _ = cv.findHomography(pts2, pts1)
            imgout = cv.warpPerspective(cv.rotate(imgAug, cv.ROTATE_90_COUNTERCLOCKWISE), matrix, (img.shape[1], img.shape[0]))
            cv.fillConvexPoly(img, pts1.astype(int), (0, 0, 0))
            imgout = img + imgout
            return imgout
        except Exception as ex:
            print(ex)
            return img

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



        testdata = data_lut.copy()
        blur = cv.GaussianBlur(testdata, (7, 7), 0)
        sigma = np.std(blur)
        mean = np.mean(blur)
        lower = int(max(0, (mean - sigma)))
        upper = int(min(255, (mean + sigma)))

        edge = cv.Canny(blur, lower, upper)

        try:
            data = data_lut.copy()


            canny = cv.Canny(data, 0,255)

            line_pixels = canny[:,:]>0
            data[line_pixels]=self.lineBrown

            return data
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
        remainder = (256-self.waterlevel)/6
        for num in range(256):

            
            if num in range(0,int(self.waterlevel/2)):
                color_table.append(self.colorDeepWater)        
            elif num in range(int(self.waterlevel/2),self.waterlevel):
                color_table.append(self.colorWater)
            elif num in range(int(self.waterlevel),int(self.waterlevel+remainder)):
                color_table.append(self.colorA)
            elif num in range(int(self.waterlevel+remainder),int(self.waterlevel+remainder*2)):
                color_table.append(self.colorB)
            elif num in range(int(self.waterlevel+remainder*2),int(self.waterlevel+remainder*3)):
                color_table.append(self.colorC)
            elif num in range(int(self.waterlevel+remainder*3),int(self.waterlevel+remainder*4)):
                color_table.append(self.colorD) 
            elif num in range(int(self.waterlevel+remainder*4),int(self.waterlevel+remainder*5)):
                color_table.append(self.colorE)
            elif num in range(int(self.waterlevel+remainder*5),int(self.waterlevel+remainder*6)):
                color_table.append(self.colorF)   
            elif num in range(int(self.waterlevel+remainder*6),int(254)):
                color_table.append(self.colorG)
            elif num == 255:
                color_table.append(self.colorWhite)

            lookup_table[num,0,0]= color_table[num][0]
            lookup_table[num,0,1]=color_table[num][1]
            lookup_table[num,0,2]=color_table[num][2]

        return lookup_table
        #return np.flip(lookup_table, axis =2)


    
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
        newRed = colorMin[0] + percentage * (colorMax[0]- colorMin[0]);
        newGreen = colorMin[1] + percentage * (colorMax[1]- colorMin[1]);
        newBlue = colorMin[2] + percentage * (colorMax[2]- colorMin[2]);

        gradientColor = (newRed,newGreen,newBlue)
        #return gradientColor
        return gradientColor



    def height_transform_lut(self, data): 
        """Transforms the height data from a Data_Getter Instance into a colour image by using a lookup table."""
      #  data = data.astype(np.uint8)
       # data = cv.convertScaleAbs(data,alpha=self.depthBrightness)
       # print("HEIHGT TRANSFROM SHAPRE ", data.shape, data)



        self.output.put_nowait(("DEPTH",data))
        return cv.LUT(data,self.lookup_table)


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
                self.depthBrightness = int(new_data[1])/1000

            elif new_data[0]=="heightlineState":
                self.heightLineMode = bool(new_data[1])

            elif new_data[0]=="colorA":
                self.colorA = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorB":
                self.colorB =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorC":
                self.colorC =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorD":
                self.colorD =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="colorE":
                self.colorE =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorF":
                self.colorF = (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorG":
                self.colorG =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorWater":
                self.colorWater =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))

                self.lookup_table = self.generate_LUT()
            elif new_data[0]=="colorDeepWater":
                self.colorDeepWater =  (int(new_data[1][2]),int(new_data[1][1]),int(new_data[1][0]))
                        
                self.lookup_table = self.generate_LUT()

            elif new_data[0]=="xoffset":
                self.firstOffset = new_data[1]

            elif new_data[0]=="yoffset":
                self.secondOffset = new_data[1]

