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
        print(np.mean(analysis.Wm2Front))
        print(np.mean(analysis.Wm2Back))
        print(np.mean(analysis.backRatio))
    # Note: gencumsky has 30-50 Wm-2 variability from run to run...  unsure why.
    assert np.mean(analysis.Wm2Front) == pytest.approx(1030, abs = 60)  #1023,1037,1050, 1035, 1027, 1044, 1015, 1003, 1056
    assert np.mean(analysis.Wm2Back) == pytest.approx(133, abs = 15) # 127, 131, 131, 135, 130, 139, 120, 145