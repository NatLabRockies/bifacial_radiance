# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 10:08:25 2018

@author: cdeline

Using pytest to create unit tests for gencumulativesky.
Note that this can't be included in the repo until TravisCI has a Linux version of gencumsky
set up in .travis.yml

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance

"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance
import numpy as np
import pytest
import os

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
DEBUG = True

"""
def test_SingleModule_gencumsky():
    import datetime
    
    # 1 module for STC conditions. DNI:900, DHI:100, sun angle: 33 elevation 0 azimuth
    name = "_test_fixedtilt_end_to_end"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(0.62) 
    metdata = demo.readWeatherFile(MET_FILENAME, starttime='06_17_13', endtime='06_17_13')
    demo.genCumSky()  # 1p, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2, 'nMods':10, 'nRows':3}  
    demo.makeModule(name='test',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test',sceneDict) 
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance  
    assert analysis.mattype[0][:12] == 'a4.1.a0.test'
    assert analysis.rearMat[0][:12] == 'a4.1.a0.test'
    assert np.mean(analysis.x) == pytest.approx(0)
    assert np.mean(analysis.rearY) == pytest.approx(0.00017364868888889194, abs = 0.0001)

    if DEBUG:
        print(np.mean(analysis.Wm2Front))
        print(np.mean(analysis.Wm2Back))
        print(np.mean(analysis.backRatio))
    # Note: gencumsky has 30-50 Wm-2 variability from run to run...  unsure why.
    assert np.mean(analysis.Wm2Front) == pytest.approx(1030, abs = 60)  #1023,1037,1050, 1035, 1027, 1044, 1015, 1003, 1056
    assert np.mean(analysis.Wm2Back) == pytest.approx(133, abs = 15) # 127, 131, 131, 135, 130, 139, 120, 145
    
    # run 1-axis gencumsky option
    trackerdict = demo.set1axis(metdata, limit_angle = 45, backtrack = True, gcr = 0.33)
    demo.genCumSky1axis(trackerdict)
"""
    
def test_SingleModule_gencumsky_modelchain():
    # duplicate previous sample using modelchain
    # 1-axis .ini file
    filename = "ini_gencumsky.ini"

    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=filename)
    Params[0]['testfolder'] = TESTDIR
    # unpack the Params tuple with *Params
    demo2, analysis = bifacial_radiance.modelchain.runModelChain(*Params ) 
    #V 0.2.5 fixed the gcr passed to set1axis. (since gcr was not being passd to set1axis, gcr was default 0.33 default). 
    assert analysis.mattype[0][:12] == 'a4.1.a0.test'
    assert analysis.rearMat[0][:12] == 'a4.1.a0.test'
    assert np.mean(analysis.x) == pytest.approx(0)
    rearY = [-0.373, -0.28, -0.186, -0.093, 0.0, 0.094, 0.188, 0.281, 0.375]
    for (a,b) in zip(rearY, analysis.rearY):
        assert a == pytest.approx(b, abs=.001)
    if DEBUG:
        print(f'Wm2Front: {np.mean(analysis.Wm2Front)}')
        print(f'Wm2Back: {np.mean(analysis.Wm2Back)}')
        print(f'backRatio: {np.mean(analysis.backRatio)}')
    # Note: gencumsky has 30-50 Wm-2 variability from run to run...  unsure why.
    assert np.mean(analysis.Wm2Front) == pytest.approx(1030, abs = 60)  #1023,1037,1050, 1035, 1027, 1044, 1015, 1003, 1056
    assert np.mean(analysis.Wm2Back) == pytest.approx(133, abs = 15) # 127, 131, 131, 135, 130, 139, 120, 145


def test_set1axis_gendaymtx():
    # load met_filename2 and test the set1axis function with gendaymtx
    demo = bifacial_radiance.RadianceObj("test_set1axis_gendaymtx")  # Create a RadianceObj 'object'
    epwfile = MET_FILENAME2
    metdata = demo.readWeatherFile(weatherFile=epwfile, coerce_year=2001)
    trackerdict = demo.set1axis(use_mtx=True)
    assert trackerdict[5]['count'] == 142
    assert trackerdict[45]['count'] == 821 #

