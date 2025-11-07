# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for bifacial_radiance.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance


"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance
import numpy as np
import pytest
import os
import datetime
import pandas as pd

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder

# test the readepw on a dummy Boulder EPW file in the /tests/ directory
MET_FILENAME =  'USA_CO_Boulder.724699_TMY2.epw'
# also test a dummy TMY3 Denver file in /tests/
MET_FILENAME2 = "724666TYA.CSV"
# custom 2-year 15 minute datafile with leab year
MET_FILENAME3= "Custom_WeatherFile_2years_15mins_BESTFieldData.csv"
# SolarGIS 1.5-year hourly datafile with leap year
MET_FILENAME4="SOLARGIS_Almeria_Spain_20210331.csv"
# custom 1 year TMY3 datafile with an added "Tracker Angle (degrees)" column 
MET_FILENAME5="Custom_WeatherFile_TMY3format_60mins_2021_wTrackerAngles_BESTFieldData.csv"
# PSM3 (SAM hourly) formatted weather file for Phoenix, AZ
MET_FILENAME6="phoenix_az_psmv3_60_tmy.csv"


#def test_quickExample():
#    results = bifacial_radiance.main.quickExample(TESTDIR)
#    assert np.mean(results.Wm2Back) == pytest.approx(195380.94444444444, rel = 0.03)  # was 182 in v0.2.2

def test_RadianceObj_set1axis():  
    # test set1axis.  requires metdata for boulder. 
    #name = "_test_set1axis"
    name = None
    demo = bifacial_radiance.RadianceObj(name)
    assert len(str(demo)) > 300 # Make sure something is printed out here for demo.__repr__

    assert len(demo.columns) >= 15
    assert len(demo.methods) >= 30
    #try:
    #    epwfile = demo.getEPW(lat=40.01667, lon=-105.25)  # From EPW: {N 40°  1'} {W 105° 15'}
    #except: # adding an except in case the internet connection in the lab forbids the epw donwload.
    epwfile = MET_FILENAME
    metdata = demo.readWeatherFile(weatherFile=epwfile, coerce_year=2001)
    trackerdict = demo.set1axis()
    assert trackerdict[0]['count'] == 78 #80
    assert trackerdict[45]['count'] == 822 #
    assert len(demo.name) == 17

   
def test_RadianceObj_fixed_tilt_end_to_end():
    # just run the demo example.  Rear irradiance fraction roughly 11.8% for 0.95m landscape panel
    # takes 12 seconds
    
    analysis = bifacial_radiance.main.quickExample(testfolder=TESTDIR)
    """
    name = "_test_fixed_tilt_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(0.62) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
  
    metdata = demo.readWeatherFile(weatherFile= MET_FILENAME, coerce_year=2001) # read in the EPW weather data from above
    timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
    demo.gendaylit(timeindex=timeindex, metdata=metdata)  # Noon, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2, 'nMods':10, 'nRows':3}  
    module = demo.makeModule(name='test-module',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene(module, sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance 
    """
    #assert np.round(np.mean(analysis.backRatio),decimals=2) == 0.12  # NOTE: this value is 0.11 when your module size is 1m, 0.12 when module size is 0.95m
    assert np.mean(analysis.backRatio) == pytest.approx(0.115, abs = 0.01)
    
def test_Radiance_high_azimuth_modelchains():
    # duplicate next example using modelchain
    # high azimuth .ini file, includes CEC performance
    import time
    
    HIGH_AZIMUTH_INI = os.path.join(TESTDIR, "ini_highAzimuth.ini")
    

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=HIGH_AZIMUTH_INI)
    Params[0]['testfolder'] = TESTDIR
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 
    results = demo2.results
    #assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    assert np.mean(results.Wm2Front[0]) == pytest.approx(899, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(results.Wm2Back[0]) == pytest.approx(189, rel = 0.03)  # was 182 in v0.2.2
    assert results.Pout[0] == demo2.compiledResults.Pout[0] == pytest.approx(369, abs= 1)
    assert results.Mismatch[0] == pytest.approx(2.82, abs = .1)

    # assert that .hdr image files were created in the last 5 minutes
    mtime_module = os.path.getmtime(os.path.join('images','test-module_XYZ.hdr'))
    mtime_scene = os.path.getmtime(os.path.join('images','scene_2021-06-17_1300_side.hdr'))
    assert  time.time() - mtime_module < 300
    assert  time.time() - mtime_scene < 300
    
"""
def test_RadianceObj_high_azimuth_angle_end_to_end():
    # modify example for high azimuth angle to test different parts of _makeSceneNxR.  Rear irradiance fraction roughly 17.3% for 0.95m landscape panel
    # takes 14 seconds for sensorsy = 9, 11 seconds for sensorsy = 2
    name = "_test_high_azimuth_angle_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround('white_EPDM') # input albedo number or material name like 'concrete'.  To see options, run this without any input.
  
    metdata = demo.readWeatherFile(MET_FILENAME2, coerce_year=2001) # select a TMY file using graphical picker
    # Now we either choose a single time point, or use cumulativesky for the entire year. 
    fullYear = False
    if fullYear:
        demo.genCumSky(demo.epwfile) # entire year.  # Don't know how to test this yet in pytest...
    else:
        timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
        demo.gendaylit(metdata=metdata,timeindex=timeindex)  # Noon, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'height':0.2,'azimuth':30, 'nMods':10, 'nRows':3}  
    module = demo.makeModule(name='test-module',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test-module',sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance      
    #assert np.round(np.mean(analysis.backRatio),2) == 0.20  # bifi ratio was == 0.22 in v0.2.2
    assert np.mean(analysis.Wm2Front) == pytest.approx(899, rel = 0.005)  # was 912 in v0.2.3
    assert np.mean(analysis.Wm2Back) == pytest.approx(189, rel = 0.02)  # was 182 in v0.2.2
"""

