
from itertools import filterfalse
from multiprocessing import Value
from pickle import FALSE
import tkinter as tk 
from tkinter import colorchooser
from PIL import Image, ImageTk
#class generates a tk inter gui
import cv2

class GUI_Manager:
    def __init__(self, manager, pipe):
        self.setting_manager = manager
        self.latest_color_img = 0
        self.newWindow_status = False
        self.selected_points = []
        self.queue = pipe 
        self.xoffset = -30
        self.yoffset = 20
        
    def start_gui(self):
        """
        This function contains all UI elements that are part of the User Interface. 
        
        """
        self.window = tk.Tk()
        self.label = tk.Label(self.window, text="Sandbox GUI")
        self.label.grid(column=1,row=0)
        self.waterslider = tk.Scale(self.window, from_=0, to=255, command= self.waterSliderMove)
        self.waterslider.set(175)
        self.waterslider.grid(column=0,row=1)
        self.labelWater = tk.Label(self.window, text="Waterlevel")
        self.labelWater.grid(column=0,row=2)
        self.markerSlider = tk.Scale(self.window, from_=50, to=250, command= self.markerSliderMove)
        self.markerSlider.set(100)
        self.markerSlider.grid(column=1,row=1)
        self.labelMarkerSize = tk.Label(self.window, text="Marker Size")
        self.labelMarkerSize.grid(column=1,row=3)

        self.markerState = tk.BooleanVar()
        self.markerOnButt = tk.Radiobutton(self.window, text="Markers On", variable=self.markerState, value=True, command=self.markerToggle)
        self.markerOnButt.grid(column=0,row=3)
        self.markerOffButt = tk.Radiobutton(self.window, text="Markers Off", variable=self.markerState, value=False, command=self.markerToggle)
        self.markerOffButt.grid(column=1, row=3)

        self.heightlineState = tk.BooleanVar()
        self.heightlineOnButt = tk.Radiobutton(self.window, text="Heightlines On", variable=self.heightlineState, value=True, command=self.heightlineToggle)
        self.heightlineOnButt.grid(column=0,row=5)
        self.heightlineOffButt = tk.Radiobutton(self.window, text="Heightlines Off", variable=self.heightlineState, value=False, command=self.heightlineToggle)
        self.heightlineOffButt.grid(column=1, row=5)

        self.brightSlider = tk.Scale(self.window, from_=0, to=250, command= self.brightSliderMove)
        self.brightSlider.set(0)
        self.brightSlider.grid(column=6,row=1)
        self.brightMarkerSize = tk.Label(self.window, text="Marker Bright.")
        self.brightMarkerSize.grid(column=6,row=3)

        
        self.depthBrightSlider = tk.Scale(self.window, from_=0, to=100, command= self.depthBrightSliderMove)
        self.depthBrightSlider.set(3)
        self.depthBrightSlider.grid(column=7,row=1)
        self.depthBrightMarkerSize = tk.Label(self.window, text="Depth Alpha")
        self.depthBrightMarkerSize.grid(column=7,row=3)

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
        self.colorG =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorG'])
        self.labelG = tk.Button(self.window,text="Color G",bg=self.colorG, command=lambda: self.choose_Color("arrcolorG"))
        self.labelG.grid(column=3,row=10)
        self.colorW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW = tk.Button(self.window,text="Color W",bg=self.colorW, command=lambda: self.choose_Color("arrcolorWater"))
        self.labelW.grid(column=3,row=11)
        self.colorDW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorDeepWater'])
        self.labelDW = tk.Button(self.window,text="Color DW",bg=self.colorDW, command=lambda: self.choose_Color("arrcolorDeepWater"))
        self.labelDW.grid(column=3,row=12)


        self.xplusone = tk.Button(self.window,text="x+1",  command=lambda: self.x_offset_change(-1))
        self.xplusone.grid(column=3,row=14)
        self.xminusone = tk.Button(self.window,text="x-1",  command=lambda: self.x_offset_change(1))
        self.xminusone.grid(column=1,row=14)
        self.xplusten = tk.Button(self.window,text="x+10",  command=lambda: self.x_offset_change(-10))
        self.xplusten.grid(column=4,row=14)
        self.xminusten = tk.Button(self.window,text="x-10",  command=lambda: self.x_offset_change(10))
        self.xminusten.grid(column=0,row=14)
        self.xreset = tk.Button(self.window,text="x-Reset",  command=lambda: self.x_reset())
        self.xreset.grid(column=2,row=14)


        self.xoffsetLabel = tk.Label(self.window, text="X-Offset: 0")
        self.xoffsetLabel.grid(column=5,row=14)

        self.yplusone = tk.Button(self.window,text="y+1",  command=lambda: self.y_offset_change(-1))
        self.yplusone.grid(column=3,row=15)
        self.yminusone = tk.Button(self.window,text="y-1",  command=lambda: self.y_offset_change(1))
        self.yminusone.grid(column=1,row=15)
        self.yplusten = tk.Button(self.window,text="y+10",  command=lambda: self.y_offset_change(-10))
        self.yplusten.grid(column=4,row=15)
        self.yminusten = tk.Button(self.window,text="y-10",  command=lambda: self.y_offset_change(10))
        self.yminusten.grid(column=0,row=15)
        self.yreset = tk.Button(self.window,text="y-Reset",  command=lambda: self.y_reset())
        self.yreset.grid(column=2,row=15)
        
        self.yoffsetLabel = tk.Label(self.window, text="Y-Offset: 0")
        self.yoffsetLabel.grid(column=5,row=15)


        self.markerDisplay = tk.Label(self.window)
        self.markerDisplay.grid(column=0,row=12)


        self.window.after(20,self.refresh_via_queue)

        self.window.attributes('-topmost', 'true')

        self.update_ui()
        self.window.mainloop()



    def x_offset_change(self, value):
        """
        Called when pressing one of the offset buttons.
        Changes the offset on the x axis

        :param int value: The value to change the x axis offset by. Can be negative or positive
        """
        self.xoffset+=value
        self.setting_manager.alter_setting("xoffset",self.xoffset)
        self.xoffsetLabel.config(text="X-Offset: "+str(self.xoffset))

    def x_reset(self):
        """
        Resets the x offset value back to zero. 
        Called when pressing the x reset button. 
        """
        self.xoffset = 0
        self.setting_manager.alter_setting("xoffset",self.xoffset)
        self.xoffsetLabel.config(text="X-Offset: "+str(self.xoffset))


    def y_offset_change(self, value):
        """
        Called when pressing one of the offset buttons.
        Changes the offset on the y axis

        :param int value: The value to change the y axis offset by. Can be negative or positive
        """
        self.yoffset+=value
        self.setting_manager.alter_setting("yoffset",self.yoffset)
        self.yoffsetLabel.config(text="Y-Offset: "+str(self.yoffset))

    def y_reset(self):
        """
        Resets the y offset value back to zero. 
        Called when pressing the y reset button. 
        """
        self.yoffset = 0
        self.setting_manager.alter_setting("yoffset",self.yoffset)
        self.yoffsetLabel.config(text="Y-Offset: "+str(self.yoffset))



    def depthBrightSliderMove(self, arg):
        """
        Called when the depth brightness slider is moved. 
        This changes an alpha-value in the Data_Interpreter 

        :param int arg: The current value of the slider. This value is later divided by 100. Parameter is passed via callback provided by tkinter. 

        """


        self.setting_manager.alter_setting("depthBrightness",arg)

    def brightSliderMove(self,arg):
        """
        Called when the brightness slider is moved. 
        This changes the addBrightness value in the Data_Visualizer, which is used for the ArUco markers. 

        :param int arg: The current value of the slider. Parameter is passed via callback provided by tkinter. 

        """
        self.setting_manager.alter_setting("addBrightness",arg)

    def waterSliderMove(self,arg):
        """
        Called when the waterlevel slider is moved. 
        This changes the waterLevel value in the Data_Interpreter, which is linked to many functions of that class.

        :param int arg: The current value of the slider. Parameter is passed via callback provided by tkinter. 

        """
        self.setting_manager.alter_setting("waterlevel",arg)


    def markerSliderMove(self,arg):
        """
        Called when the MarkerSize slider is moved. 
        This changes the markerSize value in the Data_Visualizer, which is used for the size of the ArUco markers. 

        :param int arg: The current value of the slider. Parameter is passed via callback provided by tkinter. 

        """
        self.setting_manager.alter_setting("markerSize",arg)
        self.labelMarkerSize.config(text="Marker Size: "+str(arg))

    def markerToggle(self):
        """
        Called when one of the markerState radiobuttons is selected. 
        This controls wether markers are displayed on top of the projected image in the Data_Visualizer. 
        Due to how tkinter handles radiobuttons, no argument is needed. 

        """
        self.setting_manager.alter_setting("displayMarkers",self.markerState.get())

    def heightlineToggle(self):
        """
        Called when one of the markerState radiobuttons is selected. 
        This controls wether heightlines are drawn on the image in the Data_Interpreter. 
        Due to how tkinter handles radiobuttons, no argument is needed. 

        """

        self.setting_manager.alter_setting("heightlineState",self.heightlineState.get())

    def refreshSliderMove(self,arg):
        """
        Called when the refreshRate slider is moved. 
        This changes the frequency at which images are polled from the Camera in Data_Getter.

        :param int arg: The current value of the slider. Parameter is passed via callback provided by tkinter. 

        """
        self.setting_manager.alter_setting("refreshRate",arg)

    def treeSliderMove(self,arg):
        self.setting_manager.alter_setting("newTrees",arg)

    def array_color_hex(self,array):
        """
        Helper function which transforms a three value list representing an RGB color into a string that can be used to color tkinter elements. 
        This is the RGB version of that function. 

        :param list array: A three value list representing a color - [RED, GREEN, BLUE]

        :returns: A String representing the input color.  
        :rtype: String 
        """

        try:
            return '#%02x%02x%02x' % (array[0], array[1], array[2])
        except:
            return "#000000"

    def bgr_array_color_hex(self,array):
        """
        Helper function which transforms a three value list representing a BGR color into a string that can be used to color tkinter elements. 
        This is the BGR version of that function. 

        :param list array: A three value list representing a color - [BLUE, GREEN, RED]

        :returns: A String representing the input color.  
        :rtype: String 
        """

        try:
            return '#%02x%02x%02x' % (array[0], array[1], array[2])
        except:
            return "#000000"

    def refresh_via_queue(self):
        """
        This function is repeatedly called via tk's "after" method. It polls a queue for new data which can then be displayed in the UI.
        
        """
        if not self.queue.empty():
            rec = self.queue.get_nowait()

            if rec[0] == "FOUNDMARKERS":
                seenString =""
                try:
                    for item in rec[1]:
                        seenString+=str(item)
                        seenString+="-"
                except:
                    print("GUI MARKER TRANSMISSION ER ER")

                self.markerDisplay.config(text="Markers Seen: "+ seenString)

        self.window.after(20,self.refresh_via_queue)




    def load_standard_values(self):
        """
        Called when the "Standard Values/RESET" button is pressed.
        Orders the Settings_Manager to reload standard parameters, which also applies them to all components. 

        """
        self.setting_manager.write_standards()
        self.setting_manager.read()
        self.update_ui()

    def choose_Color(self,param):
        """
        Called when one of the various color buttons is pressed. 
        Opens a colorpicker window. When "OK" is pressed in that window, the GUI_Manager passes that value to the setting_manager and in turn to the 
        Data_Visualizer. What color is changed is determined by the param argument. 
        Then the respective Button is recolored. 

        :param String param: The name of the color to be changed in the settings manager. 

        """

        try:
            color_code = colorchooser.askcolor(title ="Choose color")
            self.setting_manager.alter_setting(param,[round(color_code[0][0]),round(color_code[0][1]),round(color_code[0][2])])
            self.update_ui()
        except Exception as ex:
            print("Color chooser closed without selection or error:",ex)

    
    def update_ui(self):
        """
        Updates colors and values in the UI. 
        """

        print("Update UI called")
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
        self.colorG =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorG'])
        self.labelG.config(bg=self.colorG)
        self.colorW =  self.bgr_array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW.config(bg=self.colorW)
        self.xoffsetLabel.config(text="X-Offset: " + str(self.setting_manager.get_settings()["xoffset"]))

