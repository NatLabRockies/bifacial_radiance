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
import pandas as pd

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder

cellParams = {'xcell':0.156, 'ycell':0.156, 'numcellsx':6, 'numcellsy':10,  
               'xcellgap':0.02, 'ycellgap':0.02}

frameParams = {'frame_material' : 'Metal_Grey', 
               'frame_thickness' : 0.003,
               'frame_z' : 0.03,
               'nSides_frame' : 4,
               'frame_width' : 0.05}


omegaParams = {'omega_material': 'litesoil',
                'x_omega1' : 0.10,
                'mod_overlap' : 0.5,
                'y_omega' : 1.5,
                'x_omega3' : 0.05,
                'omega_thickness' : 0.01,
                'inverted' : False}



def test_CellLevelModule():
    # test the cell-level module generation 
    name = "_test_CellLevelModule"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'

    module = demo.makeModule(name='test-module', rewriteModulefile=True, cellModule=cellParams, customtext=r'!xform -rz 0 customTT.rad | xform -rz 90 -t 0.5 0 -0.15')
    assert module.x == 1.036
    assert module.y == 1.74
    assert module.scenex == 1.046
    assert module.sceney == 1.74
    assert module.text == '! genbox black cellPVmodule 0.156 0.156 0.02 | xform -t -0.44 -0.87 0 -a 6 -t 0.176 0 0 -a 10 -t 0 0.176 0 -a 1 -t 0 1.74 0\n!xform -rz 0 customTT.rad | xform -rz 90 -t 0.5 0 -0.15'
    module.addCellModule(**cellParams, centerJB=0.01)  #centerJB simulations still under development.
#    assert module.text == '! genbox black cellPVmodule 0.156 0.156 0.02 | xform -t -0.44 -0.87 0 -a 6 -t 0.176 0 0 -a 5.0 -t 0 0.176 0 -a 2 -t 0 0.772 0 | xform -t 0 0.181 0 -a 1 -t 0 1.73 0'
    assert len(module.cellModule.__repr__()) == 119
    assert len(module.__repr__()) > 490
    
def test_TorqueTubes_Module():
    name = "_test_TorqueTubes"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    # test pre-0.4.0 compatibility keys 'bool' and 'torqueTubeMaterial'.  Remove these when it's deprecated..
    module = demo.makeModule(name='square', y=0.95,x=1.59, tubeParams={'torqueTubeMaterial':'Metal_Grey','bool':True, 'tubetype':'square', 'axisofrotation':False}, hpc=True) #suppress saving .json
    assert module.x == 1.59
    assert module.text == '! genbox black square 1.59 0.95 0.02 | xform -t -0.795 -0.475 0 -a 1 -t 0 0.95 0\r\n! genbox Metal_Grey tube1 1.6 0.1 0.1 | xform -t -0.8 -0.05 -0.2'
    module = demo.makeModule(name='round', y=0.95,x=1.59, tubeParams={'tubetype':'round', 'axisofrotation':False}, hpc=True)
    assert module.text[0:30] == '! genbox black round 1.59 0.95'
    module = demo.makeModule(name='hex', y=0.95,x=1.59,  tubeParams={'tubetype':'hex', 'axisofrotation':False}, hpc=True)
    assert module.text[0:30] == '! genbox black hex 1.59 0.95 0'
    module = demo.makeModule(name='oct', y=0.95,x=1.59, hpc=True)
    module.addTorquetube(tubetype='oct', axisofrotation=False, recompile=False)
    module.compileText(rewriteModulefile=False, json=False)
    assert module.text[0:30] == '! genbox black oct 1.59 0.95 0'

def test_moduleFrameandOmegas():  
    # test moduleFrameandOmegas. Requires metdata for boulder. 

    name = "_test_moduleFrameandOmegas"
    demo = bifacial_radiance.RadianceObj(name)
    #demo.setGround(0.2)
    zgap = 0.10
   

    
    loopaxisofRotation = [True, True, True, True, True, True, True, True]
    loopTorquetube = [True, True, True, True, False, False, False, False ]
    loopOmega = [omegaParams, omegaParams, None, None, omegaParams, omegaParams, None, None]
    loopFrame = [frameParams, None, frameParams, None, frameParams,  None, frameParams, None]
    expectedModuleZ = [3.176, 3.145, 3.176, 3.145, 3.125, 3.095, 3.125, 3.095]
    
    # test inverted=True on the first test
    loopOmega[0]['inverted'] = True
    sceneDict = {'tilt':0, 'pitch':3, 'clearance_height':3,'azimuth':90,
                 'nMods': 1, 'nRows': 1}

    for ii in range (0, len(loopOmega)):

        if loopTorquetube[ii] is False:
            diam = 0.0
        else:  diam = 0.1

        module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, zgap = zgap,
                                             )
        module.addTorquetube(diameter=diam, axisofrotation=loopaxisofRotation[ii],
                             visible = loopTorquetube[ii]) 
        if loopFrame[ii]:
            module.addFrame(**loopFrame[ii])
                       
        if loopOmega[ii]:
            module.addOmega(**loopOmega[ii])  #another way to add omega parameters
        scene = demo.makeScene(module,sceneDict)
        analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates
        assert backscan['zstart'] == pytest.approx(expectedModuleZ[ii], abs=.001)
        
        # read the data back from module.json and check again
        module = demo.makeModule(name='test-module')
        scene = demo.makeScene('test-module',sceneDict)
        analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
        frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1)
        assert backscan['zstart'] == pytest.approx(expectedModuleZ[ii], abs=.001)
    # do it again by passing everying at once
    module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, zgap = zgap,
                                          frameParams=frameParams, omegaParams=omegaParams,
                                          tubeParams={'diameter':0.1,
                                                      'axisofrotation':True})
    scene = demo.makeScene(module, sceneDict)
    analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=1) # Gives us the dictionaries with coordinates
    assert backscan['zstart'] == pytest.approx(expectedModuleZ[0], abs=.001)
    
    # omega default values
    module.addOmega()
    assert module.omega.x_omega1==0.003; assert module.omega.y_omega==0.5; assert module.omega.x_omega3==0.005; 
    module.addOmega(inverted=True)
    assert module.omega.x_omega1==0.005; assert module.omega.y_omega==0.5; assert module.omega.x_omega3==0.0015; 
   
    # test cellModulescan (sensorsy = numellsy)
    module.glass=True
    module.addCellModule(**cellParams)
    # re-load the module to make sure all of the params are the same
    module2 = bifacial_radiance.ModuleObj(name='test-module')
    assert module.text == module2.text
    scene = demo.makeScene(module, sceneDict)
    analysis = bifacial_radiance.AnalysisObj()  # return an analysis object including the scan dimensions for back irradiance
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=10) # Gives us the dictionaries with coordinates
    assert backscan['xstart'] == pytest.approx(0.792, abs=.001)
    
