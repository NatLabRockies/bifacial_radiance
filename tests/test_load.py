# -*- coding: utf-8 -*-
"""
Created 2/19/19

@author: cdeline

Using pytest to create unit tests for load.py

to run unit tests, run pytest from the command line in the bifacial_radiance directory

"""

import bifacial_radiance
import os, pytest
import numpy as np

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder
MET_FILENAME = 'USA_CO_Boulder.724699_TMY2.epw'
TEST_FILE = os.path.join('results','test_2001-01-01_1000.csv')
TEST_FILE2_FRONT = os.path.join(TESTDIR, 'results', 'test_irr_1axis_2021-06-17_1300_Front.csv')
TEST_FILE2_BACK = os.path.join(TESTDIR, 'results', 'test_irr_1axis_2021-06-17_1300_Back.csv')


# test load function on a dummy csv file in the /tests/ directory

def test_save_load_pickle():
    # quick save and re-load the entire RadianceObj as a pickle
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.save('save.pickle')
    demo2 = bifacial_radiance.load.loadRadianceObj('save.pickle')
    assert demo2.name == 'test'

def test_load_trackerdict():
    # example of saving and loading files in /results/ for 1-axis hourly workflow.
    # this requires some pre-saved files in 
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.readWeatherFile(MET_FILENAME, coerce_year = 2001)
    trackerdict = demo.set1axis(cumulativesky = False)
    print(trackerdict)
    demo.loadtrackerdict(trackerdict,fileprefix = 'test_')
    # test that Wm2Front is deprecated
    with pytest.warns(DeprecationWarning):
        demo.Wm2Front
    with pytest.warns(DeprecationWarning):
        demo.Wm2Back
    #assert demo.Wm2Front[0] == pytest.approx(166.3, abs = 0.01)


def test_cleanResult():
    # example of setting NaN's when the scan intersects undesired material
    # test_01_01_10.csv has some ground and sky references

    resultsDF = bifacial_radiance.load.read1Result(TEST_FILE)
    cleanedDF = bifacial_radiance.load.cleanResult(resultsDF)
    assert np.isnan(cleanedDF.Wm2Front.loc[4]) 

def test_read1Result():
    # example of loading file in /results/ 
    # this requires one pre-saved files in  
    resultsDict=bifacial_radiance.load.read1Result(TEST_FILE)
    assert resultsDict['rearMat'][0] == 'a10.3.a0.PVmodule.2310'

def test_deepcleanResult():
    # example of loading file in /results/ 
    # this requires one pre-saved files in  
    resultfile=os.path.join("results", "test_2UP_torque_tube_hex_4020.csv")
    resultsDict=bifacial_radiance.load.read1Result(resultfile)
    Frontresults, Backresults=bifacial_radiance.load.deepcleanResult(resultsDict, 110, 2, automatic=True)
    assert len(Frontresults) == 110
    assert Backresults[54] == pytest.approx(244, rel = 0.01)
    assert Frontresults[54] == pytest.approx(593.824, rel = 0.001)
    
def test_deepcleanResult_sensorsy_mismatch():
    # example with front/back sensorsy of different length
    resultfile=os.path.join("results", "test_2UP_torque_tube_hex_4020_Front.csv")
    resultsDict=bifacial_radiance.load.read1Result(resultfile)
    Frontresults, temp =bifacial_radiance.load.deepcleanResult(resultsDict, 110, 2, automatic=True)
    assert len(Frontresults) == 110
    assert Frontresults[54] == pytest.approx(593.824, rel = 0.001)
    
    resultfile2=os.path.join("results", "test_2UP_torque_tube_hex_4020_Back.csv")
    resultsDict2=bifacial_radiance.load.read1Result(resultfile2)
    temp, Backresults = bifacial_radiance.load.deepcleanResult(resultsDict2, 110, 2, automatic=True)
    assert len(Backresults) == 110
    assert Backresults[54] == pytest.approx(244, rel = 0.01)

def test_gh126_raise_OSError():
    """Catch OSError for any platform instead of WindowsError"""
    with pytest.raises(OSError):
        nopath = '/there/is/no/path'
        demo = bifacial_radiance.RadianceObj(name='test', path=nopath)


def test_gh127_abspath():
    """RadianceObj path must be absolute"""
    testpath = os.path.abspath(os.path.dirname(__file__))
    projpath = os.path.dirname(testpath)
    temp_path = os.path.join(projpath, 'bifacial_radiance', 'TEMP')
    demo = bifacial_radiance.RadianceObj(name='test', path=temp_path)
    os.path.isabs(demo.path)


def test_gh130_import_tkinter():
    import tkinter
    from tkinter import filedialog


def test_gh128_import_requests():
    import requests

def test_celllevel_module():
    # test lines 593-637 `if simulationParamsDict['cellLevelModule']`
    # also test 'getEPW' 
    filename = os.path.join(TESTDIR,"ini_cell_level_module.ini")
    (Params)= bifacial_radiance.load.readconfigurationinputfile(inifile=filename)
    assert Params[0]['getEPW'] == False
    assert Params[7] == {'numcellsx': 12,
                         'numcellsy': 6,
                         'xcell': 0.15,
                         'ycell': 0.15,
                         'xcellgap': 0.01,
                         'ycellgap': 0.01}
    
def test_GH419_front_and_back_sensors():
    resultsDF_front = bifacial_radiance.load.read1Result(TEST_FILE2_FRONT)
    cleanedDF_front = bifacial_radiance.load.cleanResult(resultsDF_front)
    
    resultsDF_back = bifacial_radiance.load.read1Result(TEST_FILE2_BACK)
    cleanedDF_back = bifacial_radiance.load.cleanResult(resultsDF_back)
    assert np.isnan(cleanedDF_back.Wm2Back.loc[4]) 