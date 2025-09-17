# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 20:16:47 2019

@author: sayala
"""

from deprecated import deprecated



def _sensorupsampletocellsbyInterpolation(df, cellsy):
    '''
        
    Function for when sensorsy in the results are less than cellsy desired.
    Interpolates the dataframe.
    
    #2DO: improve interpolation with pandas. right onw it's row by row.
    
    _sensorupsampletocellsbyInterpolation(df, cellsy)
    '''
    
    import pandas as pd
    import numpy as np
    
    sensorsy = len(df)
    
    #2DO: Update this section to match bifacialvf
    cellCenterPVM=[]                                    
    for i in range (0, cellsy):
        cellCenterPVM.append((i*sensorsy/cellsy+(i+1)*sensorsy/cellsy)/2)
    
    df2 = pd.DataFrame()
    for j in range (0, len(df.keys())):
        A = list(df[df.keys()[j]])
        B= np.interp(cellCenterPVM, list(range(0,sensorsy)), A)
        df2[df.keys()[j]]=B
    
    return df2
    
def _sensorsdownsampletocellsbyAverage(df, cellsy):
    '''
    df = dataframe with rows indexed by number (i.e. 0 to sensorsy) where sensorsy > cellsy
    cellsy = int. usually 8 or 12.

    example:
    F_centeraverages = _sensorsdownsampletocellsbyAverage(F, cellsy)
    '''
    import numpy as np
    import pandas as pd

    edges=len(df)-np.floor(len(df)/(cellsy))*(cellsy)
    edge1=int(np.floor(edges/2))
    edge2=int(edges-edge1)
    A = list(range(df.index[0]+edge1, df.index[-1]-edge2+2, int(np.floor(len(df)/(cellsy)))))
    B = range(0,len(A)-1,1)
    C = [df.iloc[A[x]:A[x+1]].mean(axis=0) for x in B]
    df_centeraverages=pd.DataFrame(C)
    
    return df_centeraverages

def _sensorsdownsampletocellbyCenter(df, cellsy):
    '''
    df = dataframe with rows indexed by number (i.e. 0 to sensorsy) where sensorsy > cellsy
    cellsy = int. usually 8 or 12.

    example:
    F_centervalues = _sensorsdownsampletocellbyCenter(F, cellsy)
    '''

    import numpy as np

    
    edges=len(df)-np.floor(len(df)/(cellsy))*(cellsy)
    edge1=int(np.floor(edges/2))
    edge2=int(edges-edge1)
    A = list(range(df.index[0]+edge1, df.index[-1]-edge2+2, int(np.floor(len(df)/(cellsy)))))
    A = [int(x+(A[1]-A[0])*0.5) for x in A]
    A = A[:-1]
    df_centervalues=df.loc[A]
    df_centervalues=df_centervalues.reset_index(drop=True)
    
    return df_centervalues
    
def _setupforPVMismatch(portraitorlandscape, sensorsy, numcells=72):
    r''' Sets values for calling PVMismatch, for ladscape or portrait modes and 
    
    Example:
    stdpl, cellsx, cellsy = _setupforPVMismatch(portraitorlandscape='portrait', sensorsy=100):
    '''

    import numpy as np

        # cell placement for 'portrait'.
    if numcells == 72:
        stdpl=np.array([[0,	23,	24,	47,	48,	71],
        [1,	22,	25,	46,	49,	70],
        [2,	21,	26,	45,	50,	69],
        [3,	20,	27,	44,	51,	68],
        [4,	19,	28,	43,	52,	67],
        [5,	18,	29,	42,	53,	66],
        [6,	17,	30,	41,	54,	65],
        [7,	16,	31,	40,	55,	64],
        [8,	15,	32,	39,	56,	63],
        [9,	14,	33,	38,	57,	62],
        [10,	13,	34,	37,	58,	61],
        [11,	12,	35,	36,	59,	60]])
    
    elif numcells == 96:
        stdpl=np.array([[0,	23,	24,	47,	48,	71,	72,	95],
            [1,	22,	25,	46,	49,	70,	73,	94],
            [2,	21,	26,	45,	50,	69,	74,	93],
            [3,	20,	27,	44,	51,	68,	75,	92],
            [4,	19,	28,	43,	52,	67,	76,	91],
            [5,	18,	29,	42,	53,	66,	77,	90],
            [6,	17,	30,	41,	54,	65,	78,	89],
            [7,	16,	31,	40,	55,	64,	79,	88],
            [8,	15,	32,	39,	56,	63,	80,	87],
            [9,	14,	33,	38,	57,	62,	81,	86],
            [10,	13,	34,	37,	58,	61,	82,	85],
            [11,	12,	35,	36,	59,	60,	83,	84]])
    else:
        print("Error. Only 72 and 96 cells modules supported at the moment. Change numcells to either of this options!")
        return
    
    if portraitorlandscape == 'landscape':
        stdpl = stdpl.transpose()
    elif portraitorlandscape != 'portrait':
        print("Error. portraitorlandscape variable must either be 'landscape' or 'portrait'")
        return
    
    cellsx = len(stdpl[1]); cellsy = len(stdpl)
    
    return stdpl, cellsx, cellsy


def calculatePVMismatch(pvsys, stdpl, cellsx, cellsy, Gpoat):
    r''' calls PVMismatch with all the pre-generated values on bifacial_radiance
    
    Example:
    PowerAveraged, PowerDetailed = def calculatePVMismatch(pvsys, stdpl, cellsx, cellsy, Gpoat)

    '''

    import numpy as np
    
    if np.mean(Gpoat) < 0.001:
        PowerAveraged = 0
        PowerDetailed = 0
    else:                                   
        # makes the system  # 1 module, in portrait mode.         
        G=np.array([Gpoat]).transpose()
        H = np.ones([1,cellsx]) 
        array_det = np.dot(G,H) 
        array_avg = np.ones([cellsy,cellsx])*np.mean(Gpoat)        
                                
        # ACtually do calculations
        pvsys.setSuns({0: {0: [array_avg, stdpl]}})
        PowerAveraged=pvsys.Pmp
        
        pvsys.setSuns({0: {0: [array_det, stdpl]}})
        PowerDetailed=pvsys.Pmp

    return PowerAveraged, PowerDetailed

def mismatch_fit3(data):
    '''
    Electrical mismatch calculation following Progress in PV paper
    Estimating and parameterizing mismatch power loss in bifacial photovoltaic systems
    Chris Deline, Silvana Ayala Pelaez,Sara MacAlpine,Carlos Olalla
    https://doi.org/10.1002/pip.3259

    .. deprecated:: 0.4.3
       This fitted model is deprecated in favor of :func:`mismatch_fit2` which has
       better agreement with the experimental data.
    
    Parameters
    ----------
    data : np.ndarray, pd.Series, pd.DataFrame
        Gtotal irradiance measurements. Each column is the irradiance for a module
        at a specific time. 

    Returns
    -------
    fit3 :  Float or pd.Series
        Returns mismatch values for each module in percentage [%].
    
    Equation: 1/(n^2*Gavg)*Sum Sum (abs(G_i - G_j))
    ## Note: starting with Pandas 1.0.0 this function will not work on Series objects.
    '''
    import numpy as np
    import pandas as pd
    
    if type(data) == np.ndarray:
        data = pd.DataFrame(data)
    
    datac = data[~np.isnan(data)]
    mad = mad_fn(datac)  # (percentage)
    mad2 = mad**2
    
    fit3 = 0.054*mad + 0.068*mad2
    
    if fit3.__len__() == 1:
        if isinstance(fit3, pd.Series):
            fit3 = float(fit3.iloc[0])
        else:
            fit3 = float(fit3)

    return fit3


def mismatch_fit2(data):
    '''
    Electrical mismatch calculation following Progress in PV paper
    Estimating and parameterizing mismatch power loss in bifacial photovoltaic systems
    Chris Deline, Silvana Ayala Pelaez,Sara MacAlpine,Carlos Olalla
    https://doi.org/10.1002/pip.3259
    
    Parameters
    ----------
    data : np.ndarray, pd.Series, pd.DataFrame
        Gtotal irradiance measurements. Each column is the irradiance for a module
        at a specific time. 

    Returns
    -------
    fit2 :  Float or pd.Series
        Returns mismatch values for each module in percentage [%].
    
    Equation: 1/(n^2*Gavg)*Sum Sum (abs(G_i - G_j))
    ## Note: starting with Pandas 1.0.0 this function will not work on Series objects.
    '''
    import numpy as np
    import pandas as pd
    
    if type(data) == np.ndarray:
        data = pd.DataFrame(data)
    
    datac = data[~np.isnan(data)]
    mad = mad_fn(datac)  # (percentage)
    mad2 = mad**2
    
    fit2 = 0.142*mad + 0.032*mad2
    
    if fit2.__len__() == 1:
        if isinstance(fit2, pd.Series):
            fit2 = float(fit2.iloc[0])
        else:
            fit2 = float(fit2)

    return fit2

    
def mad_fn(data, axis='index'):
    '''
    Mean average deviation calculation for mismatch purposes.
    
    Parameters
    ----------
    data : np.ndarray or pd.Series or pd.DataFrame
        Gtotal irradiance measurements. If data is a pandas.DataFrame, one 
        MAD/Average is returned for each index, based on values across columns.
        
    axis : {0 or 'index', 1 or 'columns'}, default 'index'   
        Calculate mean average deviation across rows (default) or columns for 2D data

        * 0, or 'index' : MAD calculated across rows.
        * 1, or 'columns' : MAD calculated across columns.
    Returns
    -------
    scalar or pd.Series:   return MAD / Average [%]. Scalar for a 1D array, Series for 2D.
    
    
    Equation: 1/(n^2*Gavg)*Sum Sum (abs(G_i - G_j)) * 100[%]

    '''
    import numpy as np
    import pandas as pd
    def _mad_1D(data):  #1D calculation of MAD
        return (np.abs(np.subtract.outer(data,data)).sum()/float(data.__len__())**2 / np.mean(data))*100
    if type(axis) == str:
        try:
            axis = {"index": 0, "rows": 0, 'columns':1}[axis]
        except KeyError:
            raise Exception('Incorrect index string in mad_fn. options: index, rows, columns.')
            
    ndim = data.ndim
    if ndim == 2 and axis==0:
        data = data.T
    # Pandas returns a notimplemented error if this is a DataFrame.
    if (type(data) == pd.Series):
        data = data.to_numpy()
    
    if type(data) == pd.DataFrame:
        temp = data.apply(pd.Series.to_numpy, axis=1)
        return(temp.apply(_mad_1D))
    elif ndim ==2: #2D array
        return [_mad_1D(i) for i in data]
    else:
        return _mad_1D(data)


@deprecated(reason='This analysis script will be moved to its own tutorial' +\
            ' file in a future release.', version='0.5.0')
def analysisIrradianceandPowerMismatch(testfolder, writefiletitle, portraitorlandscape, bififactor, numcells=72, downsamplingmethod='byCenter'):
    r'''
    Use this when sensorsy calculated with bifacial_radiance > cellsy
    
    Reads and calculates power output and mismatch for each file in the 
    testfolder where all the bifacial_radiance irradiance results .csv are saved.
    First load each file, cleans it and resamples it to the numsensors set in this function,
    and then calculates irradiance mismatch and PVMismatch power output for averaged, minimum,
    or detailed irradiances on each cell for the cases of A) only 12 or 8 downsmaples values are
    considered (at the center of each cell), and B) 12 or 8 values are obtained from averaging
    all the irradiances falling in the area of the cell (No edges or inter-cell spacing are considered
    at this moment). Then it saves all the A and B irradiances, as well as the cleaned/resampled
    front and rear irradiances.
    
    Ideally sensorsy in the read data is >> 12 to give results for the irradiance mismatch in the cell.
    
    Also ideally n
     
    Parameters
    ----------
    testfolder:   folder containing output .csv files for bifacial_radiance
    writefiletitle:   .csv title where the output results will be saved. 
    portraitorlandscape: 'portrait' or 'landscape', for PVMismatch input
                      which defines the electrical interconnects inside the module. 
    bififactor: bifaciality factor of the module. Max 1.0. ALL Rear irradiance values saved include the bifi-factor.
    downsampling method: 1 - 'byCenter' - 2 - 'byAverage'
    
    Example:
        
    # User information.
    import bifacial_radiance
    testfolder=r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\results'
    writefiletitle= r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\HPC Tracking Results\RICHMOND\Bifacial_Radiance Results\PVPMC_0\test_df.csv'
    sensorsy=100
    portraitorlandscape = 'portrait'
    analysis.analysisIrradianceandPowerMismatch(testfolder, writefiletitle, portraitorlandscape, bififactor=1.0, numcells=72)

    '''
    from bifacial_radiance import load
    import os, glob
    import pandas as pd
        
    # Default variables 
    numpanels=1 # 1 at the moment, necessary for the cleaning routine.
    automatic=True
    
    #loadandclean
    # testfolder = r'C:\Users\sayala\Documents\HPC_Scratch\EUPVSEC\PinPV_Bifacial_Radiance_Runs\HPCResults\df4_FixedTilt\FixedTilt_Cairo_C_0.15\results'
    filelist = sorted(os.listdir(testfolder)) 
    #filelist = sorted(glob.glob(os.path.join('testfolder','*.csv'))) 
    print('{} files in the directory'.format(filelist.__len__()))

    # Check number of sensors on data.
    temp = load.read1Result(os.path.join(testfolder,filelist[0]))
    sensorsy = len(temp)

    # Setup PVMismatch parameters
    stdpl, cellsx, cellsy = _setupforPVMismatch(portraitorlandscape=portraitorlandscape, sensorsy=sensorsy, numcells=numcells)

    F=pd.DataFrame()
    B=pd.DataFrame()
    for z in range(0, filelist.__len__()):
            data=load.read1Result(os.path.join(testfolder,filelist[z]))
            [frontres, backres] = load.deepcleanResult(data, sensorsy=sensorsy, numpanels=numpanels, automatic=automatic)
            F[filelist[z]]=frontres
            B[filelist[z]]=backres          

    B = B*bififactor
    # Downsample routines:
    if sensorsy > cellsy:
        if downsamplingmethod == 'byCenter':
            print("Sensors y > cellsy; Downsampling data by finding CellCenter method")
            F = _sensorsdownsampletocellbyCenter(F, cellsy)
            B = _sensorsdownsampletocellbyCenter(B, cellsy)
        elif downsamplingmethod == 'byAverage':
            print("Sensors y > cellsy; Downsampling data by Averaging data into Cells method")
            F = _sensorsdownsampletocellsbyAverage(F, cellsy)
            B = _sensorsdownsampletocellsbyAverage(B, cellsy)
        else:
            print ("Sensors y > cellsy for your module. Select a proper downsampling method ('byCenter', or 'byAverage')")
            return
    elif sensorsy < cellsy:
        print("Sensors y < cellsy; Upsampling data by Interpolation")
        F = _sensorupsampletocellsbyInterpolation(F, cellsy)
        B = _sensorupsampletocellsbyInterpolation(B, cellsy)
    elif sensorsy == cellsy:
        print ("Same number of sensorsy and cellsy for your module.")
        F = F
        B = B

    # Calculate POATs
    Poat = F+B
            
    # Define arrays to fill in:
    Pavg_all=[]; Pdet_all=[]
    Pavg_front_all=[]; Pdet_front_all=[]
    colkeys = F.keys()
    
    import pvmismatch
    
    if cellsx*cellsy == 72:
        cell_pos = pvmismatch.pvmismatch_lib.pvmodule.STD72
    elif cellsx*cellsy == 96:
        cell_pos = pvmismatch.pvmismatch_lib.pvmodule.STD96
    else:
        print("Error. Only 72 and 96 cells modules supported at the moment. Change numcells to either of this options!")
        return
    
    pvmod=pvmismatch.pvmismatch_lib.pvmodule.PVmodule(cell_pos=cell_pos)        
    pvsys = pvmismatch.pvsystem.PVsystem(numberStrs=1, numberMods=1, pvmods=pvmod)  


    # Calculate powers for each hour:
    for i in range(0,len(colkeys)):        
        Pavg, Pdet = calculatePVMismatch(pvsys = pvsys, stdpl=stdpl, cellsx=cellsx, cellsy=cellsy, Gpoat=list(Poat[colkeys[i]]/1000))
        Pavg_front, Pdet_front = calculatePVMismatch(pvsys = pvsys, stdpl = stdpl, cellsx = cellsx, cellsy = cellsy, Gpoat= list(F[colkeys[i]]/1000))
        Pavg_all.append(Pavg)
        Pdet_all.append(Pdet)
        Pavg_front_all.append(Pavg_front) 
        Pdet_front_all.append(Pdet_front)
    
    ## Rename Rows and save dataframe and outputs.
    F.index='FrontIrradiance_cell_'+F.index.astype(str)
    B.index='BackIrradiance_cell_'+B.index.astype(str)
    Poat.index='POAT_Irradiance_cell_'+Poat.index.astype(str)

    # Statistics Calculatoins
    dfst=pd.DataFrame()
    dfst['MAD/G_Total'] = mad_fn(Poat)
    dfst['Front_MAD/G_Total'] = mad_fn(F)
    dfst['MAD/G_Total**2'] = dfst['MAD/G_Total']**2
    dfst['Front_MAD/G_Total**2'] = dfst['Front_MAD/G_Total']**2
    dfst['poat'] = Poat.mean()
    dfst['gfront'] = F.mean()
    dfst['grear'] = B.mean()
    dfst['bifi_ratio'] =  dfst['grear']/dfst['gfront']
    dfst['stdev'] = Poat.std()/ dfst['poat']
    dfst.index=Poat.columns.astype(str)

    # Power Calculations/Saving
    Pout=pd.DataFrame()
    Pout['Pavg']=Pavg_all
    Pout['Pdet']=Pdet_all
    Pout['Front_Pavg']=Pavg_front_all
    Pout['Front_Pdet']=Pdet_front_all
    Pout['Mismatch_rel'] = 100-(Pout['Pdet']*100/Pout['Pavg'])
    Pout['Front_Mismatch_rel'] = 100-(Pout['Front_Pdet']*100/Pout['Front_Pavg'])   
    Pout.index=Poat.columns.astype(str)

    ## Save CSV as one long row
    df_all = pd.concat([Pout, dfst, Poat.T, F.T, B.T], axis=1)
    df_all.to_csv(writefiletitle)
    print("Saved Results to ", writefiletitle)
    

    
        