def test_reinhart():
    bands = bifacial_radiance.main._make_reinhart_bands(1)
    assert bands == [(0.0, 12.0, 30, 12.0),
                    (12.0, 24.0, 30, 12.0),
                    (24.0, 36.0, 24, 15.0),
                    (36.0, 48.0, 24, 15.0),
                    (48.0, 60.0, 18, 20.0),
                    (60.0, 72.0, 12, 30.0),
                    (72.0, 84.0, 6, 60.0),
                    (84, 90, 1, 360.0)]
    bands2 = bifacial_radiance.main._make_reinhart_bands(2)
    assert bands2 == [(0.0, 6.0, 60, 6.0),
                    (6.0, 12.0, 60, 6.0),
                    (12.0, 18.0, 60, 6.0),
                    (18.0, 24.0, 60, 6.0),
                    (24.0, 30.0, 48, 7.5),
                    (30.0, 36.0, 48, 7.5),
                    (36.0, 42.0, 48, 7.5),
                    (42.0, 48.0, 48, 7.5),
                    (48.0, 54.0, 36, 10.0),
                    (54.0, 60.0, 36, 10.0),
                    (60.0, 66.0, 24, 15.0),
                    (66.0, 72.0, 24, 15.0),
                    (72.0, 78.0, 12, 30.0),
                    (78.0, 84.0, 12, 30.0),
                    (84, 90, 1, 360.0)]

def test_gencumskyMTX():
    # test the genCumSky1axis modelchain function with the use_mtx option
    import datetime
    filename = "ini_gendaymtx.ini"
    
    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=filename)
    Params[0]['testfolder'] = TESTDIR
    # unpack the Params tuple with *Params
    (demo_mtx, temp) = bifacial_radiance.modelchain.runModelChain(*Params ) 
    analysis_mtx = demo_mtx.trackerdict[5]['AnalysisObj'][0]
    # make sure the use_mtx=True branch is being taken:
    assert demo_mtx.trackerdict[5]['csvfile'] == os.path.join('EPWs', '1axis_5.0.wea')
    # does the scan line up with anything?
    assert analysis_mtx.mattype[5][:12] == 'a4.1.a0.test'
    assert analysis_mtx.rearMat[5][:12] == 'a4.1.a0.test'
    if DEBUG:
        print(np.mean(analysis_mtx.Wm2Front))
        print(np.mean(analysis_mtx.Wm2Back))
        print(np.mean(analysis_mtx.backRatio))
    assert np.mean(analysis_mtx.Wm2Front) == pytest.approx(1030, abs = 40)  #1035 1008 1032 1034 1009 1050 1047
    assert np.mean(analysis_mtx.Wm2Back) == pytest.approx(371, abs = 15) # 374 368 368 369 372 368 370 383

    """
    # 1 module for STC conditions. DNI:900, DHI:100, sun angle: 33 elevation 0 azimuth
    name = "test_gencumskyMTX"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    demo.setGround(0.62) 
    metdata = demo.readWeatherFile(MET_FILENAME, starttime='06_17_13', endtime='06_17_13')
    demo.genCumSky(use_mtx=True)  # 1p, June 17th
    # create a scene using panels in landscape at 10 deg tilt, 1.5m pitch. 0.2 m ground clearance
    sceneDict = {'tilt':10,'pitch':1.5,'clearance_height':0.2, 'nMods':10, 'nRows':3}  
    demo.makeModule(name='test',y=0.95,x=1.59, xgap=0)
    scene = demo.makeScene('test',sceneDict) 
    octfile = demo.makeOct(demo.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)  # return an analysis object including the scan dimensions for back irradiance
    (frontscan,backscan) = analysis.moduleAnalysis(scene)
    analysis.analysis(octfile, demo.name, frontscan, backscan)  # compare the back vs front irradiance  
    assert analysis.mattype[0][:12] == 'a4.1.a0.test'
    assert analysis.rearMat[0][:12] == 'a4.1.a0.test'
    assert np.mean(analysis.x) == pytest.approx(0)
    rearY = [-0.373, -0.28, -0.186, -0.093, 0.0, 0.094, 0.188, 0.281, 0.375]
    for (a,b) in zip(rearY, analysis.rearY):
        assert a == pytest.approx(b, abs=.001)

    if DEBUG:
        print(np.mean(analysis.Wm2Front))
        print(np.mean(analysis.Wm2Back))
        print(np.mean(analysis.backRatio))
    # Note: gencumsky has 30-50 Wm-2 variability from run to run...  unsure why.
    assert np.mean(analysis.Wm2Front) == pytest.approx(1030, abs = 60)  #1023,1037,1050, 1035, 1027, 1044, 1015, 1003, 1056
    assert np.mean(analysis.Wm2Back) == pytest.approx(133, abs = 15) # 127, 131, 131, 135, 130, 139, 120, 145
    
    # run 1-axis gencumsky option
    trackerdict = demo.set1axis(metdata, limit_angle = 45, backtrack = True, gcr = 0.33, use_mtx=True)
    demo.genCumSky1axis(trackerdict, use_mtx=True)
    assert os.path.basename(trackerdict[5]['skyfile']) == '1axis_5.0.rad'
    """

