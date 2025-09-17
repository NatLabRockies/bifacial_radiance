'''
Saving and reading data from a config.ini file.
'''
import os
try:
    import tkinter as tk
    from tkinter import ttk
except:
    import Tkinter as tk
    import ttk

import bifacial_radiance
import warnings

# aliases for Tkinter functions
END = tk.END
W = tk.W
Entry = tk.Entry
Button = tk.Button
Radiobutton = tk.Radiobutton
IntVar = tk.IntVar
PhotoImage = tk.PhotoImage

#global DATA_PATH # path to data files including module.json.  Global context
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))
TEMP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'TEMP'))

class Window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("950x800")
        
        yscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = yscroll.set
        self.canvas['xscrollcommand'] = xscroll.set
        yscroll['command'] = self.canvas.yview
        xscroll['command'] = self.canvas.xview

        frame = tk.Frame(self.canvas)
        self.canvas.create_window(4, 4, window=frame, anchor='nw') # Canvas equivalent of pack()
        frame.bind("<Configure>", self._on_frame_configure)

        def select_testfolder():
            """ select folder to save Radiance structure to
            """
            msg = 'Select Folder for BifacialRadiance project'
            dirname = bifacial_radiance.main._interactive_directory(msg)
            entry_testfolder.delete(0, END)
            entry_testfolder.insert(0, dirname)
            
        def select_local_weatherfile():
            """ select local weatherfile
            """
            msg = 'Select EPW or TMY .csv file'
            filename = bifacial_radiance.main._interactive_load(msg)
            entry_epwfile.delete(0, END)
            entry_epwfile.insert(0, filename)            
        
        def select_inputvariablefile():
            """ select input parameter .ini file
            """
            msg = 'Select simulation .ini file to save or load'
            
            """
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw() #Start interactive file input
            root.attributes("-topmost", True) #Bring window into foreground
            return filedialog.askopenfilename(parent=root, title=title) #initialdir = data_dir
            """     
                    
            variablefile = bifacial_radiance.main._interactive_load(msg)            
            
            entry_inputvariablefile.delete(0, END)
            entry_inputvariablefile.insert(0, variablefile) 
            pass
    
        def read_valuesfromGUI():
            '''
            List of all the variables read:
                
            testfolder, weatherfile, weatherinputMode, simulation,
            moduletype, rewriteModule, cellLevelModule, axisofrotationTorqueTube,
            torqueTube, fixedortracking,  cumulativesky, 
            selectTimes, lat, lon,   
            entry_starttime, entry_endtime,
            numberofPanels, x, y, bifi, xgap, ygap, zgap, 
            GCRorPitch, gcr, pitch, albedo, nMods, nRows, azimuth, tilt,
            clearanceheight, hubheight, axis_azimuth, backtrack, limitangle, angledelta,
            diameter, tubeType, torqueTubeMaterial, sensorsy, modWanted, rowWanted,
            numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap,
            
            
            '''

            
            testfolder, weatherfile, weatherinputMode, simulation,\
            moduletype, rewriteModule, cellLevelModule, axisofrotationTorqueTube,\
            torqueTube, fixedortracking,  cumulativesky,\
            selectTimes, lat, lon, \
            endtime, starttime, \
            numberofPanels, x, y, bifi, xgap, ygap, zgap, \
            GCRorPitch, gcr, pitch, albedo, nMods, nRows, azimuth, tilt,\
            clearanceheight, hubheight, axis_azimuth, backtrack, limitangle, angledelta,\
            diameter, tubeType, torqueTubeMaterial, sensorsy, modWanted, rowWanted,\
            numcellsx, numcellsy, xcell, ycell, xcellgap, ycellgap, invisible = \
            None, None, None, None, None, None, None, None, None, None, \
            None, None, None, None, None, None, None, None, None, None, \
            None, None, None, None, None, None, None, None, None, None, \
            None, None, None, None, None, None, None, None, None, None, \
            None, None, None, None, None, None, None, None, None, None
            
            
            try: inputvariablefile = entry_inputvariablefile.get()
            except: inputvariablefile = os.path.join('data','default.ini')
            
            # Initializing
            selectTimes = False
            if rb_fixedortracking.get() == 0: 
                fixedortracking=False # False, fixed. Fixed, Cumulative Sky Yearly
                cumulativesky = True
            if rb_fixedortracking.get() == 1: 
                fixedortracking=False # True, 'tracking' Fixed, Cumulative Sky with Start/End
                cumulativesky = True
                selectTimes = True #TODO: check this out. new 8/20/19
            if rb_fixedortracking.get() == 2: 
                fixedortracking=False # True, 'tracking'  Fixed, Hourly with Start/End times
                cumulativesky = False
                selectTimes = True 
            if rb_fixedortracking.get() == 3: 
                fixedortracking=False # True, 'tracking'  Fixed, Hourly for the Whole Year
                cumulativesky = False
            if rb_fixedortracking.get() == 4: 
                fixedortracking=True # True, 'tracking'  Tracking, Cumulative Sky Yearly
                cumulativesky = True
            if rb_fixedortracking.get() == 5: 
                fixedortracking=True # True, 'tracking' Tracking, Hourly with Start/End times
                cumulativesky = False
                selectTimes = True #TODO: check this out. new 8/20/19
            if rb_fixedortracking.get() == 6: 
                fixedortracking=True # True, 'tracking' Tracking, Hourly for the Whole Year
                cumulativesky = False
            
            # TODO: Improve validation method.
            try: albedo = entry_albedo.get() #this can either be a number or a material string
            except: print("ALBEDO: Please type in a number!")
            if len(entry_angledelta.get()) != 0:
                angledelta = float(entry_angledelta.get())
            if len(entry_axis_azimuth.get()) != 0:
                axis_azimuth =  float(entry_axis_azimuth.get())
            if len(entry_azimuth.get()) != 0:
                azimuth =  float(entry_azimuth.get())
            if len(entry_bifi.get()) != 0:
                bifi = float( entry_bifi.get())
            if len(entry_clearanceheight.get()) != 0:
                clearanceheight =  float(entry_clearanceheight.get())
            if len(entry_diameter.get()) != 0:
                diameter = float(entry_diameter.get())
            if len(entry_epwfile.get()) != 0:
                weatherfile = entry_epwfile.get()
            if len(entry_gcr.get()) != 0:
                gcr = float(entry_gcr.get())
            if len(entry_getepwfileLat.get()) != 0:
                lat = float(entry_getepwfileLat.get())
            if len(entry_getepwfileLong.get()) != 0:
                lon = float(entry_getepwfileLong.get())
            if len(entry_hubheight.get()) != 0:
                hubheight = float(entry_hubheight.get())
            if len(entry_limitangle.get()) != 0:
                limitangle = float(entry_limitangle.get())
            if len(entry_moduletype.get()) != 0:
                moduletype = entry_moduletype.get()
            if len(entry_modWanted.get()) != 0:
                modWanted = int(entry_modWanted.get())
            if len(entry_nMods.get()) != 0:
                nMods = int(entry_nMods.get())
            if len(entry_nRows.get()) != 0:
                nRows = int(entry_nRows.get())
            if len(entry_numberofPanels.get()) != 0:
                numberofPanels = int(entry_numberofPanels.get())
            if len(entry_numcellsx.get()) != 0:
                numcellsx = int(entry_numcellsx.get())
            if len(entry_numcellsy.get()) != 0:
                numcellsy = int(entry_numcellsy.get())
            if len(entry_pitch.get()) != 0:
                pitch = float(entry_pitch.get())
            if len(entry_rowWanted.get()) != 0:
                rowWanted = int(entry_rowWanted.get())
            if len(entry_sensorsy.get()) != 0:
                sensorsy = (entry_sensorsy.get())
            if len(entry_simulation.get()) != 0:
                simulation = entry_simulation.get()
            if len(entry_testfolder.get()) != 0:
                testfolder = entry_testfolder.get()
            if len(entry_tilt.get()) != 0:
                tilt = float(entry_tilt.get())
            if len(entry_x.get()) != 0:
                x = float(entry_x.get())
            if len(entry_xcell.get()) != 0:
                xcell = float(entry_xcell.get())
            if len(entry_xcellgap.get()) != 0:
                xcellgap = float(entry_xcellgap.get())
            if len(entry_y.get()) != 0:
                y = float(entry_y.get())
            if len(entry_ycell.get()) != 0:
                ycell = float(entry_ycell.get())
            if len(entry_ycellgap.get()) != 0:
                ycellgap = float(entry_ycellgap.get())
            if len(entry_xgap.get()) != 0:
                xgap = float(entry_xgap.get())
            if len(entry_ygap.get()) != 0:
                ygap = float(entry_ygap.get())
            if len(entry_zgap.get()) != 0:
                zgap = float(entry_zgap.get())


            if len(entry_endtime.get()) != 0:
               endtime = entry_endtime.get()
            if len(entry_starttime.get()) != 0:
                starttime = entry_starttime.get()


            if rb_axisofrotation.get() == 0: axisofrotationTorqueTube=True
            if rb_axisofrotation.get() == 1: axisofrotationTorqueTube=False
    
            if rb_backtrack.get() == 0: backtrack=True
            if rb_backtrack.get() == 1: backtrack=False
    
            if rb_cellLevelModule.get() == 0: cellLevelModule=False
            if rb_cellLevelModule.get() == 1: cellLevelModule=True
 

            
                
            if rb_GCRorPitch.get() == 0: GCRorPitch='gcr'
            if rb_GCRorPitch.get() == 1: GCRorPitch='pitch'
    
            if rb_rewriteModule.get() == 0: rewriteModule=True
            if rb_rewriteModule.get() == 1: rewriteModule=False

            if rb_torqueTube.get() == 0: torqueTube=True
            if rb_torqueTube.get() == 1: torqueTube=False
            
            if rb_torqueTubeMaterial.get() == 0: torqueTubeMaterial='Metal_Grey'
            if rb_torqueTubeMaterial.get() == 1: torqueTubeMaterial='black'
            if rb_torqueTubeMaterial.get() == 2: invisible=True; torqueTubeMaterial='black'
    
            if rb_tubeType.get() == 0: tubeType='round'
            if rb_tubeType.get() == 1: tubeType='square'  
            if rb_tubeType.get() == 2: tubeType='hex'
            if rb_tubeType.get() == 3: tubeType='oct'
          
            if rb_weatherinputModule.get() == 0: weatherinputMode='True'   # True gets epw
            if rb_weatherinputModule.get() == 1: weatherinputMode='False'  # False reads epw or TMY

            #TODO: add validation for inputs depending on options selected
            
            
            simulationParamsDict = {}
            sceneParamsDict = {}
            timeControlParamsDict = {}
            trackingParamsDict = {}
            torquetubeParamsDict = {}
            moduleParamsDict = {}
            analysisParamsDict = {}
            cellModuleDict = {}
            
            if testfolder is not None: simulationParamsDict['testfolder'] = testfolder
            if weatherfile is not None: simulationParamsDict['weatherFile'] = weatherfile 
            if weatherinputMode is not None: simulationParamsDict['getEPW'] = weatherinputMode
            if simulation is not None: simulationParamsDict['simulationname'] = simulation
            if moduletype is not None: simulationParamsDict['moduletype'] = moduletype
            if rewriteModule is not None: simulationParamsDict['rewriteModule'] = rewriteModule
            if cellLevelModule is not None: simulationParamsDict['cellLevelModule'] = cellLevelModule
            if axisofrotationTorqueTube is not None: simulationParamsDict['axisofrotationTorqueTube'] = axisofrotationTorqueTube
            if torqueTube is not None: simulationParamsDict['torqueTube'] = torqueTube
            simulationParamsDict['hpc'] =  False #Fix
            if fixedortracking is not None: simulationParamsDict['tracking'] =  fixedortracking
            if cumulativesky is not None: simulationParamsDict['cumulativeSky'] =  cumulativesky
            if selectTimes is not None: simulationParamsDict['selectTimes'] =  selectTimes            
            if lat is not None: simulationParamsDict['latitude'] = lat
            if lon is not None: simulationParamsDict['longitude'] = lon
            simulationParamsDict['saveImage'] =  True 
            
            if entry_starttime is not None: timeControlParamsDict['starttime'] =  starttime
            if entry_endtime is not None: timeControlParamsDict['endtime'] =  endtime
        
            if numberofPanels is not None: moduleParamsDict['numpanels'] =  numberofPanels 
            if x is not None: moduleParamsDict['x'] =  x 
            if y is not None: moduleParamsDict['y'] =  y
            if bifi is not None: moduleParamsDict['bifi'] =  bifi 
            if xgap is not None: moduleParamsDict['xgap'] =  xgap
            if ygap is not None: moduleParamsDict['ygap'] =  ygap 
            if zgap is not None: moduleParamsDict['zgap'] =  zgap
            if GCRorPitch is not None: sceneParamsDict['gcrorpitch'] =  GCRorPitch
            #print('gcr or pitch: {}'.format(GCRorPitch))
            if GCRorPitch == 'gcr' and gcr is not None:
                sceneParamsDict['gcr'] =  gcr
            elif pitch is not None:
                sceneParamsDict['pitch'] =  pitch
            if albedo is not None: sceneParamsDict['albedo'] =  albedo
            if nMods is not None: sceneParamsDict['nMods'] = nMods 
            if nRows is not None: sceneParamsDict['nRows'] =  nRows
            if azimuth is not None: sceneParamsDict['azimuth'] =  azimuth 
            if tilt is not None: sceneParamsDict['tilt'] =  tilt
            if clearanceheight is not None: sceneParamsDict['clearance_height'] =  clearanceheight 
            if hubheight is not None: sceneParamsDict['hub_height'] =  hubheight
            if axis_azimuth is not None: sceneParamsDict['axis_azimuth'] = axis_azimuth
                    
            if backtrack is not None: trackingParamsDict['backtrack'] =  backtrack 
            if limitangle is not None: trackingParamsDict['limit_angle'] =  limitangle
            if angledelta is not None: trackingParamsDict['angle_delta'] =  angledelta
            
            if torqueTube:
                if diameter is not None: torquetubeParamsDict['diameter'] =  diameter 
                if tubeType is not None: torquetubeParamsDict['tubetype'] =  tubeType
    
                if torqueTubeMaterial is not None: torquetubeParamsDict['material'] =  torqueTubeMaterial
                if invisible: torquetubeParamsDict['visible'] = False
            
            if sensorsy is not None: analysisParamsDict['sensorsy'] =  sensorsy 
            if modWanted is not None: analysisParamsDict['modWanted'] =  modWanted
            if rowWanted is not None: analysisParamsDict['rowWanted'] =  rowWanted
            
            if numcellsx is not None: cellModuleDict['numcellsx'] =  numcellsx
            if numcellsy is not None: cellModuleDict['numcellsy'] =  numcellsy
            if xcell is not None: cellModuleDict['xcell'] =  xcell 
            if ycell is not None: cellModuleDict['ycell'] =  ycell
            if xcellgap is not None: cellModuleDict['xcellgap'] =  xcellgap 
            if ycellgap is not None: cellModuleDict['ycellgap'] =  ycellgap

            # Creating None dictionaries for those empty ones
            if timeControlParamsDict == {}:
                timeControlParamsDict = None
            
            if moduleParamsDict == {}:
                moduleParamsDict = None
            
            if trackingParamsDict == {}:
                trackingParamsDict = None
            
            if torquetubeParamsDict == {}:
                torquetubeParamsDict = None
            
            if analysisParamsDict == {}:
                analysisParamsDict = None
            
            if cellModuleDict == {}:
                cellModuleDict = None

            print("Read all values")            
            return simulationParamsDict, sceneParamsDict, timeControlParamsDict, \
                moduleParamsDict, trackingParamsDict, torquetubeParamsDict, \
                analysisParamsDict, cellModuleDict, inputvariablefile;
        
        def save_inputfile(savetitle=None):
    
            import bifacial_radiance.load
            
            simulationParamsDict, sceneParamsDict, timeControlParamsDict, \
            moduleParamsDict, trackingParamsDict, torquetubeParamsDict, \
            analysisParamsDict, cellModuleDict, inputvariablefile  = read_valuesfromGUI()

            if savetitle is None:
                savetitle = inputvariablefile
                
            bifacial_radiance.load.savedictionariestoConfigurationIniFile(simulationParamsDict, sceneParamsDict, 
                                                                          timeControlParamsDict, moduleParamsDict, 
                                                                          trackingParamsDict, torquetubeParamsDict, 
                                                                          analysisParamsDict, cellModuleDict, 
                                                                          inifilename=savetitle)
            print("Saved all Values to %s " % savetitle)
            
            
        def runBifacialRadiance():
            #TODO:
            # Check if logic is correct. ModelChain itself saves the input values
            # into a .ini file in the correct folder.
            
            #TODO:
            # Add validation that needed inputs are present?
            #import bifacial_radiance.modelchain
            
            simulationParamsDict, sceneParamsDict, timeControlParamsDict, \
            moduleParamsDict, trackingParamsDict, torquetubeParamsDict,   \
            analysisParamsDict, cellModuleDict, inputvariablefile = read_valuesfromGUI()
            
            #get a return out of runModelChain and pass it back out of the GUI.
            self.data, analysis  = bifacial_radiance.modelchain.runModelChain(simulationParamsDict=simulationParamsDict, 
                                                       sceneParamsDict=sceneParamsDict, 
                                                       timeControlParamsDict=timeControlParamsDict,
                                                       moduleParamsDict=moduleParamsDict, 
                                                       trackingParamsDict=trackingParamsDict, 
                                                       torquetubeParamsDict=torquetubeParamsDict, 
                                                       analysisParamsDict=analysisParamsDict, 
                                                       cellModuleDict=cellModuleDict
                    )            
        
        def setDefaultValues():
            #TODO: read default.ini from data folder and set this automatically.
            entry_albedo.insert(0,"0.62")
            entry_angledelta.insert(0,"5")
            entry_axis_azimuth.insert(0,"180")
            entry_azimuth.insert(0,"180")
            entry_clearanceheight.insert(0,"0.8")
            entry_endtime.insert(0,"06_21_12")
            entry_epwfile.insert(0, r"EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw") #FIX
            entry_gcr.insert(0,"0.35")
            entry_getepwfileLat.insert(0,"33")
            entry_getepwfileLong.insert(0,"-110")
            entry_hubheight.insert(0,"0.9")
            entry_inputvariablefile.insert(0, "BB") #FIX
            entry_limitangle.insert(0,"60")
            entry_modWanted.insert(0,"") #was 10
            entry_nMods.insert(0,"20")
            entry_nRows.insert(0,"7")
            entry_pitch.insert(0,"10")
            entry_rowWanted.insert(0,"") #was 3
            entry_sensorsy.insert(0,"10")
            entry_simulation.insert(0,"Demo1")
            entry_starttime.insert(0,"06_21_12")
            entry_testfolder.insert(0, TEMP_PATH) 
            entry_tilt.insert(0,"10")

            # Module parameters - populate by loading first module in module.json
            """
            entry_bifi.insert(0,"0.9")     
            entry_numberofPanels.insert(0,"2")
            entry_numcellsx.insert(0,"12")
            entry_numcellsy.insert(0,"6")
            entry_diameter.insert(0,"0.1")
            entry_x.insert(0,"0.98")
            entry_xcell.insert(0,"0.15")
            entry_xcellgap.insert(0,"0.01")
            entry_y.insert(0,"1.98")
            entry_ycell.insert(0,"0.15")
            entry_ycellgap.insert(0,"0.01")
            entry_xgap.insert(0,"0.05")
            entry_ygap.insert(0,"0.15")
            entry_zgap.insert(0,"0.10")
            """


            
        def activateAllEntries():
            entry_albedo.config(state='normal')
            entry_angledelta.config(state='normal')
            entry_axis_azimuth.config(state='normal')
            entry_azimuth.config(state='normal')
            entry_bifi.config(state='normal')
            entry_clearanceheight.config(state='normal')
            entry_diameter.config(state='normal')
            entry_endtime.config(state='normal')
            entry_epwfile.config(state='normal')
            entry_gcr.config(state='normal')
            entry_getepwfileLat.config(state='normal')
            entry_getepwfileLong.config(state='normal')
            entry_hubheight.config(state='normal')
            entry_inputvariablefile.config(state='normal')
            entry_limitangle.config(state='normal')
            entry_moduletype.config(state='normal')
            entry_modWanted.config(state='normal')
            entry_nMods.config(state='normal')
            entry_nRows.config(state='normal')
            entry_numberofPanels.config(state='normal')
            entry_numcellsx.config(state='normal')
            entry_numcellsy.config(state='normal')
            entry_pitch.config(state='normal')
            entry_rowWanted.config(state='normal')
            entry_sensorsy.config(state='normal')
            entry_simulation.config(state='normal')
            entry_starttime.config(state='normal')
            entry_testfolder.config(state='normal')
            entry_tilt.config(state='normal')
            entry_x.config(state='normal')
            entry_xcell.config(state='normal')
            entry_xcellgap.config(state='normal')
            entry_y.config(state='normal')
            entry_ycell.config(state='normal')
            entry_ycellgap.config(state='normal')
            entry_xgap.config(state='normal')
            entry_ygap.config(state='normal')
            entry_zgap.config(state='normal')

        def read_inputfile():
            r''' First it activates all entries, cleares all values, 
            assigns read values, and then pushes the right radio buttons in the
            proper order so cells are activatd or not
            '''

            import bifacial_radiance.load
            
            try: inputvariablefile = entry_inputvariablefile.get()
            except: inputvariablefile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\data\default.ini'

            #TODO: remove this file below used for developemnt
            #inputvariablefile = r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\bifacial_radiance\data\default.ini'

            simulationParamsDict, sceneParamsDict, timeControlParamsDict,\
            moduleParamsDict, trackingParamsDict, torquetubeParamsDict, \
            analysisParamsDict, cellModuleDict = bifacial_radiance.load.readconfigurationinputfile(inputvariablefile)
            
            # TODO: Think if this procedure is correct.
            # readconfigurationfile already validates inputs in the configuration file.
            # this just assigns it to them.
            # Maybe print which inputs are being discarded because of options selected?

            activateAllEntries()
            clearAllValues()      
            

            #TODO: Validate empty inputs reading/entry or none dictionaries
            try: entry_testfolder.insert(0,simulationParamsDict['testfolder'])
            except: pass
            try: entry_epwfile.insert(0,simulationParamsDict['weatherFile'])
            except: pass
            try: entry_getepwfileLong.insert(0,simulationParamsDict['longitude'])
            except: pass
            try: entry_getepwfileLat.insert(0,simulationParamsDict['latitude'])
            except: pass
            entry_simulation.insert(0,simulationParamsDict['simulationname'])
            entry_moduletype.insert(0,simulationParamsDict['moduletype'])
            
            #timeControlParamsDict
            try: entry_starttime.insert(0,timeControlParamsDict['starttime'])
            except: pass
            try: entry_endtime.insert(0,timeControlParamsDict['endtime'])
            except: pass

            #moduleParamsDict
            try: entry_numberofPanels.insert(0,moduleParamsDict['numpanels'])
            except: pass
            try: entry_x.insert(0,moduleParamsDict['x'])
            except: pass
            try: entry_y.insert(0,moduleParamsDict['y'])
            except: pass
            try: entry_bifi.insert(0,moduleParamsDict['bifi'])
            except: pass
            try: entry_xgap.insert(0,moduleParamsDict['xgap'])
            except: pass
            try: entry_ygap.insert(0,moduleParamsDict['ygap'])
            except: pass
            try: entry_zgap.insert(0,moduleParamsDict['zgap'])
            except: pass
            
            #sceneParamsDict
            try: entry_gcr.insert(0,sceneParamsDict['gcr'])
            except: pass
            try: entry_pitch.insert(0,sceneParamsDict['pitch'])
            except: pass
            entry_albedo.insert(0,sceneParamsDict['albedo'])        
            try: entry_nMods.insert(0,sceneParamsDict['nMods'])
            except: pass
            try: entry_nRows.insert(0,sceneParamsDict['nRows'])
            except: pass
            try: entry_azimuth.insert(0,sceneParamsDict['azimuth'])
            except: pass
            try: entry_tilt.insert(0,sceneParamsDict['tilt'])
            except: pass
            try: entry_clearanceheight.insert(0,sceneParamsDict['clearance_height'])
            except: pass
            try: entry_hubheight.insert(0,sceneParamsDict['hub_height'])
            except: pass
            try: entry_axis_azimuth.insert(0,sceneParamsDict['axis_azimuth'])
            except: pass

            #trackingParamsDict
            try: entry_angledelta.insert(0,trackingParamsDict['angle_delta'])
            except: pass
            try: entry_limitangle.insert(0,trackingParamsDict['limit_angle'])
            except: pass
            #torquetubeParamsDict
            try: entry_diameter.insert(0,torquetubeParamsDict['diameter'])
            except: pass
        
            #analysisParamsDict
            try: entry_sensorsy.insert(0,analysisParamsDict['sensorsy'])
            except: pass
            try: entry_modWanted.insert(0,analysisParamsDict['modWanted'])
            except: pass
            try: entry_rowWanted.insert(0,analysisParamsDict['rowWanted'])
            except: pass
        
            #cellModuleDict
            try: entry_numcellsx.insert(0,cellModuleDict['numcellsx'])
            except: pass
            try: entry_numcellsy.insert(0,cellModuleDict['numcellsy'])
            except: pass
            try: entry_xcell.insert(0,cellModuleDict['xcell'])
            except: pass
            try: entry_xcellgap.insert(0,cellModuleDict['xcellgap'])
            except: pass
            try: entry_ycell.insert(0,cellModuleDict['ycell'])
            except: pass
            try: entry_ycellgap.insert(0,cellModuleDict['ycellgap'])
            except: pass
          
            # EPW boolean
            if simulationParamsDict['getEPW']:
                rad1_weatherinputModule.invoke() # get ePW activates if true
            else: 
                rad2_weatherinputModule.invoke() # read EPW activates
                      
            if simulationParamsDict['rewriteModule']:
                rad1_rewriteModule.invoke()
            else: 
                rad2_rewriteModule.invoke()
            
            #
            if simulationParamsDict['tracking']:
                if simulationParamsDict['cumulativeSky']:
                    rad5_fixedortracking.invoke()
                else: # Hourly
                    if simulationParamsDict['selectTimes']:
                        rad7_fixedortracking.invoke()
                    else:
                        rad8_fixedortracking.invoke()
            else:  # fixed tilt
                if simulationParamsDict['cumulativeSky']:
                    if simulationParamsDict['selectTimes']:
                        rad2_fixedortracking.invoke()
                    else: # full year
                        rad1_fixedortracking.invoke()
                else:  
                    if simulationParamsDict['selectTimes']:
                        rad3_fixedortracking.invoke()
                    else:
                        rad4_fixedortracking.invoke()
                #if simulationParamsDict['selectTimes']:
                #    print("Error on simulation control. No daydate simulation option available for fixed systems. Do timestamps Range!")
                                
            # FIX THIS ONE IS NOT WORKING WHY.
            if simulationParamsDict['axisofrotationTorqueTube']:
                rad2_axisofrotation.invoke()  # if false, rotate around panels
            else: 
                rad1_axisofrotation.invoke() # if true, rotate around torque tube.

            try:
                # backtracking boolean
                if trackingParamsDict['backtrack']:
                    rad1_backtrack.invoke()
                else: 
                    rad2_backtrack.invoke()
            except: pass    
                
            # torqueTube boolean
            if simulationParamsDict['torqueTube']:
                rad1_torqueTube.invoke()
            else:
                rad2_torqueTube.invoke()

            # tubeType
            try:
                if torquetubeParamsDict['tubetype'] == 'oct' or torquetubeParamsDict['tubetype'] == 'Oct' :
                    rad4_tubeType.invoke() 
                    #rad4_tubeType.config(state='normal')
                elif torquetubeParamsDict['tubetype'] == 'hex' or torquetubeParamsDict['tubetype'] == 'Hex':
                    rad3_tubeType.invoke()
                    #rad3_tubeType.config(state='normal')
                elif torquetubeParamsDict['tubetype'] == 'square' or torquetubeParamsDict['tubetype'] == 'Square':
                    rad2_tubeType.invoke()
                    #rad2_tubeType.config(state='normal')
                elif torquetubeParamsDict['tubetype'] == 'round' or torquetubeParamsDict['tubetype'] == 'Round':
                    rad1_tubeType.invoke()
                    #rad1_tubeType.config(state='normal')
                else:
                    print ("wrong type of tubeType passed in input file")
            except:
                pass
                      
            # torqueTubeMaterial
            try:
                if torquetubeParamsDict['invisible'] is True:
                    rad3_torqueTubeMaterial.invoke()
                elif torquetubeParamsDict['material'] == 'Metal_Grey':
                    rad1_torqueTubeMaterial.invoke()
                elif torquetubeParamsDict['material'].lower() == 'black' :
                    rad2_torqueTubeMaterial.invoke()
                else:
                    print ("wrong type of torquetubeMaterial passed in input file. Options: 'Metal_Grey' or 'black'")
            except:
                pass
            
            # cellLevelModule boolean
            if simulationParamsDict['cellLevelModule']: # If True, activate 2nd radio button.
                rad2_cellLevelModule.invoke()
            else:
                rad1_cellLevelModule.invoke()
            
            # gcrorpitch option
            try: 
                if sceneParamsDict['gcrorpitch'] == 'gcr' or sceneParamsDict['gcrorpitch'] == 'GCR':  # If True, activate 2nd radio button.
                    rad1_GCRorPitch.invoke()
                elif sceneParamsDict['gcrorpitch'] == 'pitch' or sceneParamsDict['gcrorpitch'] == 'pitch':
                    rad2_GCRorPitch.invoke()
                else:
                    print ("wrong type of GCR or pitch optoin on gcrorpitch in sceneParamsDict in input file. Options: 'gcr' or 'pitch'")
            except:
                pass

            print ("Finish reading file %s " % inputvariablefile)
                        
        def setdefaultGray():
            #Labels that should be inactive
            epwfile_label.config(state='disabled')
            startdate_label.config(state='disabled')
            enddate_label.config(state='disabled')
            backtrack_label.config(state='disabled')
            limitangle_label.config(state='disabled')
            angledelta_label.config(state='disabled')
            axisofrotation_label.config(state='disabled')
            numcellsx_label.config(state='disabled')
            numcellsy_label.config(state='disabled')
            xcell_label.config(state='disabled')
            ycell_label.config(state='disabled')
            xcellgap_label.config(state='disabled')
            ycellgap_label.config(state='disabled')
            pitch_label.config(state='disabled')
            axis_azimuth_label.config(state='disabled')
            hubheight_label.config(state='disabled')

            #Entries that should be inactive
            entry_epwfile.config(state='disabled')
            entry_limitangle.config(state='disabled')
            entry_angledelta.config(state='disabled')
            entry_numcellsx.config(state='disabled')
            entry_numcellsy.config(state='disabled')
            entry_xcell.config(state='disabled')
            entry_ycell.config(state='disabled')
            entry_xcellgap.config(state='disabled')
            entry_ycellgap.config(state='disabled')
            entry_pitch.config(state='disabled')
            entry_axis_azimuth.config(state='disabled')
            entry_hubheight.config(state='disabled')
            
            #buttons that should be inactive
            epwfile_button.config(state='disabled')                

            #Radiobuttons that should be disabled
            rad1_axisofrotation.config(state='disabled')
            rad2_axisofrotation.config(state='disabled')
            rad1_backtrack.config(state='disabled')
            rad2_backtrack.config(state='disabled')
          

        def setdefaultActive():
            #Labels that should be active
            getepwfile_label.config(state='normal')
            azimuth_label.config(state='normal')
            clearanceheight_label.config(state='normal')
            x_label.config(state='normal')
            y_label.config(state='normal')
            gcr_label.config(state='normal')
            tubeType_label.config(state='normal')
            torqueTubeMaterial_label.config(state='normal')

            #Radiobuttons that should be enabled
            rad1_tubeType.config(state='normal')
            rad2_tubeType.config(state='normal')
            rad3_tubeType.config(state='normal')
            rad4_tubeType.config(state='normal')
            rad1_torqueTubeMaterial.config(state='normal')
            rad2_torqueTubeMaterial.config(state='normal')
            rad3_torqueTubeMaterial.config(state='normal')
            
        def clearAllValues():

            entry_albedo.delete(0,END)
            entry_angledelta.delete(0,END)
            entry_axis_azimuth.delete(0,END)
            entry_azimuth.delete(0,END)
            entry_bifi.delete(0,END)
            entry_clearanceheight.delete(0,END)
            entry_diameter.delete(0,END)
            entry_endtime.delete(0,END)
            entry_epwfile.delete(0,END)
            entry_gcr.delete(0,END)
            entry_getepwfileLat.delete(0,END)
            entry_getepwfileLong.delete(0,END)
            entry_hubheight.delete(0,END)
            entry_inputvariablefile.delete(0,END)
            entry_limitangle.delete(0,END)
            entry_moduletype.delete(0,END)
            entry_modWanted.delete(0,END)
            entry_nMods.delete(0,END)
            entry_nRows.delete(0,END)
            entry_numberofPanels.delete(0,END)
            entry_numcellsx.delete(0,END)
            entry_numcellsy.delete(0,END)
            entry_pitch.delete(0,END)
            entry_rowWanted.delete(0,END)
            entry_sensorsy.delete(0,END)
            entry_simulation.delete(0,END)
            entry_starttime.delete(0,END)
            entry_testfolder.delete(0,END)
            entry_tilt.delete(0,END)
            entry_x.delete(0,END)
            entry_xcell.delete(0,END)
            entry_xcellgap.delete(0,END)
            entry_y.delete(0,END)
            entry_ycell.delete(0,END)
            entry_ycellgap.delete(0,END)
            entry_xgap.delete(0,END)
            entry_ygap.delete(0,END)
            entry_zgap.delete(0,END)

        def setDefaults():
            activateAllEntries()
            clearAllValues() # enables all entries
            setDefaultValues() # writes defaults to all Entries
            setdefaultActive() # selected labels and radiobuttons set to "normal"
            
            # Unselected
            rad2_weatherinputModule.deselect()
            rad2_tubeType.deselect()
            rad3_tubeType.deselect()
            rad4_tubeType.deselect()
            rad2_torqueTubeMaterial.deselect()
            rad3_torqueTubeMaterial.deselect()
            rad2_torqueTube.deselect()
            rad2_rewriteModule.deselect()
            rad2_GCRorPitch.deselect()
            rad2_fixedortracking.deselect()     
            rad3_fixedortracking.deselect()     
            rad4_fixedortracking.deselect()     
            rad5_fixedortracking.deselect()     
            rad7_fixedortracking.deselect()     
            rad8_fixedortracking.deselect()     
            rad2_cellLevelModule.deselect()    

            
            #Radio button Selected
            rad1_weatherinputModule.invoke()
            rad1_tubeType.invoke()
            rad1_torqueTubeMaterial.invoke()
            rad1_torqueTube.invoke()
            rad1_rewriteModule.invoke()
            rad1_GCRorPitch.invoke()
            rad1_cellLevelModule.invoke()
            rad1_fixedortracking.invoke()
            #rad1_timecontrol.invoke()
           # rad1_fixedortracking.invoke()
           # rad1_cumulativesky.invoke()
           #rad1_fixedortracking.config(state='normal')
            #rad1_timecontrol.config(state='normal')
            #rad1_cumulativesky.config(state='normal')


            
            # Configure Normal radiobuttons.
            rad1_weatherinputModule.config(state='normal')
            rad1_tubeType.config(state='normal')
            rad1_torqueTubeMaterial.config(state='normal')
            rad1_torqueTube.config(state='normal')
            rad1_rewriteModule.config(state='normal')
            rad1_GCRorPitch.config(state='normal')
            rad1_cellLevelModule.config(state='normal')
            

            rad1_backtrack.invoke()
            rad1_axisofrotation.invoke()
            rad1_backtrack.config(state='normal')
            rad1_axisofrotation.config(state='normal')
            rad2_backtrack.deselect()
            rad2_axisofrotation.deselect()
            #cdeline edits
            #rad1_cellLevelModule.invoke() # runs cellLevelModuleOff
            #rad1_cellLevelModule.config(state='normal')
            #rad2_cellLevelModule.deselect()

            setdefaultGray() # gray out labels, entries and rb.
            
        global fixedortracking
        fixedortracking='fixed'
        
        # Create all of the main containers
        #Col1
        maincontrol_frame = tk.Frame(frame, width=230, height=60)
        simulationcontrol_frame = tk.Frame(frame, width=180, height=30)
        trackingparams_frame = tk.Frame(frame, width=180, height=60)
        torquetubeparams_frame = tk.Frame(frame, width=230, height=60)
        
        #Col2
        imagevariables_frame = tk.Frame(frame, width=230, height=60)
        moduleparams_frame = tk.Frame(frame, width=230, height=60)
        sceneparams_frame = tk.Frame(frame, width=230, height=60)
        analysisparams_frame = tk.Frame(frame, width=230, height=60)
        

        
        maincontrol_frame.bind("<Configure>", self._on_frame_configure)
        simulationcontrol_frame.bind("<Configure>", self._on_frame_configure)
        trackingparams_frame.bind("<Configure>", self._on_frame_configure)
        torquetubeparams_frame.bind("<Configure>", self._on_frame_configure)
        imagevariables_frame.bind("<Configure>", self._on_frame_configure)
        moduleparams_frame.bind("<Configure>", self._on_frame_configure)
        sceneparams_frame.bind("<Configure>", self._on_frame_configure)
        analysisparams_frame.bind("<Configure>", self._on_frame_configure)
   
        
        maincontrol_frame.grid(row=0, column=0, sticky="ew")
        simulationcontrol_frame.grid(row=1, column=0, sticky="ew")
        trackingparams_frame.grid(row=2, column=0, sticky="ew")
        torquetubeparams_frame.grid(row=3, column=0, sticky="ew")
        
        imagevariables_frame.grid(row=0, column=1, sticky="ew")
        moduleparams_frame.grid(row=1, column=1, sticky="ew")
        sceneparams_frame.grid(row=2, column=1, sticky="ew")
        analysisparams_frame.grid(row=3, column=1, sticky="ew")
        
        
        # MAIN CONTROL
        ###################
        # Create the widgets for the maincontrol_frame
        def selGetEPW():
            getepwfile_label.config(state='normal')
            entry_getepwfileLat.config(state='normal')
            entry_getepwfileLong.config(state='normal')
            epwfile_label.config(state='disabled')
            entry_epwfile.config(state='disabled')
            epwfile_button.config(state='disabled')
        def selReadEPW():
            getepwfile_label.config(state='disabled')
            entry_getepwfileLat.config(state='disabled')
            entry_getepwfileLong.config(state='disabled')
            epwfile_label.config(state='normal')
            entry_epwfile.config(state='normal')
            epwfile_button.config(state='normal')
            
        maincontrol_label = ttk.Label(maincontrol_frame, background='lavender', text='Main Control', font=("Arial Bold", 15))
        maincontrol_label.grid(row = 0)
        inputvariablefile_label = ttk.Label(maincontrol_frame, background='orange', text='Input Variables File:')
        inputvariablefile_label.grid(row = 1, sticky=W)
        entry_inputvariablefile = Entry(maincontrol_frame, background="orange")
        entry_inputvariablefile.grid(row=1, column=1)
        inputvariablefile_button = Button(maincontrol_frame, width=10, text="Search", command=select_inputvariablefile)
        inputvariablefile_button.grid(column=2, row=1, sticky= W)         
        
        inputfileRead_button = Button(maincontrol_frame, text="READ", command=read_inputfile)
        inputfileRead_button.grid(column=0, row=2)   
        inputfileSave_button = Button(maincontrol_frame, text="SAVE", command=save_inputfile)
        inputfileSave_button.grid(column=1, row=2) 
        testfolder_label = ttk.Label(maincontrol_frame, background='lavender', text='TestFolder:')
        testfolder_label.grid(row = 3, sticky = W)
        entry_testfolder = Entry(maincontrol_frame, background="pink")
        entry_testfolder.grid(row=3, column=1)    
        testfolder_button = Button(maincontrol_frame, width=10, text="Search", command=select_testfolder)
        testfolder_button.grid(column=2, row=3, sticky= W) 
        
        
        rb_weatherinputModule=IntVar()
        rad1_weatherinputModule = ttk.Label(maincontrol_frame, background='lavender', text='WeatherFile Input:')
        rad1_weatherinputModule.grid(row = 4, sticky=W)
        rad1_weatherinputModule = Radiobutton(maincontrol_frame,background='lavender', variable=rb_weatherinputModule, text='GetEPW', value=0, command=selGetEPW)
        rad2_weatherinputModule = Radiobutton(maincontrol_frame,background='lavender', variable=rb_weatherinputModule, text='ReadEPW / TMY', value=1, command=selReadEPW)
        rad1_weatherinputModule.grid(column=1, row=4)
        rad2_weatherinputModule.grid(column=2, row=4)
        getepwfile_label = ttk.Label(maincontrol_frame, background='lavender', text='Get EPW (Lat/Lon):')
        getepwfile_label.grid(row = 5, sticky=W)
        entry_getepwfileLat = Entry(maincontrol_frame, background="white")
        entry_getepwfileLat.grid(row=5, column=1)
        #entry_getepwfileLat.insert(5,"33")
        entry_getepwfileLong = Entry(maincontrol_frame, background="white")
        entry_getepwfileLong.grid(row=5, column=2)
        epwfile_label = ttk.Label(maincontrol_frame, background='lavender', text='EPW / TMY File:', state='disabled')
        epwfile_label.grid(row = 6, sticky=W)
        entry_epwfile = Entry(maincontrol_frame, background="white", state='disabled')
        entry_epwfile.grid(row=6, column=1)
        epwfile_button = Button(maincontrol_frame, state='disabled', width=10, text="Search", command=select_local_weatherfile)
        epwfile_button.grid(column=2, row=6, sticky= W) 
        
        simulation_label = ttk.Label(maincontrol_frame, background='lavender', text='Simulation Name:')
        simulation_label.grid(row = 7, sticky=W)
        entry_simulation = Entry(maincontrol_frame, background="white")
        entry_simulation.grid(row=7, column=1)