def test_Radiance_1axis_gendaylit_modelchains():
    # duplicate next sample using modelchain
    # 1-axis .ini file
    filename = "ini_1axis.ini"

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=filename)
    Params[0]['testfolder'] = TESTDIR
    Params[6]['modWanted'] = [6,7]
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params) 
    #V 0.2.5 fixed the gcr passed to set1axis. (since gcr was not being passd to set1axis, gcr was default 0.33 default). 
    assert(demo2.compiledResults.Gfront_mean[0] == pytest.approx(205.0, 0.01) ) # was 214 in v0.2.3  # was 205 in early v0.2.4  
    assert(demo2.compiledResults.Grear_mean[0] == pytest.approx(43.0, 0.1) )
    assert(demo2.compiledResults.x.mean() == pytest.approx(np.array([-10.65, -11.59]), 0.005) )
    assert(demo2.compiledResults.y.mean() == pytest.approx(np.array([1.491, 1.491]), 0.005) )
    # test that trackerdict['scene'] is deprecated
    with pytest.warns(DeprecationWarning):
        assert demo2.trackerdict['2001-01-01_1100']['scene'][0].text.__len__() == 134
    assert demo2.trackerdict['2001-01-01_1100']['scenes'][0].text[23:28] == " 2.0 "
    demo2.exportTrackerDict(savefile = 'results/exportedTrackerDict.csv', reindex=True)
    # Run groundscan
    tracker_ground = demo2.analysis1axisground()
    results_ground = tracker_ground['2001-01-01_1100']['AnalysisObj'][2]
    assert results_ground.sensorsground == 56
    assert results_ground.mattype[0] == 'groundplane'


"""    
def test_RadianceObj_1axis_gendaylit_end_to_end():
    name = "_test_1axis_gendaylit_end_to_end"
    # 1-axis tracking end-to-end test with torque tube and gap generation.  
    # Takes 20 seconds for 2-sensor scan
    gcr = 0.35   # ground cover ratio,  = module_height / pitch
    albedo = 0.3     # ground albedo
    hub_height = 2   # tracker height at 0 tilt in meters (hub height)
    
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    metdata = demo.readWeatherFile(MET_FILENAME, starttime='2001-01-01_0100', endtime = '2001-01-01_2300', coerce_year = 2001) # read in the weather data from above
    #metdata = demo.readEPW(MET_FILENAME, starttime='01_01_01', endtime = '01_01_23') # read in the EPW weather data from above
    # set module type to be used and passed into makeScene1axis
    # test modules with gap and rear tube
    module=demo.makeModule(name='test-module',x=0.984,y=1.95,torquetube = True, numpanels = 2, ygap = 0.1)
    sceneDict = {'pitch': np.round(module.sceney / gcr,3),'height':hub_height, 'nMods':10, 'nRows':3}  
    key = '2001-01-01_1100'
    # create metdata files for each condition. keys are timestamps for gendaylit workflow
    trackerdict = demo.set1axis(cumulativesky=False, gcr=gcr)
    # create the skyfiles needed for 1-axis tracking
    demo.gendaylit1axis(metdata=metdata)
    # Create the scene for the 1-axis tracking
    demo.makeScene1axis({key:trackerdict[key]}, module='test-module', sceneDict=sceneDict, cumulativesky = False)
    #demo.makeScene1axis({key:trackerdict[key]}, module_type,sceneDict, cumulativesky = False, nMods = 10, nRows = 3, modwanted = 7, rowwanted = 3, sensorsy = 2) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    
    demo.makeOct1axis(trackerdict,key) # just run this for one timestep: Jan 1 11am
    trackerdict = demo.analysis1axis(trackerdict, singleindex=key, modWanted=[6,7], rowWanted=3, sensorsy=2) # just run this for one timestep: Jan 1 11am
    trackerdict = demo.calculateResults()
    demo.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)
    #V 0.2.5 fixed the gcr passed to set1axis. (since gcr was not being passd to set1axis, gcr was default 0.33 default). 
    assert(demo.compiledResults.Gfront_mean[0] == pytest.approx(205.0, 0.01) ) # was 214 in v0.2.3  # was 205 in early v0.2.4  
    assert(demo.compiledResults.Grear_mean[0] == pytest.approx(43.0, 0.1) )
    assert demo.trackerdict['2001-01-01_1100']['scene'].text.__len__() == 132
    assert demo.trackerdict['2001-01-01_1100']['scene'].text[23:28] == " 2.0 "
    demo.exportTrackerDict(savefile = 'results/exportedTrackerDict.csv', reindex=True)
    assert demo.trackerdict['2001-01-01_1100']['scene'].text.__len__() == 132
    assert demo.trackerdict['2001-01-01_1100']['scene'].text[23:28] == " 2.0 "
    demo.exportTrackerDict(savefile = 'results/exportedTrackerDict.csv', reindex=True)
"""

