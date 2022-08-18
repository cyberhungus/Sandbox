import freenect
from PIL import Image, ImageFilter
import frame_convert2 as fc
import numpy as np



def new_colouring_algo(data):
    
    produced_array = np.ndarray(shape=(480,640),dtype=np.ndarray, order='C')
    for row in range(1,480):
        #print(row)
        #print(len(row))
        for column in range(1,640):
            original_value = data[row][column]
            #print(original_value)
            new_array = np.ndarray(shape=(3), dtype=np.uint8, order='C')
            new_array[0] = original_value
            new_array[1] = original_value
            new_array[2] = original_value
            produced_array[row][column] =  new_array
            #print(new_array)
    return produced_array                            
        

data = freenect.sync_get_depth()
array = data[0]
pretty_array = fc.pretty_depth(array)
col_array=new_colouring_algo(pretty_array)
img = Image.fromarray(pretty_array,"L").convert("RGB").filter(ImageFilter.EDGE_ENHANCE)
rgb_array = np.array(img)


for row in rgb_array:
    for pixel in row:
        pixel[0]= 0
        pixel[1]= 0
        
print(rgb_array)

img = Image.fromarray(rgb_array,"RGB")
img.save("edited_depth.png")