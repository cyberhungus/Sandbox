from multiprocessing import Queue
from threading import Thread 
import cv2 

class Data_Visualizer:
    def __init__(self, inputQueue):
        self.input = inputQueue
        self.current_image = 0 

    def receive_new_data(self, data):
        self.current_image = data

    def visualizer_runner(self):
        while 1:
            if not self.input.empty():
                self.current_image = self.input.get_nowait()
                #print("DATA VIS RECEIVED:",self.current_image)
                try:
                    cv2.namedWindow("OUTPUT", cv2.WND_PROP_FULLSCREEN)
                    cv2.setWindowProperty("OUTPUT",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                    cv2.namedWindow("OUTPUT_CONTROL")
                    cv2.moveWindow("OUTPUT_CONTROL", 100,100)
                    cv2.imshow("OUTPUT",self.get_current())
                    cv2.imshow("OUTPUT_CONTROL",self.get_current())
                except Exception as ex:
                    print("Error in Visualizer: ", ex)
                if cv2.waitKey(10) == 27:
                    break

    def get_current(self):
        return self.current_image
                

                