def test_1axis_gencumSky():
    name = "test_1axis_gencumSky"
    # Takes 20 seconds for 2-sensor scan
    gcr = 0.35   # ground cover ratio,  = module_height / pitch
    albedo = 0.3     # ground albedo
    hub_height = 2   # tracker height at 0 tilt in meters (hub height)
    
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(albedo) # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    assert demo.ground.methods == ['printGroundMaterials']
    metdata = demo.readWeatherFile(weatherFile=MET_FILENAME, starttime='01_01_01', endtime = '02_01_23', coerce_year=2001) # read in the EPW weather data from above
    moduleText = '! genbox black test-module 0.98 1.95 0.02 | xform -t -0.49 -2.0 0 -a 2 -t 0 2.05 0'
    module=demo.makeModule(name='test-module',x=0.984,y=1.95, numpanels = 2, ygap = 0.1, text=moduleText)
    assert module.text == moduleText
    pitch= np.round(module.sceney / gcr,3)
    trackerdict = demo.set1axis(cumulativesky = True, gcr=gcr)
    demo.genCumSky1axis()
    assert trackerdict[-45.0]['skyfile'][0:5] == 'skies' #  # Having trouble with the \ or //    'skies\\1axis_-45.0.rad'
    tempcsv = pd.read_csv(trackerdict[-45.0]['csvfile'], header=None, delimiter=' ')
    assert tempcsv.iloc[10,0] == 185
    assert tempcsv.__len__() == 8760
    sceneDict = {'gcr': gcr,'hub_height':hub_height, 'clearance_height':hub_height, 'nMods':10, 'nRows':3}  
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, module = 'test-module')
    # Removing all of this other tests for hub_height and height since it's ben identified that
    # a new module to handle hub_height and height in sceneDict needs to be implemented
    # instead of checking inside of makeScene, makeSceneNxR, and makeScene1axis
    assert trackerdict[-5.0]['scenes'][0].radfiles[0:7] == 'objects' # 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    assert trackerdict[-5.0]['scenes'][0].sceneDict['tilt'] == 5

    sceneDict = {'pitch': pitch,'clearance_height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, module = 'test-module', append=False)
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, module = 'test-module', append=True)
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'clearance_height':hub_height, 'nMods':10, 'nRows':3}  # testing height filter too
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, module = 'test-module', append=True)
#    assert trackerdict[-5.0]['radfile'] == 'objects\\1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    sceneDict = {'pitch': pitch,'height':hub_height, 'hub_height':hub_height, 'nMods':10, 'nRows':3, 'originy':1}  # testing height filter too
    customObject = demo.makeCustomObject('whiteblock','! genbox white_EPDM whiteblock 1.6 4.5 0.5 | xform -t -0.8 -2.25 0')
    trackerdict = demo.makeScene1axis(sceneDict=sceneDict, module = 'test-module', customtext=' -rz 90 '+customObject, append=True)#
    assert trackerdict[-5.0]['scenes'].__len__() == 4
    fname = trackerdict[-5.0]['scenes'][3].radfiles
    with open(fname, 'r') as f:
        assert f.readline().__len__() == 133 
        assert f.readline()[-14:] == 'whiteblock.rad'
    
    assert trackerdict[-5.0]['scenes'][3].radfiles[0:7] == 'objects'
    assert trackerdict[-5.0]['scenes'][3].sceneDict['tilt'] == 5
    assert trackerdict[-5]['scenes'][3].sceneDict['originy'] == 1
    #assert trackerdict[-5.0]['radfile'] == 'objects/1axis-5.0_1.825_11.42_5.0_10x3_origin0,0.rad'
    minitrackerdict = {}
    minitrackerdict[list(trackerdict)[0]] = trackerdict[list(trackerdict.keys())[0]]
    minitrackerdict[list(trackerdict)[0]]['scenes'] = [trackerdict[list(trackerdict)[0]]['scenes'][3]]

    trackerdict = demo.makeOct1axis(trackerdict=minitrackerdict, singleindex=-5) # just run this for one timestep: -5 degrees
    trackerdict = demo.analysis1axis( modWanted=7, rowWanted=3, sensorsy=2, sceneNum=0) 
    assert trackerdict[-5.0]['AnalysisObj'][0].x[0] == pytest.approx(-10.766, abs=.001)
    modscanfront = {}
    modscanfront = {'xstart': -5}
    trackerdict = demo.analysis1axis( sensorsy=2, modscanfront=modscanfront, sceneNum=0, customname='_test2') 
    assert trackerdict[-5.0]['AnalysisObj'][1].x[0] == -5
    trackerdict = demo.analysis1axisground(sensorsground=10,modWanted=1, rowWanted=1)
    
    demo.exportTrackerDict(trackerdict, savefile = 'results/exportedTrackerDict2.csv')
    
    CECMod = pd.read_csv(os.path.join(TESTDIR, 'Canadian_Solar_Inc__CS5P_220M.csv'),
                         index_col=0).iloc[:,0]
    module.addCEC(CECMod)
    results = demo.calculatePerformance1axis(module=module)
    results = demo.calculatePerformance1axis(module=module) #make sure running this twice doesn't error..
    pd.testing.assert_frame_equal(results, demo.compiledResults)
    assert results[results.modNum==7].Grear_mean.iloc[0] == pytest.approx(210, abs=30) #gencumsky has lots of variability
    assert len(results) == 3
    assert results[results.modNum==5].iloc[0].Grear_mean == pytest.approx(np.mean(results[results.modNum==5].iloc[0].Wm2Back), abs=0.1)
    assert len(results[results.modNum==1]['Wm2Front'][0]) == 10
    assert np.isnan((results[results.modNum==1]['Wm2Back'][0])).all() 

