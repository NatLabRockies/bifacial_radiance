import numpy as np
import pandas as pd
from collections.abc import Iterable
import os
from scipy import integrate
from tqdm import tqdm
from pvlib import iotools
from bifacial_radiance import main as main


class spectral_property(object):
    """
    WRITE DOCSTRING HERE
    """
    
    def load_file(filepath):
        with open(filepath, 'r') as infile:
            meta = next(infile)[:-1]
            data = pd.read_csv(infile)
        
        return spectral_property(data['value'], data['wavelength'],
                                 interpolation=meta.split(':')[1])
    
    def to_nm(wavelength, units):
        unit_conversion = { 'nm': 1,
                            'um': 1000 }
        
        # Verify units are in conversion table
        if units not in unit_conversion:
            print("Warning: Unknown unit specified. Options are {}.".format(
                unit_conversion.keys()))
            units = 'nm'
            
        return wavelength * unit_conversion[units]
    
    def _linear_interpolation(self, wavelength_nm):
        # Find upper and lower index
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        # Determine values of surrounding indices
        upper_val = self.data['value'][upper_bound]
        lower_val = self.data['value'][lower_bound]
        
        # Calculate deltas
        delta_lambda = upper_bound - lower_bound
        delta_val = upper_val - lower_val
        
        return lower_val + delta_val*(wavelength_nm - lower_bound)/delta_lambda
    
    def _nearest_interpolation(self, wavelength_nm):
        # Find upper and lower index
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        # Determine which index is closer
        if (upper_bound - wavelength_nm) < (wavelength_nm - lower_bound):
            return self.data['value'][upper_bound]
        return self.data['value'][lower_bound]
    
    def _lower_interpolation(self, wavelength_nm):
        # Find lower index
        lower_bound = self.data[self.data.index < wavelength_nm].index.max()
        
        return self.data['value'][lower_bound]
    
    def _upper_interpolation(self, wavelength_nm):
        # Find upper index
        upper_bound = self.data[self.data.index > wavelength_nm].index.min()
        
        return self.data['value'][upper_bound]
    
    interpolation_methods = {
        'linear':   _linear_interpolation,
        'nearest':  _nearest_interpolation,
        'lower':    _lower_interpolation,
        'upper':    _upper_interpolation
    }
    
    def __init__(self, values, index, index_units='nm', interpolation=None):
        # Verify lengths match
        if len(values) != len(index):
            print("Warning: Length of values and index must match.")
            return
        
        # Convert inputs to list
        values = [ val for val in values ]
        index = [ spectral_property.to_nm(idx, index_units) for idx in index ]
        
        # Create DataFrame
        self.data = pd.DataFrame()
        self.data['value'] = values
        self.data['wavelength'] = index
        self.data = self.data.set_index('wavelength')
        
        self.interpolation = None
        if interpolation in spectral_property.interpolation_methods:
            self.interpolation = \
                    spectral_property.interpolation_methods[interpolation]
            self.interpolation_type = interpolation
        elif interpolation:
            print("Warning: Specified interpolation type unknown.")
            
    def _get_single(self, wavelength, units):
        # Convert wavelength to nm
        wavelength = spectral_property.to_nm(wavelength, units)
        
        if wavelength in self.data.index:
            # If the value for that wavelength is known, return it
            return self.data['value'][wavelength]
        elif self.interpolation:
            # Check wavelength is within range
            if wavelength < self.data.index.min() or \
               wavelength > self.data.index.max():
                print("Warning: Requested wavelength outside spectrum.")
                return None
            
            # Return interpolated value
            return self.interpolation(self, wavelength)
        
        return None
    
    def __getitem__(self, wavelength, units='nm'):
        if isinstance(wavelength, Iterable):
            return np.array([ self._get_single(wl, units) for wl in wavelength ])
        return self._get_single(wavelength, units)
    
    def to_file(self, filepath, append=False):
        mode = 'w'
        if append:
            mode = 'a'
            
        with open(filepath, mode) as outfile:
            outfile.write(f"interpolation:{self.interpolation_type}\n")
            self.data.to_csv(outfile)
    
    def range(self):
        # Find upper and lower index
        upper_bound = self.data.index.max()
        lower_bound = self.data.index.min()
        
        return (lower_bound, upper_bound)
    
    def scale_values(self, scaling_factor):
        self.data['value'] *= scaling_factor
    
