#!/usr/bin/env python
# coding: utf-8

"""
Created on Wed Sept 22 18:09:22 2021

@author: cdeline

Using pytest to create unit tests for bifacial_radiance.

to run unit tests, run pytest from the command line in the bifacial_radiance directory
to run coverage tests, run py.test --cov-report term-missing --cov=bifacial_radiance


"""

#from bifacial_radiance import RadianceObj, SceneObj, AnalysisObj
import bifacial_radiance as br
#import pytest
import os
import pandas as pd
import numpy as np

# try navigating to tests directory so tests run from here.
try:
    os.chdir('tests')
except:
    pass

TESTDIR = os.path.dirname(__file__)  # this folder

MET_FILENAME = os.path.join(TESTDIR,"724666TYA.CSV")
SPECTRA_FOLDER = os.path.join(TESTDIR,'Spectra')
os.makedirs(SPECTRA_FOLDER, exist_ok=True)
#testfolder = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\bifacial_radiance\TEMP'
#weatherfile = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\tests\USA_CO_Boulder.724699_TMY2.epw' 
#spectrafolder = r'C:\Users\cdeline\Documents\python scripts\bifacial_radiance\tests\spectra'


# # 1 ) Generate Spectra for 1 timestamp
# 
def test_generate_spectra():  
    # test set1axis.  requires metdata for boulder. 
    name = "_test_generate_spectra"
    rad_obj = br.RadianceObj(name, TESTDIR)
    metdata = rad_obj.readWeatherFile(MET_FILENAME, 
                                      starttime='2001-06-16',
                                      endtime='2001-06-16',
                                      coerce_year=2001)
    
    (spectral_alb, spectral_dni, spectral_dhi, weighted_alb) = rad_obj.generate_spectra(ground_material='Grass')
        
    assert spectral_alb.data.__len__() == 2002
    assert spectral_dhi.data.index[2001] == 4000.0
    assert spectral_dni.data.iloc[400,0] == 0.8669
    
def test_scale_spectra():  
    # test scaling of spectra and albedo 
    name = "_test_generate_spectra"
    rad_obj = br.RadianceObj(name, TESTDIR)
    metdata = rad_obj.readWeatherFile(MET_FILENAME, 
                                      starttime='2001-06-16',
                                      endtime='2001-06-16',
                                      coerce_year=2001)
    
    (spectral_alb, spectral_dni, spectral_dhi, weighted_alb) = rad_obj.generate_spectra(ground_material='Grass',
                                                                                        scale_spectra=True,
                                                                                        scale_albedo=True)
    assert spectral_alb.data.__len__() == 2002
    assert spectral_dhi.data.index[2001] == 4000.0
    assert (0.40682  <= spectral_dni.data.iloc[400][0] <= 0.5074)
    assert spectral_dni.data.iloc[400].name == 560.0
    assert weighted_alb == None

def test_nonspectral_albedo():
    # test scale_albedo_nonspectral_sim
    name = '_test_generate_nonspectral_albedo'
    rad_obj = br.RadianceObj(name, TESTDIR)
    metdata = rad_obj.readWeatherFile(MET_FILENAME,
                                      starttime='2001-06-16',
                                      endtime='2001-06-16',
                                      coerce_year=2001)

    weighted_alb = rad_obj.generate_spectra(ground_material='Grass', scale_albedo_nonspectral_sim=True)[3]
    
    assert np.round(weighted_alb[12],3) == 0.129 #this had been ~0.12855 previously?
    #assert((weighted_alb[12] <= 0.1286) & (weighted_alb[12] >= 0.1285))
    assert(len(weighted_alb) == 16)