def test_SceneObj_makeSceneNxR_lowtilt():
    # test _makeSceneNxR(tilt, height, pitch, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 10 degree tilt, 0.2 height, 1.5 row spacing, landscape
    name = "_test_makeSceneNxR_lowtilt"
    demo = bifacial_radiance.RadianceObj(name) 
    demo.makeModule(name='test-module',y=0.95,x=1.59)
    #scene = bifacial_radiance.SceneObj(moduletype = name)
    #scene._makeSceneNxR(tilt=10,height=0.2,pitch=1.5)
    sceneDict={'tilt':10, 'clearance_height':0.2, 'pitch':1.5}
    scene = demo.makeScene(module='test-module', sceneDict=sceneDict)
    analysis = bifacial_radiance.AnalysisObj()
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    
    assert frontscan.pop('orient') == '-0.000 0.174 -0.985'# was 0,0,-11 in v0.2.4
    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1,  'xinc': 0,  'yinc': 0.09357,
                              'xstart': 0,'ystart': -0.3787, 'zinc': 0.0165, 'zstart': 0.2411,
                              'sx_xinc': 0.0, 'sx_yinc':0.0, 'sx_zinc':0.0}, abs=.001)
                               
    assert backscan.pop('orient') == '0.000 -0.174 0.985' # was 0,0,1 in v0.2.4
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1,  'xinc': 0, 'yinc': 0.09357,
                              'xstart': 0,  'ystart': -0.3733, 'zinc': 0.0165,'zstart': 0.2115,
                                'sx_xinc': 0.0, 'sx_yinc':0.0, 'sx_zinc':0.0}, abs=.001)
                        # zstart was 0.01 and zinc was 0 in v0.2.2
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 10 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 0 objects\\simple_panel.rad'
    assert scene.text[0:105] == '!xform -rx 10 -t 0 0 0.2825 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -14.4 -4.5 0 -rz 0 -t 0 0 0 "objects' #linux has different directory structure and will error here.

def test_SceneObj_makeSceneNxR_hightilt():
    # test _makeSceneNxR(tilt, height, pitch, orientation = None, azimuth = 180, nMods = 20, nRows = 7, radname = None)
    # default scene with simple_panel, 50 degree tilt, 0.2 height, 1.5 row spacing, landscape
    name = "_test__makeSceneNxR_hightilt"
    demo = bifacial_radiance.RadianceObj(name) 
    demo.makeModule(name='test-module',y=0.95,x=1.59)
    #scene = bifacial_radiance.SceneObj(moduletype = name)
    #scene._makeSceneNxR(tilt=65,height=0.2,pitch=1.5,azimuth=89)
    sceneDict={'tilt':65, 'clearance_height':0.2, 'pitch':1.5, 'azimuth':89}
    scene = demo.makeScene(module='test-module', sceneDict=sceneDict)
    analysis = bifacial_radiance.AnalysisObj()
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
        
    temp = frontscan.pop('orient')
    '''
    assert [float(x) for x in temp.split(' ')] == pytest.approx([-0.999847695156, -0.0174524064373, 0])

    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0, 'xstart': 0, 'yinc': 0,
                                'ystart': 0, 'zinc': 0.086099239768481745,'zstart': 0.28609923976848173})
                               
    temp2 = backscan.pop('orient')
    assert [float(x) for x in temp2.split(' ')] == pytest.approx([0.999847695156, 0.0174524064373, 0])
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 1, 'Nz': 9, 'xinc': 0, 'xstart': -0.94985531039857163, 
                            'yinc': 0, 'ystart': -0.016579786115419416, 'zinc': 0.086099239768481745, 'zstart': 0.28609923976848173})
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
    assert scene.text[0:93] == '!xform -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -16.0 -4.5 0 -rz 91 objects'
    '''   
    assert [float(x) for x in temp.split(' ')] == pytest.approx([-0.906, -0.016, -0.423]) #was 0,0,-1 in v0.2.4

    assert frontscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1, 'xinc': -0.04013, 'xstart': 0.1832, 'yinc': -0.0007,
                                'ystart': 0.00313, 'zinc': 0.0861,'zstart':  0.296,
                                'sx_xinc': 0.0, 'sx_yinc':0.0, 'sx_zinc':0.0}, abs=.001)
                               
    temp2 = backscan.pop('orient')
    assert [float(x) for x in temp2.split(' ')] == pytest.approx([0.906, 0.016, 0.423]) #was 0,0,1 in v0.2.4
    assert backscan == pytest.approx({'Nx': 1, 'Ny': 9, 'Nz': 1, 
                            'xinc': -0.0401, 'xstart': 0.156, 
                            'yinc': -0.0007, 'ystart': 0.002787, 
                            'zinc': 0.0861, 'zstart': 0.284,
                            'sx_xinc': 0.0, 'sx_yinc':0.0, 'sx_zinc':0.0}, abs=.001)
    #assert scene.text == '!xform -rz -90 -t -0.795 0.475 0 -rx 65 -t 0 0 0.2 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -15.9 -4.5 0 -rz 91 objects\\simple_panel.rad'
    assert scene.text[0:106] == '!xform -rx 65 -t 0 0 0.6304 -a 20 -t 1.6 0 0 -a 7 -t 0 1.5 0 -i 1 -t -14.4 -4.5 0 -rz 91 -t 0 0 0 "objects'
    assert analysis._linePtsArray(frontscan)[1][0:3] == pytest.approx([0.0032, 0.0025, 0.0018], abs=.0001)

 