def spectral_albedo_smarts(zen, azm, material, min_wavelength=300,
                           max_wavelength=4000):

    import pySMARTS
    
    smarts_res = pySMARTS.SMARTSSpectraZenAzm('30 31', str(zen), str(azm), material,
                                     min_wvl=str(min_wavelength),
                                     max_wvl=str(max_wavelength))
    
    return spectral_property(smarts_res['Local_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')

def spectral_irradiance_smarts(zen, azm, material='LiteSoil', min_wavelength=300,
                           max_wavelength=4000):

    import pySMARTS

    try:
        smarts_res = pySMARTS.SMARTSSpectraZenAzm('2 3 4', str(zen), str(azm),
                                     material=material,
                                     min_wvl=str(min_wavelength),
                                     max_wvl=str(max_wavelength))
    except PermissionError as e:
        msg = "{}".format(e)
        raise PermissionError(msg + "  Error accessing SMARTS. Make sure you have "
              "SMARTS installed in a directory that you have read/write privileges for. ")

    
    dni_spectrum = spectral_property(smarts_res['Direct_normal_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res['Difuse_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res['Global_horizn_irradiance'],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_irradiance_smarts_SRRL(YEAR, MONTH, DAY, HOUR, ZONE,
                                LATIT, LONGIT, ALTIT,
                                RH, TAIR, SEASON, TDAY, SPR, W,
                                TILT, WAZIM, HEIGHT,
                                ALPHA1, ALPHA2, OMEGL, GG, BETA, TAU5,
                                RHOG, material,
                                IOUT='2 3 4', min_wvl='280', max_wvl='4000'):
    
    import pySMARTS

    smarts_res = pySMARTS.SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, ZONE=ZONE,
                            LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                             RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, W=W, 
                             TILT=TILT, WAZIM=WAZIM, HEIGHT=HEIGHT,
                             ALPHA1 = ALPHA1, ALPHA2 = ALPHA2, OMEGL = OMEGL,
                             GG = GG, BETA = BETA, TAU5= TAU5, 
                             RHOG=RHOG, material=material, 
                             min_wvl=min_wvl, max_wvl=max_wvl)
    

    dni_spectrum = spectral_property(smarts_res[smarts_res.keys()[1]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    dhi_spectrum = spectral_property(smarts_res[smarts_res.keys()[2]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    ghi_spectrum = spectral_property(smarts_res[smarts_res.keys()[3]],
                                     smarts_res['Wvlgth'], interpolation='linear')
    
    return (dni_spectrum, dhi_spectrum, ghi_spectrum)



def spectral_albedo_smarts_SRRL(YEAR, MONTH, DAY, HOUR, ZONE,
                                LATIT, LONGIT, ALTIT,
                                RH, TAIR, SEASON, TDAY, SPR, W,
                                TILT, WAZIM, HEIGHT, 
                                ALPHA1, ALPHA2, OMEGL, GG, BETA, TAU5,
                                RHOG, material,
                                IOUT='30 31', min_wvl='280', max_wvl='4000'):
 
    import pySMARTS

    smarts_res = pySMARTS.SMARTSSRRL(IOUT=IOUT, YEAR=YEAR,MONTH=MONTH,DAY=DAY,HOUR=HOUR, ZONE=ZONE,
                            LATIT=LATIT, LONGIT=LONGIT, ALTIT=ALTIT, 
                             RH=RH, TAIR=TAIR, SEASON=SEASON, TDAY=TDAY, SPR=SPR, W=W, 
                             TILT=TILT, WAZIM=WAZIM, HEIGHT=HEIGHT,
                             ALPHA1 = ALPHA1, ALPHA2 = ALPHA2, OMEGL = OMEGL,
                             GG = GG, BETA = BETA, TAU5= TAU5,
                             RHOG=RHOG, material=material, 
                             min_wvl=min_wvl, max_wvl=max_wvl)
    
    return spectral_property(smarts_res['Local_ground_reflectance'],
                             smarts_res['Wvlgth'], interpolation='linear')
   

def generate_spectra(metdata, simulation_path, ground_material='Gravel', spectra_folder=None, scale_spectra=False,
                     scale_albedo=False, scale_albedo_nonspectral_sim=False, scale_upper_bound=2500, min_wavelength=280, max_wavelength=4000):
    """
    generate spectral curve for particular material.  Requires pySMARTS 

    Parameters
    ----------
    metdata : bifacial_radiance MetObj
        MetObj containing weather data, with a datetime index.
    simulation_path: string or path
        path of simulation directory
    ground_material : string, optional
        type of ground material for spectral simulation. Options include:
        Grass, Gravel, Snow, Seasonal etc.
        The default is 'Gravel'.
    spectra_folder : path, optional
        location to save spectral data. The default is None.
    scale_spectra : bool, optional
        DESCRIPTION. The default is False.
    scale_albedo : bool, optional
        DESCRIPTION. The default is False.
    scale_albedo_nonspectral_sim : bool, optional
        DESCRIPTION. The default is False.
    scale_upper_bound: integer, optional
        Set an upper bound for the wavelength when taking the mean
        or integral of any generated spectra. 

    Returns
    -------
    spectral_alb : spectral_property class
        spectral_alb.data:  dataframe with frequency and magnitude data.
    spectral_dni : spectral_property class
        spectral_dni.data:  dataframe with frequency and magnitude data.
    spectral_dhi : spectral_property class
        spectral_dhi.data:  dataframe with frequency and magnitude data.
    weighted_alb : pd.series
        datetime-indexed series of weighted albedo values

    """

    # make the datetime easily readable and indexed
    dts = pd.Series(data=metdata.datetime)

    # weighted albedo data frame
    walb = pd.Series(index=np.array(metdata.datetime),dtype='float64')

    # print useful reminders
    if scale_albedo_nonspectral_sim:
        print(' -= Non-Spectral Simulation =- \n Spectra files will NOT be saved.')
    else:
        print(' -=   Spectral Simulation   =- \n Spectra files will be saved.')

    for dt in tqdm(dts,ncols=100,desc='Generating Spectra'):

        # scrape all the necessary metadata
        idx = dts.index[dts==dt][0]
        dni = metdata.dni[idx]
        dhi = metdata.dhi[idx]
        ghi = metdata.ghi[idx]
        if metdata.albedo is not None:
            alb = metdata.albedo[idx]
        else:
            alb = 0.2
        solpos = metdata.solpos.iloc[idx]
        zen = float(solpos.zenith)
        azm = float(solpos.azimuth) - 180
        lat = metdata.latitude

        # create file names
        suffix = f'_{str(dt.year)[-2:]}_{dt.month:02}_{dt.day:02}_{dt.hour:02}_{dt.minute:02}.txt'
        dni_file = os.path.join(simulation_path, spectra_folder, "dni"+suffix)
        dhi_file = os.path.join(simulation_path, spectra_folder, "dhi"+suffix)
        ghi_file = os.path.join(simulation_path, spectra_folder, "ghi"+suffix)
        alb_file = os.path.join(simulation_path, spectra_folder, "alb"+suffix)
        
        # generate the base spectra
        try:
            spectral_dni, spectral_dhi, spectral_ghi = spectral_irradiance_smarts(zen, azm, min_wavelength=min_wavelength, max_wavelength=max_wavelength)
        except:
            if scale_albedo_nonspectral_sim:
                walb[dt] = 0.0
            continue

        # limit dataframes for calculations by scaling upper bound
        tdni = spectral_dni.data[spectral_dni.data.index <= scale_upper_bound]
        tdhi = spectral_dhi.data[spectral_dhi.data.index <= scale_upper_bound]
        tghi = spectral_ghi.data[spectral_ghi.data.index <= scale_upper_bound]
        
        # scaling spectra
        if scale_spectra:
            dni_scale = dni / integrate.trapezoid(tdni.value, x=tdni.index)
            dhi_scale = dhi / integrate.trapezoid(tdhi.value, x=tdhi.index)
            ghi_scale = ghi / integrate.trapezoid(tghi.value, x=tghi.index)
            spectral_dni.scale_values(dni_scale)
            spectral_dhi.scale_values(dhi_scale)
            spectral_ghi.scale_values(ghi_scale)

        # Determine Seasonal ground cover, if necessary
        north = [1,2,3,4,10,11,12]
        south = [5,6,7,8,9,10]
        if lat < 0: winter = north
        if lat > 0: winter = south

        if ground_material == 'Seasonal':
            MONTH = metdata.datetime[idx].month
            if MONTH in winter :
                if alb >= 0.6:
                    ground_material = 'Snow'
                else:
                    ground_material = 'DryGrass'
            else:
                ground_material = 'Grass'

        # Generate base spectral albedo
        spectral_alb = spectral_albedo_smarts(zen, azm, ground_material, min_wavelength=280)
        
        # Limit albedo by upper bound wavelength
        talb = spectral_alb.data[spectral_alb.data.index <= scale_upper_bound]

        # scaling albedo
        if scale_albedo:
            #***
            # Currently using simple scaling model (scale by mean)
            #***
            denom = talb.values.mean()
            scale_factor = alb / denom
            spectral_alb.scale_values(scale_factor)

        # If performing a non-spectral simulation, generate single albedo weighted by spectra
        if scale_albedo_nonspectral_sim:        
            #SR = SR[SR.index <= scale_upper_bound] # placeholder for Spectral Responsivity
            num = talb * tghi #* SR
            num = integrate.trapezoid(num.value, x=num.index)
            denom = tghi #* SR
            denom = integrate.trapezoid(denom.value, x=denom.index)
            alb_weighted = num / denom
            
            walb[dt] = alb_weighted
            
        # only save the files if performing a spectral simulation
        if not scale_albedo_nonspectral_sim:
            spectral_alb.to_file(alb_file)
            spectral_dhi.to_file(dhi_file)
            spectral_dni.to_file(dni_file)
            spectral_ghi.to_file(ghi_file)       
    
    # save a basic csv of weighted albedo, indexed by datetime
    if scale_albedo_nonspectral_sim:        
        walbPath = os.path.join(simulation_path,spectra_folder,'albedo_scaled_nonSpec.csv')
        walb.to_csv(walbPath)
        print('Weighted albedo CSV saved.')
        weighted_alb = walb
        return (spectral_alb, spectral_dni, spectral_dhi, weighted_alb)    
    
    return (spectral_alb, spectral_dni, spectral_dhi, None)

def generate_spectral_tmys(wavelengths, spectra_folder, metdata, location_name, output_folder):
    """
    Generate a series of TMY-like files with per-wavelength irradiance. There will be one file per 
    wavelength. These are necessary to run a spectral simulation with gencumsky
    
    Paramters:
    ----------
    wavelengths: (np.array or list)
        array or list of integer wavelengths to simulate, in units [nm]. example: [300,325,350]
    spectra_folder: (path or str)
        File path or path-like string pointing to the folder contained the SMARTS generated spectra
    metdata: pandas DataFrame
        DataFrame containing the weather data, with a datetime index.
    location_name: 
        _description_
    output_folder: 
        File path or path-like string pointing to the destination folder for spectral TMYs
    """

    # -- read in the spectra files
    spectra_files = next(os.walk(spectra_folder))[2]
    spectra_files.sort()

    # -- read in the weather file and format
    #(tmydata, metdata) = main.RadianceObj.readWeatherFile(weatherFile=weather_file, coerce_year=2021)
    #(tmydata, metdata) = iotools.read_tmy3(weather_file, coerce_year=2021)
    tmydata = metdata.tmydata.copy()
    #tmydata.index = tmydata.index+pd.Timedelta(hours=1)
    tmydata.rename(columns={'dni':'DNI',
                            'dhi':'DHI',
                            'temp_air':'DryBulb',
                            'wind_speed':'Wspd',
                            'ghi':'GHI',
                            'relative_humidity':'RH',
                            'albedo':'Alb'
                            }, inplace=True)
    dtindex = tmydata.index

    # -- grab the weather file header to reproduce location meta-data
    # with open(weather_file, 'r') as wf:
    #     header = wf.readline()
    header = metdata.metadata.copy()
    
    # -- read in a spectra file to copy wavelength-index
    temp = pd.read_csv(os.path.join(spectra_folder,spectra_files[0]), header=1, index_col = 0)

    # -- copy and reproduce the datetime index
    dates = []
    for file in spectra_files:
        take = file[4:-4]
        if take not in dates:
            dates.append(take)
    dates = pd.to_datetime(dates,format='%y_%m_%d_%H_%M').tz_localize(dtindex.tz)

    # -- create a multi-index of columns [timeindex:alb,dni,dhi,ghi]
    iterables = [dates,['ALB','DHI','DNI','GHI']]
    multi_index = pd.MultiIndex.from_product(iterables, names=['time_index','irr_type'])

    # -- create empty dataframe
    spectra_df = pd.DataFrame(index=temp.index,columns=multi_index)

    # -- fill with irradiance data
    for file in spectra_files:
        a = pd.to_datetime(file[4:-4],format='%y_%m_%d_%H_%M').tz_localize(dtindex.tz)
        b = file[:3].upper()
        spectra_df[a,b] = pd.read_csv(os.path.join(spectra_folder,file),header=1, index_col=0)

    # -- reorder the columns to match TMYs
    spectra_df.columns.set_levels(['Alb','DHI','DNI','GHI'],level=1)
    # -- create arrays of zeros for data outside the array
    zeros = np.zeros(len(dtindex))

    # -- build the blank tmy-like data frame
    blank_df = pd.DataFrame(index=dtindex, data={'Date (MM/DD/YYYY)':dtindex.strftime('%#m/%#d/%Y'),
                                                'Time (HH:MM)':dtindex.strftime('%H:%M'),
                                                'Wspd':tmydata['Wspd'],'Dry-bulb':tmydata['DryBulb'],
                                                'DHI':zeros,'DNI':zeros,'GHI':zeros,'ALB':zeros})

    # column names for transfer
    irrs = ['DNI','DHI','GHI','ALB']

    # -- grab data, save file
    for wave in tqdm(wavelengths, ncols=100, desc='Generating Spectral TMYs'):
        fileName = f'{location_name}_TMY_w{wave:04}.csv'
        fileName = os.path.join(output_folder,fileName)
        wave_df = blank_df.copy()
        for col in spectra_df.columns:
            wave_df.loc[col[0],col[1]] = spectra_df[col].loc[wave]
        
        with open(fileName, 'w', newline='') as ict:
            # for line in header:
            #     ict.write(line)
            wave_df.to_csv(ict, index=False)


def integrated_spectrum(spectra_folder, metdata ):
    """
    Generate integrated sums across the full spectra
    
    Paramters:
    ----------
    spectra_folder: (path or str)
        File path or path-like string pointing to the folder contained the SMARTS generated spectra
    metdata: pandas DataFrame
        DataFrame containing the weather data, with a datetime index.
        

    Returns:
    -------
    integrated_sums: (list)
        list of integrated sums for DNI, DHI, DNI*ALB, DHI*ALB
    """

    # -- read in the spectra files
    spectra_files = next(os.walk(spectra_folder))[2]
    spectra_files.sort()

    # -- read in the weather file and format
    #(tmydata, metdata) = main.RadianceObj.readWeatherFile(weatherFile=weather_file, coerce_year=2021)
    #(tmydata, metdata) = iotools.read_tmy3(weather_file, coerce_year=2021)
    tmydata = metdata.tmydata.copy()
    #tmydata.index = tmydata.index+pd.Timedelta(hours=1)
    tmydata.rename(columns={'dni':'DNI',
                            'dhi':'DHI',
                            'temp_air':'DryBulb',
                            'wind_speed':'Wspd',
                            'ghi':'GHI',
                            'relative_humidity':'RH',
                            'albedo':'Alb'
                            }, inplace=True)
    dtindex = tmydata.index

    # -- grab the weather file header to reproduce location meta-data
    # with open(weather_file, 'r') as wf:
    #     header = wf.readline()
    header = metdata.metadata.copy()
    
    # -- read in a spectra file to copy wavelength-index
    temp = pd.read_csv(os.path.join(spectra_folder,spectra_files[0]), header=1, index_col = 0)

    # -- copy and reproduce the datetime index
    dates = []
    for file in spectra_files:
        take = file[4:-4]
        if take not in dates:
            dates.append(take)
    dates = pd.to_datetime(dates,format='%y_%m_%d_%H_%M').tz_localize(dtindex.tz)

    # -- create a multi-index of columns [timeindex:alb,dni,dhi,ghi]
    iterables = [dates,['ALB','DHI','DNI','GHI']]
    multi_index = pd.MultiIndex.from_product(iterables, names=['time_index','irr_type'])

    # -- create empty dataframe
    spectra_df = pd.DataFrame(index=temp.index,columns=multi_index)
     # -- fill with irradiance data
    for file in spectra_files:
        a = pd.to_datetime(file[4:-4],format='%y_%m_%d_%H_%M').tz_localize(dtindex.tz)
        b = file[:3].upper()
        spectra_df[a,b] = pd.read_csv(os.path.join(spectra_folder,file),header=1, index_col=0)
    integrated_sums = pd.DataFrame(index=dates, columns=['Sum_DNI', 'Sum_DHI', 'Sum_DNI_ALB', 'Sum_DHI_ALB'])
    for col in spectra_df.columns:
        integrated_sums.loc[col[0], 'Sum_DNI'] = integrate.trapezoid(spectra_df[col[0], 'DNI'], spectra_df.index)
        integrated_sums.loc[col[0], 'Sum_DHI'] = integrate.trapezoid(spectra_df[col[0], 'DHI'], spectra_df.index)
        integrated_sums.loc[col[0], 'Sum_DNI_ALB'] = integrate.trapezoid(spectra_df[col[0], 'DNI'] * spectra_df[col[0], 'ALB'], spectra_df.index)
        integrated_sums.loc[col[0], 'Sum_DHI_ALB'] = integrate.trapezoid(spectra_df[col[0], 'DHI'] * spectra_df[col[0], 'ALB'], spectra_df.index)

    return integrated_sums
    
    
