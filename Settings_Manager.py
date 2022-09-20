import json

class Settings_Manager:
    def __init__(self,main_manager, filepath="config.json", load_standards = True ):
        self.filepath=filepath
        self.main_manager = main_manager
        self.standard_dict = {"waterlevel":70,
                         "colorA":(0,150,100,1),
                         "colorB":(150,240,190,1),
                         "colorC":(175,230,230,1),
                         "colorD":(150,200,200,1),
                         "colorE":(255,230,230,1),
                         "colorF":(150,200,255,1),
                         "colorWater":(200,50,0,1),
                         "colorDeepWater":(250,50,0,1),
                         "mainScreenHeight":2160,
                         "mainScreenWidth":3840,
                         "projectorWidth":1920,
                         "projectorHeight":1080, 
                         "markerSize":50,
                         "displayMarkers":1,
                         "refreshRate":1,
                         "addBrightness":90
                         }
        self.settings_dict = {"waterlevel":150,
                         "colorA":(0,50,0),
                         "colorB":(0,100,100),
                         "colorC":(0,150,100),
                         "colorD":(0,200,100),
                         "colorE":(255,230,230),
                         "colorF":(150,200,255),
                         "colorWater":(200,50,0),
                         "colorDeepWater":(250,50,0),
                         "mainScreenHeight":2160,
                         "mainScreenWidth":3840,
                         "projectorWidth":1920,
                         "projectorHeight":1080, 
                         "markerSize":100,
                         "displayMarkers":1,
                         "refreshRate":1,
                         "addBrightness":90
                         }
        if load_standards==True:
           self.write_standards()
        self.read()

    #allows other components/classes to alter settings
    #parameter=parameter name (see dictionary above)
    #value=what value to set for that parameter 
    def alter_setting(self,parameter, value):
        if not parameter.__contains__("color"): 
            self.settings_dict[parameter] = value 
            self.main_manager.update_settings_hook(self.settings_dict)
            self.write()
        else:
            self.settings_dict[parameter[3:]] = [value[0],value[1],value[2]]
            self.main_manager.update_settings_hook(self.settings_dict)
            self.write()

    #gathers the settings from a file 
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
            self.settings_dict['colorE']=settings['colorE']
            self.settings_dict['colorF']=settings['colorF']
            self.settings_dict['colorWater']=settings['colorWater']
            self.settings_dict['colorDeepWater']=settings['colorDeepWater']
            self.settings_dict['shapeThreshLow']=settings['shapeThreshLow']
            self.settings_dict['shapeThreshHigh']=settings['shapeThreshHigh']
            self.settings_dict['minShapeSize']=settings['minShapeSize']
            self.settings_dict['refreshRate']=settings['refreshRate']
            return dict(settings)
        except Exception as ex:
            print("Error in Settings Manager",ex )
            return 0 

    #writes settings to file 
    def write(self):

        with open(self.filepath, "w") as outfile:
            json.dump(self.settings_dict, outfile)

    #writes standard settings to file (reset )
    def write_standards(self):
        with open(self.filepath, "w") as outfile:
            json.dump(self.standard_dict, outfile)

    #returns the setting dictionary 
    def get_settings(self):
        return self.settings_dict

