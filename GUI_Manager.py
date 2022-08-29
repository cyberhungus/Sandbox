
import tkinter as tk 
from tkinter import colorchooser

class GUI_Manager:
    def __init__(self, manager):
        self.setting_manager = manager


        self.window = tk.Tk()
        self.label = tk.Label(self.window, text="Sandbox GUI")


        self.label.grid(column=1,row=0)
        self.waterslider = tk.Scale(self.window, from_=0, to=255, command= self.waterSliderMove)
        self.waterslider.set(self.setting_manager.get_settings()['waterlevel'])
        self.waterslider.grid(column=0,row=1)
        self.labelWater = tk.Label(self.window, text="Waterlevel")
        self.labelWater.grid(column=0,row=2)


        self.shapeminslider = tk.Scale(self.window, from_=30, to=400, command= self.shapeSliderMove)
        self.shapeminslider.set(self.setting_manager.get_settings()['minShapeSize'])
        self.shapeminslider.grid(column=1,row=1)
        self.labelShape = tk.Label(self.window, text="Shapesize")
        self.labelShape.grid(column=1,row=2)

        self.refreshSlider = tk.Scale(self.window, from_=1, to=20, command= self.refreshSliderMove)
        self.shapeminslider.set(self.setting_manager.get_settings()['refreshRate'])
        self.refreshSlider.grid(column=2,row=1)
        self.labelRefresh = tk.Label(self.window, text="Refresh")
        self.labelRefresh.grid(column=2,row=2)

        self.color_corr_state = False
        self.autoColorButton = tk.Button(self.window, text="Color Correct: False"+str(self.color_corr_state),command=self.col_corr)
        self.autoColorButton.grid(column = 0,row=3 )

        self.standardButton = tk.Button(self.window, text="STANDARD VALUES (RESET)",command=self.load_standard_values)
        self.standardButton.grid(column = 0,row=4 )

        self.colorA =  self.array_color_hex(self.setting_manager.get_settings()['colorA'])
        self.labelA = tk.Button(self.window,bg=self.colorA, command=lambda: self.choose_Color("arrcolorA"))
        self.labelA.grid(column=3,row=3)

        self.colorB =  self.array_color_hex(self.setting_manager.get_settings()['colorB'])
        self.labelB = tk.Button(self.window,bg=self.colorB, command=lambda: self.choose_Color("arrcolorB"))
        self.labelB.grid(column=4,row=3)

        self.colorC =  self.array_color_hex(self.setting_manager.get_settings()['colorC'])
        self.labelC = tk.Button(self.window,bg=self.colorC, command=lambda: self.choose_Color("arrcolorC"))
        self.labelC.grid(column=5,row=3)

        self.colorD =  self.array_color_hex(self.setting_manager.get_settings()['colorD'])
        self.labelD = tk.Button(self.window,bg=self.colorD, command=lambda: self.choose_Color("arrcolorD"))
        self.labelD.grid(column=6,row=3)

        self.colorW =  self.array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW = tk.Button(self.window,bg=self.colorW, command=lambda: self.choose_Color("arrcolorWater"))
        self.labelW.grid(column=7,row=3)
        self.window.attributes('-topmost', 'true')
        self.window.mainloop()




    def waterSliderMove(self,arg):
        self.setting_manager.alter_setting("waterlevel",arg)


    def shapeSliderMove(self,arg):
        self.setting_manager.alter_setting("minShapeSize",arg)

    def refreshSliderMove(self,arg):
        self.setting_manager.alter_setting("refreshRate",arg)

    def col_corr(self):
        print("color correct button press")
        self.color_corr_state = not self.color_corr_state
        self.setting_manager.change_col_corr(self.color_corr_state)
        self.autoColorButton.config(text="Color Correct: "+str(self.color_corr_state))


    def array_color_hex(self,array):
        try:
            return '#%02x%02x%02x' % (array[0], array[1], array[2])
        except:
            return "#000000"


    def load_standard_values(self):
        self.setting_manager.write_standards()
        self.setting_manager.read()
        self.update_ui()

    def choose_Color(self,param):
 
        # variable to store hexadecimal code of color
        try:
            color_code = colorchooser.askcolor(title ="Choose color")
            self.setting_manager.alter_setting(param,[round(color_code[0][2]),round(color_code[0][1]),round(color_code[0][1])])
            self.update_ui()
        except Exception as ex:
            print("Color chooser closed without selection or error:",ex)

    def update_ui(self):
        self.waterslider.set(self.setting_manager.get_settings()['waterlevel'])
        self.shapeminslider.set(self.setting_manager.get_settings()['minShapeSize'])
        self.shapeminslider.set(self.setting_manager.get_settings()['refreshRate'])
        self.colorA =  self.array_color_hex(self.setting_manager.get_settings()['colorA'])
        self.labelA.config(bg=self.colorA)
        self.colorB =  self.array_color_hex(self.setting_manager.get_settings()['colorB'])
        self.labelB.config(bg=self.colorB)
        self.colorC =  self.array_color_hex(self.setting_manager.get_settings()['colorC'])
        self.labelC.config(bg=self.colorC)
        self.colorD =  self.array_color_hex(self.setting_manager.get_settings()['colorD'])
        self.labelD.config(bg=self.colorD)
        self.colorW =  self.array_color_hex(self.setting_manager.get_settings()['colorWater'])
        self.labelW.config(bg=self.colorW)