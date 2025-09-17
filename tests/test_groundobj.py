# -*- coding: utf-8 -*-
"""
Created 2/19/19

@author: cdeline

Using pytest to create unit tests for GroundObj

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

# also test a dummy TMY3 Boulder file in /tests/
MET_FILENAME =  'USA_CO_Boulder.724699_TMY2.epw'
MET_FILENAME2 =  '724666TYA.CSV'
# return albedo values in GroundObj
def _groundtest(groundobj):
    if type(groundobj) != bifacial_radiance.main.GroundObj:
        raise TypeError('bifacial_radiance.GroundObj not passed')
    
    return(groundobj.Rrefl, groundobj.Grefl, groundobj.Brefl, groundobj.ReflAvg)
        

def test_albedo_cases_orig():
    # test 'litesoil', constant albedo
    ground = bifacial_radiance.GroundObj('litesoil')
    testvals_litesoil = ([.29], [.187], [.163], [.213])
    np.testing.assert_allclose(_groundtest(ground), testvals_litesoil, atol=.001)
    
    ground = bifacial_radiance.GroundObj(0.2)
    testvals_const = ([.2], [.2], [.2], [.2])
    np.testing.assert_allclose(_groundtest(ground), testvals_const, atol=.001)


def test_albedo_tmy3():
    # test 1xN albedo array
    demo = bifacial_radiance.RadianceObj(name = 'test')
    demo.readWeatherFile(MET_FILENAME2, coerce_year=2001)
    demo.setGround(demo.metdata.albedo)
    assert demo.ground.Rrefl.mean() == pytest.approx(0.2051, abs=.0001)
    assert demo.ground.ReflAvg[0] == 0.33


def test_RGB_timeseries():
    # test 3xN albedo array with two timesteps
    albedo = np.array([[0.2, 0.3, 0.4],  [0.12, 0.13, 0.26]]) # 2 RGB Albedo
    ground = bifacial_radiance.GroundObj(albedo)
    testval = _groundtest(ground)
    testvals_const = ([[.2,.12], [.3, .13], [.4, .26], [.3,.17]])
    np.testing.assert_allclose(testval, testvals_const)
    
    # test 4xN albedo array which should be trimmed and raise a warning
    albedo_bad = np.array([[0.2, 0.3, 0.4, 0.5], [0.12, 0.13, 0.26, 0.5]]) # invalid
    ground = pytest.warns(UserWarning, bifacial_radiance.GroundObj, albedo_bad)
    np.testing.assert_allclose(_groundtest(ground), testvals_const)
    with pytest.raises(Exception):
        temp = bifacial_radiance.GroundObj(np.array([[.1,.2],[.1,.2]]))

def test_printGroundMaterials():
    ground = bifacial_radiance.GroundObj('litesoil')
    assert ground.printGroundMaterials()[1] == 'litesoil'

def test_albedo_greaterthan_one():
    ground = bifacial_radiance.GroundObj(2)
    assert ground.ReflAvg[0] == 1
    
def test_repr_and_normval(): 
    ground = bifacial_radiance.GroundObj()
    groundstr = ground.__repr__()
    ground = bifacial_radiance.GroundObj([0.1, 0.2])
    assert ground.normval == pytest.approx([0.10034, 0.20068])
