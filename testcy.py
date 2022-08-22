import numpy as np
import cv2 as cv
from PIL import Image
def testcyfun(arr,lvl):
    output = np.zeros((480,640),dtype=np.uint8)
    mult = lvl/4
    mult= int(mult)
    print(mult,type(mult))
    water = arr[:,:]>lvl
    arr[water] = -1 
    landA = arr[:,:]>lvl-mult
    arr[landA] = -1
    landB = arr[:,:]>lvl-(mult*2)
    arr[landB] = -1
    landC = arr[:,:]>lvl-(mult*3)
    arr[landC] = -1
    landD = arr[:,:]>lvl-(mult*4)
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

    return data

    
            
            