#        customModule_label = ttk.Label(maincontrol_frame, background='lavender', text='Create Custom Module:')
#        customModule_label.grid(row = 9, sticky=W)
#        rb_customModule=IntVar()
#        rad1_customModule = Radiobutton(maincontrol_frame,background='lavender', variable=rb_customModule, text='True', value=0)
#        rad2_customModule = Radiobutton(maincontrol_frame,background='lavender', variable=rb_customModule, text='False', value=1)

        
    
        # Simulation CONTROL
        ###################
    
        def selfixed():
            global fixedortracking
            fixedortracking='fixed'
            
            buttonImage.configure(image=image_fixed)
            
            azimuth_label.config(state='normal')
            entry_azimuth.config(state='normal')
            clearanceheight_label.config(state='normal') 
            entry_clearanceheight.config(state='normal')
            tilt_label.config(state='normal')
            entry_tilt.config(state='normal')
        
            axis_azimuth_label.config(state='disabled')
            entry_axis_azimuth.config(state='disabled')
            hubheight_label.config(state='disabled')
            entry_hubheight.config(state='disabled')
            
            backtrack_label.config(state='disabled')
            rad1_backtrack.config(state='disabled') 
            rad2_backtrack.config(state='disabled')
            limitangle_label.config(state='disabled')
            entry_limitangle.config(state='disabled')
            angledelta_label.config(state='disabled')
            entry_angledelta.config(state='disabled')
            
            axisofrotation_label.config(state='disabled')
            rad1_axisofrotation.config(state='disabled')
            rad2_axisofrotation.config(state='disabled')
    
    
        def selHSAT():
            global fixedortracking
            fixedortracking='tracking'       
            buttonImage.configure(image=image_tracked)       

            azimuth_label.config(state='disabled')
            entry_azimuth.config(state='disabled')
            clearanceheight_label.config(state='disabled')  
            entry_clearanceheight.config(state='disabled') 
            tilt_label.config(state='disabled')
            entry_tilt.config(state='disabled')
            
            axis_azimuth_label.config(state='normal')
            entry_axis_azimuth.config(state='normal')
            hubheight_label.config(state='normal')
            entry_hubheight.config(state='normal')
            
            backtrack_label.config(state='normal')
            rad1_backtrack.config(state='normal') 
            rad2_backtrack.config(state='normal')
            limitangle_label.config(state='normal')
            entry_limitangle.config(state='normal')
            angledelta_label.config(state='normal')
            entry_angledelta.config(state='normal')
             
            axisofrotation_label.config(state='normal')
            rad1_axisofrotation.config(state='normal')
            rad2_axisofrotation.config(state='normal')

        def tcAll():
            startdate_label.config(state='disabled')
            enddate_label.config(state='disabled')
            entry_starttime.config(state='disabled')
            entry_endtime.config(state='disabled')
    
        def tcStartEndDate():
            startdate_label.config(state='normal')
            enddate_label.config(state='normal')
            entry_starttime.config(state='normal')
            entry_endtime.config(state='normal')
                
        # Fixed, Cumulative Sky Yearly
        def tcOne():
            selfixed()
            tcAll()
            
        # Fixed, cUmulative Sky with STart/End times
        def tcTwo():
            selfixed()
            tcStartEndDate()
        
        # Fixed, Hourly by Tiestamps:
        def tcThree():
            selfixed()
            tcStartEndDate()
        
        # Fixed, Hourly for the whole Year:
        def tcFour():
            selfixed()
            tcAll()
            
        # Tracking, Cumulative sky Yearly
        def tcFive():
            selHSAT()
            tcAll()
            
        # Tracking, Hourly for a Day
        def tcSix():
            selHSAT()
            
        # Tracking, Hourly with STart/End Times
        def tcSeven():
            selHSAT()
            tcStartEndDate()
            
        def tcEight():
            selHSAT()
            tcAll()
        
        simulationcontrol_label = ttk.Label(simulationcontrol_frame, text='Simulation Control', font=("Arial Bold", 15))
        simulationcontrol_label.grid(row = 0, columnspan=2, sticky=W)
        rb_fixedortracking=IntVar()
        rad1_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50, text='Fixed, Cumulative Sky Yearly', value=0, command=tcOne)
        rad2_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Fixed, Cumulative Sky with Start/End times', value=1, command=tcTwo)
        rad3_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Fixed, Hourly with Start/End times', value=2, command=tcThree) #text='Fixed, Hourly by Timestamps'
        rad4_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Fixed, Hourly for the Whole Year', value=3, command=tcFour)
        rad5_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Tracking, Cumulative Sky Yearly', value=4, command=tcFive)
        rad7_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Tracking, Hourly with Start/End times', value=5, command=tcSeven)
        rad8_fixedortracking = Radiobutton(simulationcontrol_frame, variable=rb_fixedortracking, indicatoron = 0, width = 50,  text='Tracking, Hourly for the Whole Year', value=6, command=tcEight)
        rad1_fixedortracking.grid(column=0, row=1, columnspan=3)
        rad2_fixedortracking.grid(column=0, row=2, columnspan=3)
        rad3_fixedortracking.grid(column=0, row=3, columnspan=3)
        rad4_fixedortracking.grid(column=0, row=4, columnspan=3)
        rad5_fixedortracking.grid(column=0, row=5, columnspan=3)
        rad7_fixedortracking.grid(column=0, row=6, columnspan=3)
        rad8_fixedortracking.grid(column=0, row=7, columnspan=3)
    
        # Time CONTROL
        ###################
    
        startdate_label = ttk.Label(simulationcontrol_frame, state='disabled',  text='Start time ( mm_dd_HH or YYYY-mm-dd_HHMM ):')
        startdate_label.grid(row = 10, column=0,  sticky = W, columnspan=2)
        entry_starttime = Entry(simulationcontrol_frame, state='disabled', background="white")
        entry_starttime.grid(row=10, column=2,  sticky = W, columnspan=1)  
    
        enddate_label = ttk.Label(simulationcontrol_frame, state='disabled',   text='End time ( mm_dd_HH or mm_dd_HH_MM):')
        enddate_label.grid(row= 11, column=0,  sticky = W, columnspan=2)
        entry_endtime = Entry(simulationcontrol_frame, state='disabled', background="white")
        entry_endtime.grid(row=11, column=2,  sticky = W, columnspan=1)       

        # Tracking Parameters
        ###################
        
        def backtrackOn():
            rb_backtrack=0
            
        def backtrackOff():
            rb_backtrack=1
            
        trackingcontrol_label = ttk.Label(trackingparams_frame, text='Tracking Parameters', font=("Arial Bold", 15))
        trackingcontrol_label.grid(row = 0, columnspan=2, sticky=W)
        backtrack_label = ttk.Label(trackingparams_frame, state='disabled',  text='Backtrack:')
        backtrack_label.grid(row=1, column=0,  sticky = W)
        rb_backtrack=IntVar()
        rad1_backtrack = Radiobutton(trackingparams_frame, state='disabled', variable=rb_backtrack, text='True', value=0, command=backtrackOn)
        rad2_backtrack = Radiobutton(trackingparams_frame, state='disabled', variable=rb_backtrack, text='False', value=1, command=backtrackOff)
        rad1_backtrack.grid(column=1, row=1,  sticky = W)
        rad2_backtrack.grid(column=2, row=1,  sticky = W)
        limitangle_label = ttk.Label(trackingparams_frame, state='disabled',  text='Limit Angle (deg):')
        limitangle_label.grid(row=2, column=0, sticky = W)
        entry_limitangle = Entry(trackingparams_frame, state='disabled', background="white")
        entry_limitangle.grid(row=2, column=1, columnspan=2, sticky = W)
        angledelta_label = ttk.Label(trackingparams_frame, state='disabled',  text='Angle delta (deg):')
        angledelta_label.grid(row=4, column=0,  sticky = W)
        entry_angledelta = Entry(trackingparams_frame, state='disabled', background="white")
        entry_angledelta.grid(row=4, column=1, columnspan=2)
        
        axisofrotation_label = ttk.Label(trackingparams_frame, state='disabled', text='Axis of Rotation:')
        axisofrotation_label.grid(row=5, column=0, sticky = W)
        rb_axisofrotation=IntVar()
        rad1_axisofrotation = Radiobutton(trackingparams_frame, variable=rb_axisofrotation, state='disabled', text='Torque Tube', value=0)
        rad2_axisofrotation = Radiobutton(trackingparams_frame, width = 8, variable=rb_axisofrotation, state='disabled', text='Panels', value=1)
        rad1_axisofrotation.grid(row=5, column=1, sticky = W)
        rad2_axisofrotation.grid(row=5, column=2, sticky = W)
        
        
        # TorqueTube Parameters
        ###################
        
        def torquetubeTrue():
            tubeType_label.config(state='normal')
            rad1_tubeType.config(state='normal')
            rad2_tubeType.config(state='normal')
            rad3_tubeType.config(state='normal')
            rad4_tubeType.config(state='normal')
            torqueTubeMaterial_label.config(state='normal') 
            rad1_torqueTubeMaterial.config(state='normal')
            rad2_torqueTubeMaterial.config(state='normal')
            rad3_torqueTubeMaterial.config(state='normal')
            entry_diameter.config(state='normal')
    
        
        def torquetubeFalse():
            tubeType_label.config(state='disabled')
            rad1_tubeType.config(state='disabled')
            rad2_tubeType.config(state='disabled')
            rad3_tubeType.config(state='disabled')
            rad4_tubeType.config(state='disabled')
            torqueTubeMaterial_label.config(state='disabled')
            rad1_torqueTubeMaterial.config(state='disabled')
            rad2_torqueTubeMaterial.config(state='disabled')
            rad3_torqueTubeMaterial.config(state='disabled')
            entry_diameter.delete(0,END)
            entry_diameter.config(state='disabled')
        
        
        torquetubecontrol_label = ttk.Label(torquetubeparams_frame, text='TorqueTube Parameters', font=("Arial Bold", 15))
        torquetubecontrol_label.grid(row = 0, columnspan=3, sticky=W)
        torqueTube_label = ttk.Label(torquetubeparams_frame,   text='TorqueTube:')
        torqueTube_label.grid(row=1, column=0,  sticky = W)
        rb_torqueTube=IntVar()
        rad1_torqueTube = Radiobutton(torquetubeparams_frame, indicatoron = 0, width = 10,  variable=rb_torqueTube, text='True', value=0, command=torquetubeTrue)
        rad2_torqueTube = Radiobutton(torquetubeparams_frame, indicatoron = 0, width = 10,  variable=rb_torqueTube, text='False', value=1, command=torquetubeFalse)
        rad1_torqueTube.grid(column=1, row=1,  sticky = W)
        rad2_torqueTube.grid(column=2, row=1,  sticky = W)
        diameter_label = ttk.Label(torquetubeparams_frame,  text='Diameter:')
        diameter_label.grid(row=2, column=0, sticky = W)
        entry_diameter = Entry(torquetubeparams_frame,  width = 12,  background="white")
        entry_diameter.grid(row=2, column=1,  sticky = W)
        tubeType_label = ttk.Label(torquetubeparams_frame,  text='Tube type:')
        tubeType_label.grid(row=3, column=0,  sticky = W)
        rb_tubeType=IntVar()
        rad1_tubeType = Radiobutton(torquetubeparams_frame,  variable=rb_tubeType, text='Round', value=0)
        rad2_tubeType = Radiobutton(torquetubeparams_frame,   variable=rb_tubeType, text='Square', value=1)
        rad3_tubeType = Radiobutton(torquetubeparams_frame, width = 5,   variable=rb_tubeType, text='Hex', value=2)
        rad4_tubeType = Radiobutton(torquetubeparams_frame, width = 5,  variable=rb_tubeType, text='Oct', value=3)
        rad1_tubeType.grid(column=1, row=3,  sticky = W)
        rad2_tubeType.grid(column=2, row=3,  sticky = W)
        rad3_tubeType.grid(column=3, row=3,  sticky = W)    
        rad4_tubeType.grid(column=4, row=3,  sticky = W)
        rb_torqueTubeMaterial=IntVar()
        torqueTubeMaterial_label = ttk.Label(torquetubeparams_frame, text='TorqueTube Material:')
        torqueTubeMaterial_label.grid(column=0, row=4,  sticky = W)
        rad1_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,  variable=rb_torqueTubeMaterial, text='Metal_Grey', value=0)
        rad2_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,  variable=rb_torqueTubeMaterial, text='Black', value=1)
        rad3_torqueTubeMaterial = Radiobutton(torquetubeparams_frame,  variable=rb_torqueTubeMaterial, text='Invisible', value=2)
        rad1_torqueTubeMaterial.grid(column=1, row = 4, sticky = W)
        rad2_torqueTubeMaterial.grid(column=2, row = 4, sticky = W)
        rad3_torqueTubeMaterial.grid(column=3, row = 4, sticky = W)
    
        # MODULE PARAMETERS Parameters
        ###################
        
        def cellLevelModuleOn():        
            numcellsx_label.config(state='normal')
            entry_numcellsx.config(state='normal')
            numcellsy_label.config(state='normal')
            entry_numcellsy.config(state='normal')
            xcell_label.config(state='normal')
            entry_xcell.config(state='normal')
            ycell_label.config(state='normal')
            entry_ycell.config(state='normal')
            xcellgap_label.config(state='normal')
            entry_xcellgap.config(state='normal')
            ycellgap_label.config(state='normal') 
            entry_ycellgap.config(state='normal') 
            x_label.config(state='disabled')
            y_label.config(state='disabled')
            entry_x.config(state='disabled')
            entry_y.config(state='disabled')
            
        def cellLevelModuleOff():    
            numcellsx_label.config(state='disabled')
            entry_numcellsx.config(state='disabled') 
            numcellsy_label.config(state='disabled') 
            entry_numcellsy.config(state='disabled')
            xcell_label.config(state='disabled')
            entry_xcell.config(state='disabled')
            ycell_label.config(state='disabled')
            entry_ycell.config(state='disabled')
            xcellgap_label.config(state='disabled')
            entry_xcellgap.config(state='disabled')
            ycellgap_label.config(state='disabled')
            entry_ycellgap.config(state='disabled')
            x_label.config(state='normal')
            y_label.config(state='normal')
            entry_x.config(state='normal')
            entry_y.config(state='normal')
            
        def getModuleJSONlist():
            """ populate entry_modulename with module names from module.json
            """
            import json
            jsonfile = os.path.join(DATA_PATH,'module.json')
            with open(jsonfile) as configfile:
                jsondata = json.load(configfile)
            
            systemtuple = ('',) 
            for key in jsondata.keys():
                systemtuple = systemtuple + (str(key),)   #build the tuple of strings
            entry_modulename['values'] = systemtuple[1:]
            entry_modulename.current(0)
            self.jsondata = jsondata
            
        def showModule(noprint=False):
            """ run objview to show view of a module
                create a temp module based on GUI parameters
                input: noprint (boolean) suppress module printing
            """
            #simulationParamsDict, sceneParamsDict, timeControlParamsDict, \
            #moduleParamsDict, trackingParamsDict, torquetubeParamsDict, \
            #analysisParamsDict, cellModuleDict,_ 
            P = read_valuesfromGUI()
            #simDict = P[0]; modDict = P[3]; tubeDict = P[5]
            if P[3] is None:
                print('Empty module dictionary - returning')
                return

            moduletype = 'test-module'
            print('Creating test module')
            
            # need to first create a dummy SceneObj to create the module .rad
            # file in TEMP_PATH
            demo = bifacial_radiance.RadianceObj(path = TEMP_PATH)
            
            # create the kwargs for makeModule
            cellModuleParams = (P[7] if P[0]['cellLevelModule'] else None)
            kwargs = {'name':moduletype, 'numpanels':P[3]['numpanels'], 
                      'x':P[3]['x'],'y':P[3]['y'], 'xgap':P[3]['xgap'],
                       'ygap':P[3]['ygap'],'zgap':P[3]['zgap']}

            # Run makeModule with the above kwarg dictionary
            module = demo.makeModule(**kwargs)
            if cellModuleParams: module.addCellModule(**cellModuleParams)
            if P[5]: 
                print(f'P5: {P[5]}')
                module.addTorquetube(**P[5])

            if noprint is False:
                # show module
                module.showModule()
            
            return demo

           
        def showScene():
            """ run objview to show view of a scene
                create a temp scene based on GUI parameters
            """
            
            # first create the module given the current conditions of the GUI 
            demo = showModule(noprint = True)
            moduletype = demo.module.name

            # read in the GUI values
            #simulationParamsDict, sceneParamsDict, timeControlParamsDict, \
            #moduleParamsDict, trackingParamsDict, torquetubeParamsDict, \
            #analysisParamsDict, cellModuleDict,_ 
            P = read_valuesfromGUI()

            # Case: tracking scenario
            if P[0]['tracking'] is True:
                print('Rendering tracker scene at 0 (noon) tilt')
                # assume  0 tilt
                key = '01_01_12'
                trackerdict = {key: {'surf_azm':P[1]['axis_azimuth']+90,
                            'surf_tilt': 0.0, 'theta':0, 'ghi':999} }

                trackerdict = demo.makeScene1axis(trackerdict, 
                                             sceneDict = P[1], 
                                             cumulativesky=False, 
                                             module=moduletype)
                scene = trackerdict[key]['scene']
            else: # fixed tilt scenario
                scene = demo.makeScene(module=moduletype, sceneDict=P[1])
            
            scene.showScene()
        
        def modulenamecallbackFunc(event):
            """ load specific module data from module.json after new module selected
            """
            
            def enable_torquetube(d):
                """ torque tube details are enabled
                """
                rad1_torqueTube.invoke() # torquetube True button
                entry_diameter.delete(0,END) # torque tube diameter
                entry_diameter.insert(0,str(d['torquetube']['diameter']))
                #tubetype. 'round', square, hex, oct
                tubeoptions= {'round':rad1_tubeType.invoke,
                              'square':rad2_tubeType.invoke,
                              'hex':rad3_tubeType.invoke,
                              'oct':rad4_tubeType.invoke}
                tubeoptions.get(d['torquetube']['tubetype'].lower())
                
                #material. 'Metal_Grey' or 'Black'
                if d['torquetube']['visible'] is False:
                    rad3_torqueTubeMaterial.invoke()
                elif d['torquetube']['material'].lower() == 'black':
                    rad2_torqueTubeMaterial.invoke()
                else:
                    rad1_torqueTubeMaterial.invoke()
                             
            def disable_torquetube(d):
                """ torque tube details are disabled
                """
                rad2_torqueTube.invoke() # torquetube False button
                entry_diameter.delete(0,END)
                #if 'torquetube' in d:
                    #entry_diameter.insert(0,str(d['torquetube']['diameter']))

            def enable_cellModule(d):
                """cellModule parameters passed
                """
                rad2_cellLevelModule.invoke()
                # clear cellLevelModule entries loaded from json
                entry_numcellsx.delete(0,END)
                entry_numcellsy.delete(0,END)
                entry_xcell.delete(0,END)
                entry_ycell.delete(0,END)
                entry_xcellgap.delete(0,END)
                entry_ycellgap.delete(0,END)

               # set module entries loaded from json
                entry_numcellsx.insert(0,str(d['cellModule']['numcellsx']))
                entry_numcellsy.insert(0,str(d['cellModule']['numcellsy']))
                entry_xcell.insert(0,str(d['cellModule']['xcell']))
                entry_ycell.insert(0,str(d['cellModule']['ycell']))
                entry_xcellgap.insert(0,str(d['cellModule']['xcellgap']))
                entry_ycellgap.insert(0,str(d['cellModule']['ycellgap']))
                
            

            key = entry_modulename_value.get() # what is the value selected?
            #print(key + ' selected')
            if key != '':  # '' not a dict key
                #print(self.jsondata[key])
                d = self.jsondata[key]
                self.moduletype = key
                # set radio buttons
                rad1_cellLevelModule.invoke()  # non cell-level modules by default
                rad2_rewriteModule.invoke()               
                
                # clear module entries loaded from json
                entry_moduletype.delete(0,END)
                entry_numberofPanels.delete(0,END)
                entry_x.delete(0,END)
                entry_y.delete(0,END)
                entry_bifi.delete(0,END)
                entry_xgap.delete(0,END)
                entry_ygap.delete(0,END)
                entry_zgap.delete(0,END)
 
               # set module entries loaded from json
                entry_moduletype.insert(0,key)
                entry_numberofPanels.insert(0,str(d['numpanels']))
                entry_x.insert(0,str(d['x']))
                entry_y.insert(0,str(d['y']))
                entry_bifi.insert(0,str(d['bifi']))
                entry_xgap.insert(0,str(d['xgap']))
                entry_ygap.insert(0,str(d['ygap']))
                entry_zgap.insert(0,str(d['zgap']))              
                
                # Torque tube details from json
                tubebool = d.get('torquetube')
                if tubebool:
                    enable_torquetube(d)
                else:
                    disable_torquetube(d)
                # cellModule details from json
                cellbool = d.get('cellModule')
                if cellbool:
                    enable_cellModule(d)
            
        moduleparams_label = ttk.Label(moduleparams_frame, text='Module Parameters', font=("Arial Bold", 15))
        moduleparams_label.grid(row = 0, columnspan=3, sticky=W)
        
        entry_modulename_value = tk.StringVar()        
        entry_modulename = ttk.Combobox(moduleparams_frame, textvariable=entry_modulename_value)
        entry_modulename.grid(row=0, column=2, sticky = W, columnspan=2)
        getModuleJSONlist()  #set the module name values
        entry_modulename.bind("<<ComboboxSelected>>", modulenamecallbackFunc)
        
        numberofPanels_label = ttk.Label(moduleparams_frame, text='Number of Panels')
        numberofPanels_label.grid(row=1, column=0, sticky = W)
        entry_numberofPanels = Entry(moduleparams_frame, width = 4)
        entry_numberofPanels.grid(row=1, column=1, sticky = W)
        cellLevelModule_label = ttk.Label(moduleparams_frame, text='Cell Level Module')
        cellLevelModule_label.grid(row=2, column=0, sticky = W)
        rb_cellLevelModule=IntVar()
        rad1_cellLevelModule = Radiobutton(moduleparams_frame, indicatoron = 0, width = 8, variable=rb_cellLevelModule, text='False', value=0, command=cellLevelModuleOff)
        rad2_cellLevelModule = Radiobutton(moduleparams_frame, indicatoron = 0, width = 8, variable=rb_cellLevelModule, text='True', value=1, command=cellLevelModuleOn)
        rad1_cellLevelModule.grid(column=1, row=2,  sticky = W)
        rad2_cellLevelModule.grid(column=2, row=2,  sticky = W)  
        
        numcellsx_label = ttk.Label(moduleparams_frame, state='disabled', text='numcells x:')
        numcellsx_label.grid(row=3, column=0, sticky = W)
        entry_numcellsx = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_numcellsx.grid(row=3, column=1, sticky = W)
        numcellsy_label = ttk.Label(moduleparams_frame, state='disabled', text='numcells y:')
        numcellsy_label.grid(row=3, column=2, sticky = W)
        entry_numcellsy = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_numcellsy.grid(row=3, column=3, sticky = W)
        
        xcell_label = ttk.Label(moduleparams_frame, state='disabled', text='Size Xcell:')
        xcell_label.grid(row=4, column=0, sticky = W)
        entry_xcell = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_xcell.grid(row=4, column=1, sticky = W)
        ycell_label = ttk.Label(moduleparams_frame, state='disabled', text='Size Ycell:')
        ycell_label.grid(row=4, column=2, sticky = W)
        entry_ycell = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_ycell.grid(row=4, column=3, sticky = W)
    
        xcellgap_label = ttk.Label(moduleparams_frame, state='disabled', text='Xcell gap:')
        xcellgap_label.grid(row=5, column=0, sticky = W)
        entry_xcellgap = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_xcellgap.grid(row=5, column=1, sticky = W)
        ycellgap_label = ttk.Label(moduleparams_frame, state='disabled', text='Ycell gap:')
        ycellgap_label.grid(row=5, column=2, sticky = W)
        entry_ycellgap = Entry(moduleparams_frame, state='disabled', width = 6)
        entry_ycellgap.grid(row=5, column=3, sticky = W)
            
        x_label = ttk.Label(moduleparams_frame,  text='Module size   x:')
        x_label.grid(row=6, column=0, sticky = W)
        entry_x = Entry(moduleparams_frame, width = 6)
        entry_x.grid(row=6, column=1, sticky = W)
        y_label = ttk.Label(moduleparams_frame, width = 4, text='y:')
        y_label.grid(row=6, column=2, sticky = W)
        entry_y = Entry(moduleparams_frame, width = 6)
        entry_y.grid(row=6, column=3, sticky = W)
        xgap_label = ttk.Label(moduleparams_frame,  text='Xgap | Ygap | Zgap :')
        xgap_label.grid(row=7, column=0, sticky = W)
        entry_xgap = Entry(moduleparams_frame, width = 6)
        entry_xgap.grid(row=7, column=1, sticky = W)
        entry_ygap = Entry(moduleparams_frame, width = 6)
        entry_ygap.grid(row=7, column=2, sticky = W)
        entry_zgap = Entry(moduleparams_frame, width = 6)
        entry_zgap.grid(row=7, column=3, sticky = W)
        bifi_label = ttk.Label(moduleparams_frame,  text='Bifacial Factor (i.e. 0.9):')
        bifi_label.grid(row=8, column=0, sticky = W)
        entry_bifi = Entry(moduleparams_frame, width = 6)
        entry_bifi.grid(row=8, column=1, sticky = W)
        
        showModule_button = Button(moduleparams_frame, width = 10, text="VIEW", command=showModule)
        showModule_button.grid(column=2, row=8, columnspan=1) 

        moduletype_label = ttk.Label(moduleparams_frame, background='lavender', text='Module Name:')
        moduletype_label.grid(row = 9, sticky=W)
        entry_moduletype = Entry(moduleparams_frame, background="white")
        entry_moduletype.grid(row=9, column=1, columnspan=2)
        rewriteModule_label = ttk.Label(moduleparams_frame, background='lavender', text='Rewrite Module:')
        rewriteModule_label.grid(row = 10, sticky=W)
        rb_rewriteModule=IntVar()
        rad1_rewriteModule = Radiobutton(moduleparams_frame,background='lavender', variable=rb_rewriteModule, text='True', value=0)
        rad2_rewriteModule = Radiobutton(moduleparams_frame,background='lavender', variable=rb_rewriteModule, text='False', value=1)
        rad1_rewriteModule.grid(column=1, row=10)
        rad2_rewriteModule.grid(column=2, row=10)



    
        # SCENE PARAMETERS 
        ###################
        def definebyGCR():        
            gcr_label.config(state='normal')
            entry_gcr.config(state='normal')
            pitch_label.config(state='disabled')
            entry_pitch.config(state='disabled')
        
        def definebyPitch():
            gcr_label.config(state='disabled')
            entry_gcr.config(state='disabled')
            pitch_label.config(state='normal')
            entry_pitch.config(state='normal')
            
        def clearAllValuesButton():
            activateAllEntries()
            clearAllValues()
            setdefaultActive()
            setdefaultGray()

            
        sceneparams_label = ttk.Label(sceneparams_frame, text='Scene Parameters', font=("Arial Bold", 15))
        sceneparams_label.grid(row = 0, columnspan=3, sticky=W)
        GCRorPitch_label = ttk.Label(sceneparams_frame, text='Row spacing by:')
        GCRorPitch_label.grid(row=1, column=0, sticky = W)
        rb_GCRorPitch=IntVar()
        rad1_GCRorPitch = Radiobutton(sceneparams_frame, width = 8, variable=rb_GCRorPitch, text='GCR', value=0, command=definebyGCR)
        rad2_GCRorPitch = Radiobutton(sceneparams_frame, width = 8, variable=rb_GCRorPitch, text='Pitch', value=1, command=definebyPitch)
        rad1_GCRorPitch.grid(column=1, row=1,  sticky = W)
        rad2_GCRorPitch.grid(column=2, row=1,  sticky = W)  
        gcr_label  = ttk.Label(sceneparams_frame, text='GCR:')
        gcr_label.grid(row=2, column=0, sticky = W)
        entry_gcr = Entry(sceneparams_frame, width = 6)
        entry_gcr.grid(row=2, column=1, sticky = W)
        pitch_label = ttk.Label(sceneparams_frame, state='disabled', text='Pitch:')
        pitch_label.grid(row=2, column=2, sticky = W)
        entry_pitch = Entry(sceneparams_frame, state='disabled', width = 6)
        entry_pitch.grid(row=2, column=3, sticky = W)
        albedo_label  = ttk.Label(sceneparams_frame, text='Albedo:')
        albedo_label.grid(row=3, column=0, sticky = W)
        entry_albedo = Entry(sceneparams_frame, width = 6)
        entry_albedo.grid(row=3, column=1, sticky = W)
        nMods_label  = ttk.Label(sceneparams_frame, text='# Mods:')
        nMods_label.grid(row=4, column=0, sticky = W)
        entry_nMods = Entry(sceneparams_frame, width = 6)
        entry_nMods.grid(row=4, column=1, sticky = W)
        nRows_label = ttk.Label(sceneparams_frame, text='# Rows:')
        nRows_label.grid(row=4, column=2, sticky = W)
        entry_nRows = Entry(sceneparams_frame, width = 6)
        entry_nRows.grid(row=4, column=3, sticky = W)   
        
        azimuth_label  = ttk.Label(sceneparams_frame, text='Azimuth Angle (i.e. 180 for South):')
        azimuth_label.grid(row=5, column=0, sticky = W, columnspan=2)
        entry_azimuth = Entry(sceneparams_frame, width = 6)
        entry_azimuth.grid(row=5, column=2, sticky = W)
        
        clearanceheight_label  = ttk.Label(sceneparams_frame, text='Clearance height: ')
        clearanceheight_label.grid(row=6, column=0, sticky = W, columnspan=2)
        entry_clearanceheight = Entry(sceneparams_frame, width = 6)
        entry_clearanceheight.grid(row=6, column=1, sticky = W)
    
        tilt_label  = ttk.Label(sceneparams_frame, text='Tilt: ')
        tilt_label.grid(row=6, column=2, sticky = W, columnspan=2)
        entry_tilt = Entry(sceneparams_frame, width = 6)
        entry_tilt.grid(row=6, column=3, sticky = W)
        
        axis_azimuth_label = ttk.Label(sceneparams_frame, state='disabled', text='Axis Azimuth (i.e. 180 for EW HSATtrackers):')
        axis_azimuth_label.grid(row=7, column=0, sticky = W, columnspan=3)
        entry_axis_azimuth = Entry(sceneparams_frame,  state='disabled',  width = 6)
        entry_axis_azimuth.grid(row=7, column=3, sticky = W)
        
        hubheight_label  = ttk.Label(sceneparams_frame,  state='disabled', text='Hub height: ')
        hubheight_label.grid(row=8, column=0, sticky = W, columnspan=2)
        entry_hubheight = Entry(sceneparams_frame,  state='disabled', width = 6)
        entry_hubheight.grid(row=8, column=1, sticky = W)
        
        showScene_button = Button(sceneparams_frame, width = 10, text="VIEW", command=showScene)
        showScene_button.grid(column=2, row=8, columnspan=1) 
    
    
        # Analysis PARAMETERS 
        ###################
        analysisparams_label = ttk.Label(analysisparams_frame, text='Analysis Parameters', font=("Arial Bold", 15))
        analysisparams_label.grid(row = 0, columnspan=3, sticky=W)
        sensorsy_label  = ttk.Label(analysisparams_frame, text='# Sensors: ')
        sensorsy_label.grid(row=1, column=0, sticky = W)
        entry_sensorsy = Entry(analysisparams_frame, width = 6)
        entry_sensorsy.grid(row=1, column=1, sticky = W)
        modWanted_label  = ttk.Label(analysisparams_frame, text='Mod Wanted: ')
        modWanted_label.grid(row=2, column=0, sticky = W)
        entry_modWanted = Entry(analysisparams_frame, width = 6)
        entry_modWanted.grid(row=2, column=1, sticky = W)
        rowWanted_label  = ttk.Label(analysisparams_frame, text='Row Wanted: ')
        rowWanted_label.grid(row=2, column=2, sticky = W)
        entry_rowWanted = Entry(analysisparams_frame, width = 6)
        entry_rowWanted.grid(row=2, column=3, sticky = W)
        emptyspace = ttk.Label(analysisparams_frame, text='', font=("Arial Bold", 5))
        emptyspace.grid(row = 3, columnspan=3, sticky=W)
        Clear_button = Button(analysisparams_frame, text="CLEAR", command=clearAllValuesButton)
        Clear_button.grid(column=0, row=4)
        DEFAULT_button = Button(analysisparams_frame,text="DEFAULT", command=setDefaults)
        DEFAULT_button.grid(column=1, row=4)
        RUN_button = Button(analysisparams_frame, width = 25, text="RUN", command=runBifacialRadiance)
        RUN_button.grid(column=2, row=4, columnspan=3) 
        
        ## IMAGE STUFF
        #imagevariables_frame
        image_fixed = PhotoImage(file=os.path.join(IMAGE_PATH,'fig1_fixed_small.gif'))
        image_tracked = PhotoImage(file=os.path.join(IMAGE_PATH,'fig2_tracked_small.gif'))
        buttonImage = Button(imagevariables_frame, image=image_fixed)
        buttonImage.grid(row=0, columnspan=4, sticky=W)
            
        setDefaults()
        setdefaultGray()
        entry_modulename.event_generate('<<ComboboxSelected>>') # populate module params
        

    #    root.title("Bifacial_Radiance | v. 0_2_5")

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def gui():
    """
    Graphical user interface- just type bifacial_radiance.gui() to get started! 

    Returns
    -------
    None.

    """    
    root = Window()
    # bring window into focus
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    # run mainloop
    root.mainloop()
    print("\nNow leaving GUI")
    # Hold off on returning values for now until we can clean them first
    #print('Annual bifacial ratio average:  %0.3f' %(
    #    sum(root.data.Wm2Back) / sum(root.data.Wm2Front) ) )  
    #return root.data

# If the script is run as a file, it needs to call gui().    
if __name__ == '__main__':
    gui()  