def test_AnalysisObj_linePtsMake3D():
    # test linepts = linePtsMake3D(xstart,ystart,zstart,xinc,yinc,zinc,Nx,Ny,Nz,orient):
    analysis = bifacial_radiance.AnalysisObj()
    linepts = analysis._linePtsMake3D(0,0,0,1,1,1,0,0,0,1,2,3,'0 1 0')
    assert linepts == '0 0 0 0 1 0 \r1 1 1 0 1 0 \r0 0 0 0 1 0 \r1 1 1 0 1 0 \r0 0 0 0 1 0 \r1 1 1 0 1 0 \r' # v2.5.0 new linepts because now x and z also increase not only y.
    #assert linepts == '0 0 0 0 1 0 \r0 1 0 0 1 0 \r0 0 1 0 1 0 \r0 1 1 0 1 0 \r0 0 2 0 1 0 \r0 1 2 0 1 0 \r'
    assert str(analysis).split(',')[5] == " 'rowWanted': None" # this depends on the order of the dict. but generally aligns with 'octfile' in alphabetical order..


def test_gendaylit2manual():
    name = "_test_gendaylit2manual"
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround('litesoil') 
    skyname = demo.gendaylit2manual(dni = 700, dhi = 100, sunalt = 67, sunaz = 180) # Invented values.
    assert skyname[0:5] == 'skies' # Having trouble with the \ or // with 'skies\sky2__test_gendaylit2manual.rad'


    
