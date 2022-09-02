from multiprocessing import Queue
from threading import Thread 
import cv2 

class Data_Visualizer:
    def __init__(self, inputQueue):
        self.input = inputQueue
        self.current_image_full = 0 
        self.current_image_rgb_raw = 0 
        self.depth_control = 0


    def visualizer_runner(self):
        while 1:
            if not self.input.empty():
                current_data = self.input.get_nowait()

                if current_data[0]=="ANALYZED":
                    self.current_image_full = current_data[1]

                elif current_data[0]=="RAW_RGB":
                    self.current_image_rgb_raw = current_data[1]

                elif current_data[0]=="DEPTH_TEST":
                    self.depth_control = current_data[1]



                #print("DATA VIS RECEIVED:",self.current_image)
                try:
                    cv2.namedWindow("OUTPUT", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("OUTPUT",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                    cv2.namedWindow("OUTPUT_CONTROL")
                    cv2.imshow("OUTPUT",self.get_current())
                    cv2.imshow("OUTPUT_CONTROL",self.get_current())
                    cv2.imshow("OUTPUT2",self.current_image_rgb_raw)
                    cv2.imshow("output3",self.depth_control)

                except Exception as ex:
                    print("Error in Visualizer: ", ex)
                if cv2.waitKey(10) == 27:
                    break

    def get_current(self):
        return self.current_image_full
                

                