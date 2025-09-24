# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 15:48:21 2021

@author: sayala
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:39:39 2019

@author: sayala
"""

#import bifacial_radiance
#from   bifacial_radiance.config import *
#import os

# DATA_PATH = bifacial_radiance.main.DATA_PATH  # directory with module.json etc.

def _append_dicts(x, y):
    """python2 compatible way to append 2 dictionaries
    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def runModelChain(simulationParamsDict, sceneParamsDict, timeControlParamsDict=None, 
                  moduleParamsDict=None, trackingParamsDict=None, torquetubeParamsDict=None, 
                  analysisParamsDict=None, cellModuleDict=None, CECModParamsDict=None, 
                  frameParamsDict=None, omegaParamsDict=None, pilesParamsDict=None):
    """
    This calls config.py values, which are arranged into dictionaries,
    and runs all the respective processes based on the variables in the config.py.
 
    To import the variables from a .ini file, use::
        
        (simulationParamsDict, sceneParamsDict, timeControlParamsDict, moduleParamsDict, 
         trackingParamsDict,torquetubeParamsDict,analysisParamsDict,cellModuleDict,
         CECModParamsDict, frameParamsDict, omegaParamsDict, pilesParamsDict) = \
        bifacial_radiance.load.readconfigurationinputfile(inifile)
    
    """
    
    import bifacial_radiance
    import os
    import numpy as np
    import pandas as pd
    
    print("\nNew bifacial_radiance simulation starting. ")
    print("Version: ", bifacial_radiance.__version__)
    
    if not simulationParamsDict.get('testfolder'):
        simulationParamsDict['testfolder'] = bifacial_radiance.main._interactive_directory(
            title='Select or create an empty directory for the Radiance tree')

    testfolder = simulationParamsDict['testfolder']
    demo = bifacial_radiance.RadianceObj(
        simulationParamsDict['simulationname'], path=testfolder)  # Create a RadianceObj 'object'


    # Save INIFILE in folder
    inifilename = os.path.join(
        simulationParamsDict['testfolder'],  'simulation.ini')
    bifacial_radiance.load.savedictionariestoConfigurationIniFile(simulationParamsDict, sceneParamsDict, timeControlParamsDict,
                                                                  moduleParamsDict, trackingParamsDict, torquetubeParamsDict, analysisParamsDict, 
                                                                  cellModuleDict, CECModParamsDict, 
                                                                  frameParamsDict, omegaParamsDict, pilesParamsDict,
                                                                  inifilename)
    # re-load configuration file to make sure all booleans are converted
    (simulationParamsDict, sceneParamsDict, timeControlParamsDict, 
     moduleParamsDict, trackingParamsDict,torquetubeParamsDict,
     analysisParamsDict,cellModuleDict, CECModParamsDict, frameParamsDict, 
     omegaParamsDict, pilesParamsDict ) = \
        bifacial_radiance.load.readconfigurationinputfile(inifilename)
    
    # Load weatherfile

    if simulationParamsDict['getEPW']:
        simulationParamsDict['weatherFile'] = demo.getEPW(
            simulationParamsDict['latitude'], simulationParamsDict['longitude'])  # pull EPW data for any global lat/lon
  
    if simulationParamsDict['selectTimes']: 
        starttime = timeControlParamsDict['starttime'] 
        endtime = timeControlParamsDict['endtime'] 
    else: # read in full TMY file
        starttime = None; endtime=None
    
    if 'coerce_year' in simulationParamsDict:
        coerce_year = simulationParamsDict['coerce_year']
    else:
        coerce_year = None
    
    if 'weatherFileType' in simulationParamsDict:
        source = simulationParamsDict['weatherFileType']
        print("Weather file of type ", source, " passed.")
    else:
        source = None

    print('Reading weather file {}'.format(simulationParamsDict['weatherFile']))
    metdata = demo.readWeatherFile(simulationParamsDict['weatherFile'],
                                   starttime=starttime, endtime=endtime, 
                                   coerce_year=coerce_year, source=source)
    
    # input albedo number or material name like 'concrete'.  To see options, run this without any input.
    demo.setGround(sceneParamsDict['albedo'])
    analysis = None  # initialize default analysis return value to none.

    A = demo.printModules()
    
    #cellLeveLParams are none by default.
    cellModule = None 
    try:
        if simulationParamsDict['cellLevelModule']:
            cellModule = cellModuleDict
    except: pass
    
    
    """
    if not torquetubeParamsDict:
        #kwargs = {**torquetubeParamsDict, **moduleParamsDict} #Py3 Only
        torquetubeParamsDict = {}
    torquetubeParamsDict['axisofrotation'] = simulationParamsDict[
                                         'axisofrotationTorqueTube']
    """
    kwargs = moduleParamsDict
    kwargs['rewriteModulefile'] = simulationParamsDict['rewriteModule']
    if torquetubeParamsDict:
        if not 'visible' in torquetubeParamsDict:
            torquetubeParamsDict['visible'] = simulationParamsDict['torqueTube']
        if 'axisofrotationTorqueTube' in simulationParamsDict:
            torquetubeParamsDict['axisofrotation'] = simulationParamsDict[
                                         'axisofrotationTorqueTube']
        
    if (simulationParamsDict['moduletype'] in A) and not (kwargs['rewriteModulefile']):

        module = simulationParamsDict['moduletype']
        print("\nUsing Pre-determined Module Type: %s " %
              simulationParamsDict['moduletype'])
    else:
        module = demo.makeModule(name=simulationParamsDict['moduletype'],
                                     tubeParams=torquetubeParamsDict,
                                         frameParams=frameParamsDict,
                                         omegaParams=omegaParamsDict,
                                     cellModule=cellModule, **kwargs)

    # module CEC params
    if CECModParamsDict:
        module.addCEC(pd.DataFrame(CECModParamsDict, index=[0]))

    customObject = None

    if "customObject" in sceneParamsDict:
        if sceneParamsDict["customObject"] is not None:
            if sceneParamsDict["customObject"] != '':
                customObject = sceneParamsDict['customObject']
                print("Custom Object Found, will be added to all Scenes.")
                
    if 'gcr' not in sceneParamsDict:  # didn't get gcr passed - need to calculate it
        sceneParamsDict['gcr'] = module.sceney / \
            sceneParamsDict['pitch']

    if simulationParamsDict['tracking'] == False and simulationParamsDict['cumulativeSky'] == True:
    # Fixed gencumsky condition
        scene = demo.makeScene(module=module, 
                               sceneDict=sceneParamsDict, customtext=customObject)
        demo.genCumSky(demo.gencumsky_metfile)  
        
        if pilesParamsDict:
            demo.addPiles(spacingPiles=pilesParamsDict['spacingPiles'], 
                          pile_lenx=pilesParamsDict['pile_lenx'], 
                          pile_leny=pilesParamsDict['pile_leny'],
                          pile_height=pilesParamsDict['pile_height'])
            
        octfile = demo.makeOct(demo.getfilelist())
        analysis = bifacial_radiance.AnalysisObj(octfile, demo.name)
        frontscan, backscan = analysis.moduleAnalysis(scene, modWanted=analysisParamsDict['modWanted'],
                                                      rowWanted=analysisParamsDict['rowWanted'],
                                                      sensorsy=analysisParamsDict['sensorsy'])
        analysis.analysis(octfile, demo.name, frontscan, backscan)
        print('Bifacial ratio yearly average:  %0.3f' %
              (np.mean(analysis.Wm2Back) / np.mean(analysis.Wm2Front)))


    else:
    # Run everything through TrackerDict.    
        # check for deprecated axis_azimuth
        if  (sceneParamsDict.get('axis_azimuth') is not None) and (sceneParamsDict.get('azimuth') is None):
            sceneParamsDict['azimuth'] = sceneParamsDict['axis_azimuth']

        if simulationParamsDict['tracking'] == False:
            trackerdict = demo.set1axis(metdata, 
                                        cumulativesky=simulationParamsDict["cumulativeSky"],
                                        fixed_tilt_angle=sceneParamsDict['tilt'],
                                        azimuth=sceneParamsDict['azimuth']) 
        else:
            trackerdict = demo.set1axis(metdata, gcr=sceneParamsDict['gcr'],
                                        azimuth=sceneParamsDict['azimuth'],
                                        limit_angle=trackingParamsDict['limit_angle'],
                                        angledelta=trackingParamsDict['angle_delta'],
                                        backtrack=trackingParamsDict['backtrack'],
                                        cumulativesky=simulationParamsDict["cumulativeSky"])
            


        if simulationParamsDict['cumulativeSky']:
            trackerdict = demo.genCumSky1axis(trackerdict=trackerdict)
        else:           
            trackerdict = demo.gendaylit1axis()                

        trackerdict = demo.makeScene1axis(trackerdict=trackerdict,
                                          module=module,
                                          sceneDict=sceneParamsDict,
                                          cumulativesky=simulationParamsDict['cumulativeSky'], customtext=customObject)

        trackerdict = demo.makeOct1axis(trackerdict=trackerdict)

        trackerdict = demo.analysis1axis(trackerdict=trackerdict,
                                         modWanted=analysisParamsDict['modWanted'],
                                         rowWanted=analysisParamsDict['rowWanted'],
                                         sensorsy=analysisParamsDict['sensorsy'])
        
        # TODO: Chris, not all functions were saving/returning analysis before. 
               # It is also not a very good return as it will only include the last key
               # in teh trackerdict for this, but that is what we had before.
               # I would consider removing analysis as a return and modifying
               # the way teh ini_highAzimuth py test works.
               # What was before:         
               # analysis = trackerdict[time]['AnalysisObj']

        # TODO: this is only returning the first AnalysisObj for the trackerdict entry.
        #  check this for more complicated scenarios with multiple AnalysisObjs...
        # analysis = demo.trackerdict[list(demo.trackerdict.keys())[-1]]['AnalysisObj'][0]
        


            
            
        if not simulationParamsDict['cumulativeSky']:

            print("\n--> Calculating Performance values")
            
            demo.calculatePerformance1axis()
            demo.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)

    # Save example image files
    #print(simulationParamsDict)
    if simulationParamsDict.get('saveImage'):
        if hasattr(demo, 'trackerdict'):
            bestkey = _getDesiredIndex(demo.trackerdict)
            scene = demo.trackerdict[bestkey]['scenes'][0] #TODO: select which sceneNum chosen?
            imagefilename = f'scene_{bestkey}'
            viewfile = None # just use default value for now. Improve later..
        elif hasattr(demo, 'scenes'):
            scene = demo.scenes[0]
            viewfile = None # just use default value for now. Improve later..
            imagefilename = 'scene0'
        try:
            print("\nSaving scene and module .hdr to images/")
            scene.saveImage(filename=imagefilename, view=viewfile)
            #analysis.makeFalseColor('side.vp')
            scene.module.saveImage()
        except:
            print("Failed to make image")        

    print("Finished! ")
    return demo, analysis

def _getDesiredIndex(trackerdict):
    """
    Identify 'optimal' best key of trackerdict to use for visualizations.

    Parameters
    ----------
    trackerdict : final trackerdict

    Returns
    -------
    bestkey
    
    viewfile

    """
    import pandas as pd
    
    df = pd.DataFrame.from_dict(trackerdict, orient='index')
    try:
        df = df[df['scenes'].notna()] 
    except KeyError:
        print('Error in _getDesiredIndex - trackerdict has no scene defined.')
        return df.index[-1]
    # try to find an index close to 25 degree tilt
    try:
        df['objective_fn'] = abs(df.surf_tilt - 25) # choose an index closest to 25 tilt with 
        bestkey = df['objective_fn'].idxmin()
    except:
        bestkey = df.index[-1]  # default to last index

    return bestkey