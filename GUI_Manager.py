
from itertools import filterfalse
from pickle import FALSE
import tkinter as tk 
from tkinter import colorchooser
from PIL import Image, ImageTk
#class generates a tk inter gui
import cv2

class GUI_Manager:
    def __init__(self, manager):
        self.setting_manager = manager
        self.latest_color_img = 0
        self.newWindow_status = False
        self.selected_points = []
        
    def start_gui(self):
        self.window = tk.Tk()
        self.label = tk.Label(self.window, text="Sandbox GUI")
        self.label.grid(column=1,row=0)
        self.waterslider = tk.Scale(self.window, from_=0, to=255, command= self.waterSliderMove)
        self.waterslider.set(50)
        self.waterslider.grid(column=0,row=1)
        self.labelWater = tk.Label(self.window, text="Waterlevel")
        self.labelWater.grid(column=0,row=2)
        self.markerSlider = tk.Scale(self.window, from_=50, to=250, command= self.markerSliderMove)
        self.markerSlider.set(100)
        self.markerSlider.grid(column=1,row=1)
        self.labelMarkerSize = tk.Label(self.window, text="Marker Size")
        self.labelMarkerSize.grid(column=1,row=3)

        self.markerState = tk.BooleanVar()
        markerOnButt = tk.Radiobutton(self.window, text="Markers On", variable=self.markerState, value=True, command=self.markerToggle)
        markerOnButt.grid(column=0,row=3)

        markerOffButt = tk.Radiobutton(self.window, text="Markers Off", variable=self.markerState, value=False, command=self.markerToggle)
       
        markerOffButt.grid(column=1, row=3)


        self.brightSlider = tk.Scale(self.window, from_=50, to=250, command= self.brightSliderMove)
        self.brightSlider.set(90)
        self.brightSlider.grid(column=2,row=1)
        self.brightMarkerSize = tk.Label(self.window, text="BrightnessAdd")
        self.brightMarkerSize.grid(column=2,row=3)


        self.refreshSlider = tk.Scale(self.window, from_=1, to=20, command= self.refreshSliderMove)
        self.refreshSlider.grid(column=2,row=1)
        self.labelRefresh = tk.Label(self.window, text="Refresh")
        self.labelRefresh.grid(column=2,row=2)
        self.treeSlide = tk.Scale(self.window, from_=1, to=20, command= self.treeSliderMove)
        self.treeSlide.grid(column=3,row=1)
        self.labelTree = tk.Label(self.window, text="Trees")
        self.labelTree.grid(column=3,row=2)

        self.standardButton = tk.Button(self.window, text="STANDARD VALUES (RESET)",command=self.load_standard_values)
        self.standardButton.grid(column = 0,row=11 )
        self.colorA =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorA'])
        self.labelA = tk.Button(self.window,text="Color A",bg=self.colorA, command=lambda: self.choose_Color("arrcolorA"))
        self.labelA.grid(column=3,row=4)
        self.colorB =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorB'])
        self.labelB = tk.Button(self.window,text="Color B",bg=self.colorB, command=lambda: self.choose_Color("arrcolorB"))
        self.labelB.grid(column=3,row=5)
        self.colorC =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorC'])
        self.labelC = tk.Button(self.window,text="Color C",bg=self.colorC, command=lambda: self.choose_Color("arrcolorC"))
        self.labelC.grid(column=3,row=6)
        self.colorD =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorD'])
        self.labelD = tk.Button(self.window,text="Color D",bg=self.colorD, command=lambda: self.choose_Color("arrcolorD"))
        self.labelD.grid(column=3,row=7)
        self.colorE =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorE'])
        self.labelE = tk.Button(self.window,text="Color E",bg=self.colorE, command=lambda: self.choose_Color("arrcolorE"))
        self.labelE.grid(column=3,row=8)
        self.colorF =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorF'])
        self.labelF = tk.Button(self.window,text="Color F",bg=self.colorF, command=lambda: self.choose_Color("arrcolorF"))
        self.labelF.grid(column=3,row=9)
        self.colorW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW = tk.Button(self.window,text="Color W",bg=self.colorW, command=lambda: self.choose_Color("arrcolorWater"))
        self.labelW.grid(column=3,row=10)
        self.colorDW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorDeepWater'])
        self.labelDW = tk.Button(self.window,text="Color DW",bg=self.colorDW, command=lambda: self.choose_Color("arrcolorDeepWater"))
        self.labelDW.grid(column=3,row=11)

        self.window.attributes('-topmost', 'true')
        self.window.mainloop()

    def on_close_new(self):
        self.newWindow_status=False
        self.newWindow.destroy()


    def brightSliderMove(self,arg):
        self.setting_manager.alter_setting("addBrightness",arg)

    def waterSliderMove(self,arg):
        self.setting_manager.alter_setting("waterlevel",arg)


    def markerSliderMove(self,arg):
        self.setting_manager.alter_setting("markerSize",arg)
        self.labelMarkerSize.config(text="Marker Size: "+str(arg))

    def markerToggle(self):
        print("marker toggle", self.markerState.get())
        self.setting_manager.alter_setting("displayMarkers",self.markerState.get())

    def refreshSliderMove(self,arg):
        self.setting_manager.alter_setting("refreshRate",arg)

    def treeSliderMove(self,arg):
        self.setting_manager.alter_setting("newTrees",arg)

    def array_color_hex(self,array):
        try:
            return '#%02x%02x%02x' % (array[0], array[1], array[2])
        except:
            return "#000000"

    def bgr_array_color_hex(self,array):
        try:
            return '#%02x%02x%02x' % (array[2], array[1], array[0])
        except:
            return "#000000"

    #resets all values to standard values 
    def load_standard_values(self):
        self.setting_manager.write_standards()
        self.setting_manager.read()
        self.update_ui()

    #displays the color picker 
    def choose_Color(self,param):
        # variable to store hexadecimal code of color
        try:
            color_code = colorchooser.askcolor(title ="Choose color")
            self.setting_manager.alter_setting(param,[round(color_code[0][2]),round(color_code[0][1]),round(color_code[0][0])])
            self.update_ui()
        except Exception as ex:
            print("Color chooser closed without selection or error:",ex)

    #hook to update the ui 
    def update_ui(self):
        self.waterslider.set(self.setting_manager.get_settings()['waterlevel'])

        self.colorA =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorA'])
        self.labelA.config(bg=self.colorA)
        self.colorB =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorB'])
        self.labelB.config(bg=self.colorB)
        self.colorC =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorC'])
        self.labelC.config(bg=self.colorC)
        self.colorD =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorD'])
        self.labelD.config(bg=self.colorD)
        self.colorE =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorE'])
        self.labelE.config(bg=self.colorE)
        self.colorF =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorF'])
        self.labelF.config(bg=self.colorF)
        self.colorW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW.config(bg=self.colorW)