def test_SingleModule_HPC():
    # 1 module for STC conditions. DNI:900, DHI:100, sun angle: 33 elevation 0 azimuth
    name = "_test_SingleModule_end_to_end"
    demo = bifacial_radiance.RadianceObj(name, hpc=True)  # Create a RadianceObj 'object'
    demo.setGround('litesoil') 
    metdata = demo.readWeatherFile(weatherFile= MET_FILENAME, coerce_year=2001)
    timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 13:0:0 -7'))
    demo.gendaylit(timeindex=timeindex, metdata=metdata, debug=True)  # 1pm, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    tilt=demo.getSingleTimestampTrackerAngle(metdata=metdata, timeindex=timeindex, gcr=0.33)
    assert tilt == pytest.approx(-6.7, abs = 0.4)
    sceneDict = {'tilt':0,'pitch':1.5,'clearance_height':1, 'nMods':1, 'nRows':1}  
    module=demo.makeModule(name='test-module',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene(module,sceneDict) 
    #objname='Marker'
    #text='! genbox white_EPDM mymarker 0.02 0.02 2.5 | xform -t -.01 -.01 0'   
    #customObject = demo.makeCustomObject(objname,text)
    #demo.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')

    # check that scene radfile is using full path since hpc=True
    with open(demo.getfilelist()[-1], 'r') as f:
        temp = f.readline()
        assert (temp.count('\\')+temp.count('/') > 1)

    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name, hpc=True)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene, sensorsy=1, debug=True, frontsurfaceoffset=None, backsurfaceoffset=None)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance  
    assert analysis.mattype[0][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[0][:12] == 'a0.0.a0.test'
    assert analysis.x == [0]
    assert analysis.y == [0]
    assert np.mean(analysis.Wm2Front) == pytest.approx(1025, abs = 2)
    analysis.makeImage('side.vp')
    analysis.makeFalseColor('side.vp') #TODO: this works on silvanas computer, 
    # side.vp must exist inside of views folder in test folder... make sure this works 
    # in other computers
    assert np.mean(analysis.Wm2Back) == pytest.approx(166, abs = 6)
    demo.makeModule() # return information text about how to makeModule 

def test_left_label_metdata():
    # left labeled MetObj read in with -1 hour timedelta should be identical to 
    # right labeled MetObj
    import pvlib
    import pandas as pd
    (tmydata, metadata) = pvlib.iotools.epw.read_epw(MET_FILENAME, coerce_year=2001)
    # rename different field parameters to match output from 
    # pvlib.tmy.readtmy: DNI, DHI, DryBulb, Wspd
    tmydata.rename(columns={'dni':'DNI',
                            'dhi':'DHI',
                            'temp_air':'DryBulb',
                            'wind_speed':'Wspd',
                            'ghi':'GHI',
                            'albedo':'Alb'
                            }, inplace=True)    
    metdata1 = bifacial_radiance.MetObj(tmydata, metadata, label='left')
    columnlist = ['ghi', 'dhi', 'dni', 'albedo', 'dewpoint', 'pressure', 'temp_air','wind_speed']
    assert all([col in list(metdata1.tmydata.columns) for col in columnlist])
    metadatalist = ['city', 'elevation', 'label', 'latitude', 'longitude', 'timezone']
    assert all([col in list(metdata1.metadata.keys()) for col in metadatalist])

    
    demo = bifacial_radiance.RadianceObj('test')
    metdata2 = demo.readWeatherFile(weatherFile=MET_FILENAME, label='right', coerce_year=2001)
    #pd.testing.assert_frame_equal(metdata1.solpos[:-1], metdata2.solpos[:-1])
    assert all(metdata1.ghi == metdata2.ghi)
    assert metdata2.solpos.index[0] == pd.to_datetime('2001-01-01 07:42:00 -7')

    
def test_analyzeRow():  
    # test analyzeRow. Requires metdata for boulder. 

    name = "_test_analyzeRow"
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround(0.2)
    metdata = demo.readWeatherFile(weatherFile = MET_FILENAME)    
    nMods = 2
    nRows = 2
    sceneDict = {'tilt':0, 'pitch':30, 'clearance_height':3,
                 'azimuth':90, 'nMods': nMods, 'nRows': nRows} 
    demo.setGround(0.2)
    demo.gendaylit(4020)
    demo.makeModule(name='test-module',y=1,x=2, xgap=0.0)
    scene = demo.makeScene('test-module',sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    rowscan = analysis.analyzeRow(octfile=octfile, scene=scene, name=name, 
                                  rowWanted=1, sensorsy=[5,3])
    assert len(rowscan) == 2
    assert rowscan.keys()[2] == 'z'
    assert len(rowscan[rowscan.keys()[2]][0]) == 5
    # Assert z is the same for two different modules
    assert rowscan[rowscan.keys()[2]][0][0] == rowscan[rowscan.keys()[2]][1][0]
    # Assert Y is different for two different modules
    assert rowscan[rowscan.keys()[1]][0][0]+2 == rowscan[rowscan.keys()[1]][1][0]
    assert (analysis.__printval__('x')[2] == 0) & (analysis.x[2] == 0)
    assert any( analysis.__printval__('Wm2Front') != analysis.Wm2Front)
    temp = analysis.__repr__() # does the repr compile at all?
    assert analysis.rearX == pytest.approx([0.25, 0, -0.25])
    assert analysis.x == pytest.approx([.333, .167, 0, -.167, -.333], abs=.001)
    # test default xscan and yscan = 1
    rowscan = analysis.analyzeRow(octfile=octfile, scene=scene, name=name, 
                                  rowWanted=1, sensorsy=None, sensorsx=None)
    assert analysis.x == pytest.approx([0])
    assert analysis.rearX == pytest.approx([0])

    # test part 2: run a 2D groundAnalysis for the scene
    groundscan = analysis.groundAnalysis(scene=scene, modWanted=1, rowWanted=1, 
                       sensorsground=None, sensorsgroundx=9)
    assert groundscan['xinc'] == pytest.approx(0.20, abs=0.01)
    assert groundscan['yinc'] == 0
    assert groundscan['sx_yinc'] == pytest.approx(0.2, abs=0.01)

def test_addMaterialGroundRad():  
    # test addMaterialGroundRad.  requires metdata for boulder. 
    name = "_test_addMaterial"
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround(0.2)
    material = 'demoMat'
    com = "a demonstration material"
    Rrefl = 0.9
    Grefl = 0.2
    Brefl = 0.9
    demo.addMaterial(material=material, Rrefl=Rrefl, Grefl=Grefl, Brefl=Brefl, comment=com)
    demo.setGround('demoMat')
    assert list(demo.ground.Rrefl) == [0.9]
    Rrefl = 0.45
    demo.addMaterial(material=material, Rrefl=Rrefl, Grefl=Grefl, Brefl=Brefl, comment=com, rewrite=False)
    demo.setGround('demoMat')
    assert list(demo.ground.Rrefl) == [0.9]
    demo.addMaterial(material=material, Rrefl=Rrefl, Grefl=Grefl, Brefl=Brefl, comment=com, rewrite=True)
    demo.setGround('demoMat')
    assert list(demo.ground.Rrefl) == [0.45]
    
def test_verticalmoduleSouthFacing():  
    # test full routine for Vertical Modules.  
    name = "_test_verticalSouthFacing"   
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround(0.2) 
    metdata = demo.readWeatherFile(weatherFile = MET_FILENAME)    
    demo.gendaylit(4020)  
    demo.makeModule(name='test-module',y=2,x=1)
    sceneDict = {'gcr': 0.35,'hub_height':2.3, 'tilt': 90, 'azimuth': 180, 
                 'nMods':1, 'nRows': 1}  
    scene = demo.makeScene('test-module',sceneDict)
    octfile = demo.makeOct(demo.getfilelist())  
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = [4,4])
    results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
    assert analysis.mattype[0][:12] == 'a0.0.a0.test'
    assert analysis.mattype[1][:12] == 'a0.0.a0.test'
    assert analysis.mattype[2][:12] == 'a0.0.a0.test'
    assert analysis.mattype[3][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[0][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[1][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[2][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[3][:12] == 'a0.0.a0.test'
    assert analysis.x[0] == analysis.x[1]
    assert analysis.x[1] == analysis.x[2]
    assert round(analysis.x[0]) == 0
    assert round(analysis.x[0]) == 0
    assert analysis.z[3] == pytest.approx(2.9, abs=0.002)

def test_verticalmoduleEastFacing():  
    # test full routine for Vertical Modules.  
    name = "_test_verticalEastFacing"   
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround(0.2) 
    metdata = demo.readWeatherFile(weatherFile = MET_FILENAME)    
    demo.gendaylit(4020)  
    demo.makeModule(name='test-module',y=2,x=1)
    sceneDict = {'gcr': 0.35,'hub_height':2.3, 'tilt': 90, 'azimuth': 90, 
                 'nMods':1, 'nRows': 1}  
    scene = demo.makeScene('test-module',sceneDict)
    octfile = demo.makeOct(demo.getfilelist())  
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=4)
    results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
    assert analysis.mattype[0][:12] == 'a0.0.a0.test'
    assert analysis.mattype[1][:12] == 'a0.0.a0.test'
    assert analysis.mattype[2][:12] == 'a0.0.a0.test'
    assert analysis.mattype[3][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[0][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[1][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[2][:12] == 'a0.0.a0.test'
    assert analysis.rearMat[3][:12] == 'a0.0.a0.test'
    assert analysis.x[0] == analysis.x[1]
    assert analysis.x[1] == analysis.x[2]
    assert round(analysis.y[0]) == 0
    assert round(analysis.y[0]) == 0
    assert analysis.z[3] == pytest.approx(2.9, abs=0.003)
    
def test_tiltandazimuthModuleTest():  
    # test full routine for Vertical Modules.  
    name = "_test_tiltandazimuth"   
    demo = bifacial_radiance.RadianceObj(name)
    demo.setGround(0.2) 
    metdata = demo.readWeatherFile(weatherFile = MET_FILENAME)    
    demo.gendaylit(4020)  
    demo.makeModule(name='test-module',y=2,x=1)
    sceneDict = {'gcr': 0.35,'hub_height':2.3, 'tilt': 45, 'azimuth': 135, 
                 'nMods':1, 'nRows': 1}  
    scene = demo.makeScene('test-module',sceneDict)
    octfile = demo.makeOct()  
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy = [4,4])
    results = analysis.analysis(octfile, demo.basename, frontscan, backscan) 
    assert analysis.mattype[0] == 'a0.0.a0.test-module.6457'
    assert analysis.mattype[1] == 'a0.0.a0.test-module.6457'
    assert analysis.mattype[2] == 'a0.0.a0.test-module.6457'
    assert analysis.mattype[3] == 'a0.0.a0.test-module.6457'
    assert analysis.rearMat[0] == 'a0.0.a0.test-module.2310'
    assert analysis.rearMat[1] == 'a0.0.a0.test-module.2310'
    assert analysis.rearMat[2] == 'a0.0.a0.test-module.2310'
    assert analysis.rearMat[3] == 'a0.0.a0.test-module.2310'
    
def test_readWeatherFile_extra():
    # test mm_DD input, trim=true, Silvana's 15-minute multi-year file. Test PSM3 file

    
    name = "_test_readWeatherFile_extra"   
    demo = bifacial_radiance.RadianceObj(name)
    metdata1 = demo.readWeatherFile(weatherFile = MET_FILENAME,
                                   starttime = '06_01')
    
    metdata2 = demo.readWeatherFile(weatherFile = MET_FILENAME,
                                   starttime = '06_01_12')
    
    starttime = datetime.datetime(2021,6,1,12)
    metdata3 = demo.readWeatherFile(weatherFile=MET_FILENAME,
                                   starttime=starttime, 
                                   coerce_year=2021)  
     
    starttime = pd.to_datetime('2021-06-01')
    metdata4 = demo.readWeatherFile(weatherFile = MET_FILENAME,
                                   starttime=starttime 
                                   )  
    
    assert metdata1.ghi[0] == 2
    assert metdata2.ghi[0] == 610
    assert metdata3.ghi[0] == 610 
    assert metdata4.ghi[0] == 2  

    metdata6 = demo.readWeatherFile(weatherFile=MET_FILENAME6, source='PSM3')
    
def test_readWeatherFile_subhourly():
    # need to test out is_leap_and_29Feb and _subhourlydatatoGencumskyformat
    # and len(tmydata) != 8760 and _readSOLARGIS
    name = "_test_readWeatherFile_subhourly_gencumsky"   
    demo = bifacial_radiance.RadianceObj(name)
    metdata = demo.readWeatherFile(weatherFile=MET_FILENAME4,
                                    source='solargis', tz_convert_val= 2 )
    assert len(demo.gencumsky_metfile) == 2
    gencumsky_file2 = pd.read_csv(demo.gencumsky_metfile[1], delimiter=' ', 
                                    header=None)
    assert gencumsky_file2.__len__() == 8760
    assert gencumsky_file2.iloc[11,0] == pytest.approx(284.0, abs=0.1)
    assert metdata.elevation == 497
    assert metdata.timezone == 2
    # test McGuire AFB epwfile
    metdata2 = demo.readWeatherFile(weatherFile='USA_NJ_McGuire.AFB.724096_TMY3.epw', coerce_year=2000)
    leapday = (metdata2.tmydata.index.month == 2) & (metdata2.tmydata.index.day == 29)
    assert leapday.sum() == 0

def test_nsrdb_readWeatherFile():
    # initial test of NSRDBWeatherData in main.py
    import json
    name = "_test_nsrdb_readWeatherFile" 
    with open('nsrdb_boulder_metadata.json', 'r') as fp:
        metadata = json.load(fp)
    metdata = pd.read_csv('nsrdb_boulder_metdata.csv', index_col=0, parse_dates=True)
    radObj = bifacial_radiance.RadianceObj(name) 
    metData = radObj.readWeatherData(metadata, metdata, starttime='11_08_09', endtime='11_08_11',coerce_year=2021)
    
    assert metData.ghi[0] == 450
    assert metData.albedo[0] == 0.15
    assert metData.label == 'center'
    assert metData.timezone == -7
    
    metData= radObj.readWeatherFile('Custom_WeatherFile_TMY3format_15mins_2021_wTrackerAngles_BESTFieldData_2.csv')
    
def test_customTrackerAngles():
    # TODO: I think with the end test on this function the 
    #         test_RadianceObj_set1axis is no longer needed 
    name = "_test_customTrackerAngles"   
    demo = bifacial_radiance.RadianceObj(name)
    metdata = demo.readWeatherFile(weatherFile=MET_FILENAME5)
    assert metdata.meastracker_angle is not None
    trackerdict = demo.set1axis(azimuth=90, useMeasuredTrackerAngle=True)
    assert trackerdict[-20]['count'] == 3440
    trackerdict = demo.set1axis(azimuth=90, useMeasuredTrackerAngle=False)
    assert trackerdict[-20]['count'] == 37
    
def test_addPiles():
    # Test adding piles to the scene.
    # TODO: implement and test functionality in makescene1axis
    name = "_addPiles"
    demo = bifacial_radiance.RadianceObj(name)
    module = demo.makeModule(name='test', x=1.59, y=0.95)
    sceneDict = {'tilt':10,'pitch':1.5,'hub_height':.5,
                 'azimuth':180, 'nMods': 10, 'nRows': 3}
    scene = demo.makeScene(module=module, sceneDict=sceneDict)
    scene.addPiles()
    assert scene.radfiles[1][-23:] == 'Piles_6_0.2_0.2_0.5.rad'
    with open(scene.radfiles[1], 'r') as f:
        assert f.read()[:87] == '!xform -rx 0 -a 3.0 -t 6 0 0 -a 3 ' + \
        '-t 0 1.5 0 -i 1 -t -6.4 -1.5 0 -rz 0 -t 0 0 0 objects'
        
def test_customObj():
    # Test using appendtoScene to make custom objects.
    name = "_customObj"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    module = demo.makeModule(name='test', x=1.59, y=0.95)
    sceneDict = {'tilt':10,'pitch':1.5,'hub_height':.5,
                 'azimuth':180, 'nMods': 10, 'nRows': 3}
    scene = demo.makeScene(module=module, sceneDict=sceneDict)
    assert demo.sceneNames() == ['Scene0'] 
    
    objname='Marker'
    text='! genbox white_EPDM mymarker 0.02 0.02 2.5 | xform -t -.01 -.01 0'   
    customObject = demo.makeCustomObject(objname,text)
    demo.appendtoScene(scene.radfiles[0], customObject, '-rz 0')
    scene.appendtoScene(customObject=customObject, text='-t 1 1 0')
    
    with open(scene.radfiles[0], 'r') as f:
        assert f.readline().__len__() == 112 
        assert f.readline()[0:26] == '!xform -rx 0 -rz 0 objects'
        assert f.readline()[0:29] == '!xform -rx 0 -t 1 1 0 objects'
    
    # continue as 1-axis time based analysis with customObj.
    metdata = demo.readWeatherFile(weatherFile=MET_FILENAME, starttime='01_01_08', endtime = '01_01_10', coerce_year=2001) # read in the EPW weather data from above
    trackerdict = demo.set1axis(cumulativesky = False)
    trackerdict= demo.makeScene1axis(sceneDict={'hub_height':0.5, 'pitch':1.5, 'azimuth':180}, 
                                     customtext='-t 1 1 0 '+customObject, append=False)
    trackerdict= demo.makeScene1axis(sceneDict={'hub_height':0.75, 'pitch':1.0, 'azimuth':180}, 
                                     customtext='-t 2 1 0 '+customObject, append=True)
    with open(trackerdict['2001-01-01_0800']['scenes'][0].radfiles, 'r') as f:
        f.readline()
        line = f.readline()  #Linux uses backslash, windows forward slash...
        assert(line  == '!xform -rx 0  -t 1 1 0 objects/Marker.rad') or (line  == r'!xform -rx 0  -t 1 1 0 objects\Marker.rad')
    with open(trackerdict['2001-01-01_0900']['scenes'][1].radfiles, 'r') as f:
        f.readline()
        line = f.readline()
        assert(line == '!xform -rx 0  -t 2 1 0 objects/Marker.rad') or (line == r'!xform -rx 0  -t 2 1 0 objects\Marker.rad')
        
    
def test_raypath():
    # test errors and raypath updates
    import re
    raypath0 = os.getenv('RAYPATH', default=None)
    
    os.environ['RAYPATH'] = ''
    with pytest.raises(Exception):
        bifacial_radiance.main._checkRaypath()
    os.environ['RAYPATH'] = 'test'
    bifacial_radiance.main._checkRaypath()
    assert '.' in re.split(':|;', os.environ['RAYPATH'])
    
    os.environ['RAYPATH'] = raypath0    

def test_GH256_nomodule_error():
    moduletype = 'moduletypeNOTonJason'
    startdate= '09_23_08'
    enddate = '09_23_08'
    demo = bifacial_radiance.RadianceObj('test')
    metdata = demo.readWeatherFile(MET_FILENAME, starttime=startdate, endtime=enddate)
    demo.setGround()
    sceneDict = {'pitch': 7,'hub_height':2, 'nMods':1, 'nRows': 1, 'module_type':moduletype}
    trackerdict = demo.set1axis(metdata = metdata, cumulativesky = False)
    foodict = demo.gendaylit1axis()
    with pytest.raises(Exception):
        foodict = demo.makeScene1axis(trackerdict=foodict, module=moduletype, 
                                      sceneDict=sceneDict, cumulativesky=False)
    

    