def test_GlassModule():
    # test the cell-level module generation 
    name = "_test_GlassModule"
    # default glass=True with .001 absorber and 0.01 glass
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    module = demo.makeModule(name='test-module', rewriteModulefile=True, glass=True, x=1, y=2)
    assert module.text == '! genbox black test-module 1 2 0.001 | xform -t -0.5 -1.0 0 -a 1 -t 0 2.0' +\
        ' 0\r\n! genbox stock_glass test-module_Glass 1.01 2.01 0.01 | xform -t -0.505 -1.005 -0.005 -a 1 -t 0 2.0 0'
    # custom glass=True with .001 absorber and 0.005 glass and 0.02 glass edge
    module = demo.makeModule(name='test-module', glass=True, x=1, y=2, z=0.005, glassEdge=0.02) 
    assert module.text == '! genbox black test-module 1 2 0.001 | xform -t -0.5 -1.0 0 -a 1 -t 0 2.0' +\
        ' 0\r\n! genbox stock_glass test-module_Glass 1.02 2.02 0.005 | xform -t -0.51 -1.01 -0.0025 -a 1 -t 0 2.0 0'

def test_inifile():
    # test loading a module from a simulation .ini file
    INIFILE = os.path.join(TESTDIR, "ini_soltec.ini")

    (simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, trackingParamsDict, 
     torquetubeParamsDict, analysisParamsDict, cellLevelModuleParamsDict, CECMod, frameParamsDict, 
     omegaParamsDict, *kwargs )= bifacial_radiance.load.readconfigurationinputfile(inifile=INIFILE)
    
    simulationParamsDict['testfolder'] = TESTDIR
    name = "_test_inifile_module"
    demo = bifacial_radiance.RadianceObj(name)  # Create a RadianceObj 'object'
    module = demo.makeModule(name='test-module', tubeParams=torquetubeParamsDict, cellModule=cellLevelModuleParamsDict,
                              frameParams=frameParamsDict, omegaParams=omegaParamsDict, 
                              **moduleParamsDict)
    # check that there's a cellPVmodule, torque tube, framesides, framelegs, mod_adj, verti, tt_adj,
    assert module.glass == True
    assert module.glassEdge == 0.02
    assert module.text.find('genbox black cellPVmodule 0.15 0.15 0.001 | xform -t -1.375 -1.375') > 0
    assert module.text.find('genbox Metal_Grey hextube1a 2.926 0.05 0.0866') > 0
    assert module.text.find('genbox Metal_Grey frameside 0.003 1.3') > 0
    assert module.text.find('genbox Metal_Grey frameleg 0.017 1.3') > 0
    assert module.text.find('genbox Metal_Grey frameside 2.894 0.003 0.017') > 0
    assert module.text.find('genbox Metal_Grey mod_adj 0.05 1.5 0.009 | xform -t 1.41 -0.75 0.136') > 0
    assert module.text.find('genbox Metal_Grey verti 0.009 1.5 0.1 | xform -t 1.451 -0.75 0.045') > 0
    assert module.text.find('genbox Metal_Grey tt_adj 0.003 1.5 0.009 | xform -t 1.46 -0.75 0.045') > 0
    
    
    
    
def test_CECmodule():
    # Test adding CEC module in various ways
    CECMod1 = pd.read_csv(os.path.join(TESTDIR, 'Canadian_Solar_Inc__CS5P_220M.csv'),
                         index_col=0) #1D dataframe
    CECMod2 = CECMod1.iloc[:,0]  #pd.Series
    CECMod3 = CECMod2.to_dict()
    CECMod4 = pd.concat([CECMod1.T, CECMod1.T])
    module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, CECMod=CECMod1 )
    module.addCEC(CECMod2)
    module3 = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, CECMod=CECMod3 )
    module4 = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1, CECMod=CECMod4 )
    assert module4.CECMod.name=='Canadian_Solar_Inc__CS5P_220M'
    # check for exceptions
    with pytest.raises(Exception):
        CECMod3.pop('alpha_sc')
        module.addCEC(CECMod3)
    with pytest.raises(Exception):  #when module search function is enabled, this can be updated..
        module.addCEC('Canadian_Solar_Inc__CS5P_220M')        
    with pytest.raises(Exception):
        module.addCEC(1)     
    # check that CECMod is loaded in from module.json
    module2 = bifacial_radiance.ModuleObj(name='test-module' )
    assert module.CECMod.alpha_sc == module2.CECMod.alpha_sc == module3.CECMod.alpha_sc == module4.CECMod.alpha_sc

def test_modulePerformance():
    module = bifacial_radiance.ModuleObj(name='test-module',x=2, y=1)  
    