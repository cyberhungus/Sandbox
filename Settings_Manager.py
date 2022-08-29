import json

class Settings_Manager:
    def __init__(self,main_manager, filepath="config.json", standards = True ):
        self.filepath=filepath
        self.main_manager = main_manager
        self.standard_dict = {"waterlevel":150,
                         "colorA":(0,50,0),
                         "colorB":(0,100,100),
                         "colorC":(0,150,100),
                         "colorD":(0,200,100),
                         "colorWater":(200,50,0),
                         "shapeThreshLow":(70,0,70),
                         "shapeThreshHigh":(100,45,100),
                         "minShapeSize":50,
                         "refreshRate":1
                         }
        self.settings_dict = {"waterlevel":150,
                         "colorA":(0,50,0),
                         "colorB":(0,100,100),
                         "colorC":(0,150,100),
                         "colorD":(0,200,100),
                         "colorWater":(200,50,0),
                         "shapeThreshLow":(70,0,70),
                         "shapeThreshHigh":(100,45,100),
                         "minShapeSize":50,
                         "refreshRate":1
                         }
        if standards==True:
           self.write_standards()
        self.read()

    def alter_setting(self,parameter, value):
        if not parameter.__contains__("color"): 
            self.settings_dict[parameter] = value 
            self.main_manager.update_settings_hook(self.settings_dict)
            self.write()
        else:
            self.settings_dict[parameter[3:]] = [value[0],value[1],value[2] ]
            self.main_manager.update_settings_hook(self.settings_dict)
            self.write()


    def read(self):
        try:
            config_file = open(self.filepath)
            settings = json.load(config_file)
            config_file.close()
            self.settings_dict['waterlevel']=settings['waterlevel']
            self.settings_dict['colorA']=settings['colorA']
            self.settings_dict['colorB']=settings['colorB']
            self.settings_dict['colorC']=settings['colorC']
            self.settings_dict['colorD']=settings['colorD']
            self.settings_dict['colorWater']=settings['colorWater']
            self.settings_dict['shapeThreshLow']=settings['shapeThreshLow']
            self.settings_dict['shapeThreshHigh']=settings['shapeThreshHigh']
            self.settings_dict['minShapeSize']=settings['minShapeSize']
            self.settings_dict['refreshRate']=settings['refreshRate']
            return dict(settings)
        except Exception as ex:
            print("Error in Settings Manager",ex )
            return 0 

    def write(self):

        with open(self.filepath, "w") as outfile:
            json.dump(self.settings_dict, outfile)

    def write_standards(self):
        with open(self.filepath, "w") as outfile:
            json.dump(self.standard_dict, outfile)


    def get_settings(self):
        return self.settings_dict

    def change_col_corr(self, state):
        self.main_manager.toggle_color_correct(state)