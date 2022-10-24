
import cv2 as cv 
import numpy as np 






def showLUT(lut):
    visualizer_height = 500
    visualizer_width = 500
    image = np.ones((visualizer_height, visualizer_width, 3), dtype = np.uint8)
   # black = np.where(image=[0,0,0])
   # image[black] = [255,255,255]
    x_it = 10
    y_it = 10 
    item_iterator = 0 
    for item in lut:
        #print("LUTITEM",item)
        col = [int(item[0][0]),int(item[0][1]),int(item[0][2])]
        cv.circle(image,center=(x_it, y_it), radius=5, color = col, thickness=5)
        font = cv.FONT_HERSHEY_PLAIN
        cv.putText(image, str(item_iterator), (x_it,y_it+20),font,0.5, (255,255,255))
        if x_it+20 < visualizer_width:
            x_it+=20
        else:
            x_it=20
            y_it +=40
        item_iterator += 1

    return image



    

        


    