def test_integrated_spectrum():
    """Test the integrated_spectrum function that integrates spectral data across wavelengths"""
    import tempfile
    from bifacial_radiance.spectral_utils import integrated_spectrum
    
    # Create test data and setup
    name = "_test_integrated_spectrum"
    rad_obj = br.RadianceObj(name, TESTDIR)
    metdata = rad_obj.readWeatherFile(MET_FILENAME, 
                                      starttime='2001-06-16',
                                      endtime='2001-06-16',
                                      coerce_year=2001)
    
    # Create temporary folder with mock spectral files for testing
    with tempfile.TemporaryDirectory() as temp_spectra_folder:
        # Create sample spectral files with the expected naming convention
        # Format: XXX_YY_MM_DD_HH_MM.txt where XXX is ALB, DNI, DHI, or GHI
        
        # Sample wavelengths and spectral data
        wavelengths = np.linspace(280, 4000, 50)  # 50 wavelength points for faster testing
        
        # Create test file for one timestamp
        date_str = '01_06_16_12_00'
        
        for irr_type in ['ALB', 'DNI', 'DHI', 'GHI']:
            filename = f"{irr_type.lower()}_{date_str}.txt"
            filepath = os.path.join(temp_spectra_folder, filename)
            
            # Generate realistic spectral data
            if irr_type == 'ALB':
                # Albedo values between 0-1
                values = np.full(len(wavelengths), 0.2)  # Simple constant albedo
            elif irr_type == 'DNI':
                values = np.full(len(wavelengths), 800.0)  # Constant DNI
            elif irr_type == 'DHI':
                values = np.full(len(wavelengths), 200.0)  # Constant DHI
            elif irr_type == 'GHI':
                values = np.full(len(wavelengths), 1000.0)  # Constant GHI
            
            # Create DataFrame with proper format
            spectral_df = pd.DataFrame({
                'wavelength': wavelengths,
                'value': values
            })
            
            # Write file with header (first line is metadata, then CSV data)
            with open(filepath, 'w') as f:
                f.write("# Test spectral data\n")
                spectral_df.to_csv(f, index=False)
        
        # Test the integrated_spectrum function
        integrated_sums = integrated_spectrum(temp_spectra_folder, metdata)
        
        # Verify the results
        assert isinstance(integrated_sums, pd.DataFrame), "Should return a DataFrame"
        assert len(integrated_sums) == 1, "Should have 1 time entry"
        
        # Check that all expected columns are present
        expected_columns = ['Sum_DNI', 'Sum_DHI', 'Sum_DNI_ALB', 'Sum_DHI_ALB']
        for col in expected_columns:
            assert col in integrated_sums.columns, f"Missing column: {col}"
        
        # Verify values are positive and reasonable
        for col in expected_columns:
            assert integrated_sums[col].iloc[0] > 0, f"{col} should have positive values"
        
        # Check that DNI*ALB is less than DNI (since albedo = 0.2 < 1)
        assert integrated_sums['Sum_DNI_ALB'].iloc[0] < integrated_sums['Sum_DNI'].iloc[0], \
            "DNI*ALB should be less than DNI"
        
        # Check that DHI*ALB is less than DHI (since albedo = 0.2 < 1)
        assert integrated_sums['Sum_DHI_ALB'].iloc[0] < integrated_sums['Sum_DHI'].iloc[0], \
            "DHI*ALB should be less than DHI"
        
        # Check approximate expected values for constant spectra
        # Expected integration of constant 800 over wavelength range (280-4000) = 800 * (4000-280) = 2,976,000
        expected_dni = 800.0 * (4000 - 280)
        assert abs(integrated_sums['Sum_DNI'].iloc[0] - expected_dni) / expected_dni < 0.1, \
            f"DNI integration not as expected: got {integrated_sums['Sum_DNI'].iloc[0]}, expected ~{expected_dni}"
        
        print(f"✓ integrated_spectrum test passed")


def _other_cruft():
    # In[3]:
    
    
    # Improvements: 
    # Create new SPECTRA Folder on the Radiance Scene Folder to save spectras in automatically
    # Search for metdata internally if not passed
    # Start using timestamps instead of indexes
    # generate spectras and save values internally as part of the rad_obj ~ 
    # generate spectras for all indexes in metdata automatically (might take a while for the year if readWeatherFile is not restricted)
    # pySMARTS: interactive folder selectro to choose where Smarts executable is at, in case it doesn't find it in the Environment Variables
    
    
    # # 2) Call spectra for that timestamp
    
    # In[14]:
        
    
    wavelength = 700
    
    
    # In[ ]:
    
    
    # spectral_utils generates files with this suffix
    suffix = f'_{idx:04}.txt'
    
    # Load albedo
    alb_file = Path(spectra_folder, "alb"+suffix)
    spectral_alb = br.spectral_utils.spectral_property.load_file(alb_file)
    
    # Generate/Load dni and dhi
    dni_file = os.path.join(spectra_folder, "dni"+suffix)
    dhi_file = os.path.join(spectra_folder, "dhi"+suffix)
    ghi_file = os.path.join(spectra_folder, "ghi"+suffix)
    spectral_dni = br.spectral_utils.spectral_property.load_file(dni_file)
    spectral_dhi = br.spectral_utils.spectral_property.load_file(dhi_file)
    spectral_ghi = br.spectral_utils.spectral_property.load_file(ghi_file)
    
    alb = spectral_alb[wavelength]
    dni = spectral_dni[wavelength]
    dhi = spectral_dhi[wavelength]
    ghi = spectral_ghi[wavelength]
    
    rad_obj.setGround(alb) # this option is for spectral-albedo
    solpos = rad_obj.metdata.solpos.iloc[idx]
    zen = float(solpos.zenith)
    azm = float(solpos.azimuth) - 180
    rad_obj.gendaylit2manual(dni, dhi, 90 - zen, azm)
    
    sceneDict = {'tilt':tilt, 'pitch':0.0001, 'clearance_height':2.0,
                         'azimuth':180, 'nMods':1, 'nRows':1}
    sceneObj = rad_obj.makeScene(moduletype=module_type,sceneDict=sceneDict) 
    
    # Build oct file            
    octfile = rad_obj.makeOct(octname=f'Oct_{idx:04}')
    analysis = br.AnalysisObj(octfile, rad_obj.basename)  
    frontscan, backscan = analysis.moduleAnalysis(sceneObj, sensorsy=3)
    res_name = f'CenterRow_Center_{idx:04}'
    frontdict, backdict = analysis.analysis(octfile, res_name, frontscan, backscan)

