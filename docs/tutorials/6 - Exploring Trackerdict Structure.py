#!/usr/bin/env python
# coding: utf-8

# # NOTE: this notebook is not updated for v0.5.0

# In[1]:


# This information helps with debugging and getting support :)
import sys, platform
import pandas as pd
import bifacial_radiance as br
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# # 6 - Exploring Trackerdict Structure
# 
# Tutorial 6 gives a good, detailed introduction to the trackerdict structure step by step.
# Here is a condensed summary of functions you can use to explore the tracker dictionary.
# 
# 
# ***Steps:***
# 
# 1. <a href='#step1'> Create a short Simulation + tracker dictionary beginning to end for 1 day </a>
# 2. <a href='#step2'> Explore the tracker dictionary </a>
# 3. <a href='#step3'> Explore Save Options </a>

# <a id='step 1'></a>

# ## 1. Create a short Simulation + tracker dictionary beginning to end for 1 day

# In[2]:


import bifacial_radiance
from pathlib import Path
import os

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_06')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)              

simulationName = 'tutorial_6'
moduletype = 'test-module'   
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 3
nRows = 1
hub_height = 2.3 # meters
pitch = 10 # meters      # We will be using pitch instead of GCR for this example.

# Traking parameters
cumulativesky = False
limit_angle = 45 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 

#makeModule parameters
# x and y will be defined by the cell-level module parameters
xgap = 0.01
ygap = 0.10
zgap = 0.05
numpanels = 2
torquetube = True
axisofrotationTorqueTube = False
diameter = 0.1
tubetype = 'Oct'    # This will make an octagonal torque tube.
material = 'black'   # Torque tube will be made of this material (0% reflectivity)

tubeParams = {'diameter':diameter,
              'tubetype':tubetype,
              'material':material,
              'axisofrotation':axisofrotationTorqueTube,
              'visible':torquetube}

# Simulation range between two hours
startdate = '11_06_11'       # Options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
enddate = '11_06_14'

# Cell Parameters
numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate)  
cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}
mymodule = demo.makeModule(name=moduletype, xgap=xgap, ygap=ygap, zgap=zgap, 
                           numpanels=numpanels, cellModule=cellLevelModuleParams, tubeParams=tubeParams)

sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle=limit_angle, backtrack=backtrack, gcr=mymodule.sceney / pitch, cumulativesky=cumulativesky)
demo.gendaylit1axis()
demo.makeScene1axis(module=mymodule, sceneDict=sceneDict)
demo.makeOct1axis()
demo.analysis1axis()


# <a id='step2'></a>

# ## 2. Explore the tracker dictionary
# 
# You can use any of the below options to explore the tracking dictionary. Copy it into an empty cell to see their contents.

# In[2]:


print(demo)   # Shows all keys for top-level RadianceObj

trackerkeys = sorted(demo.trackerdict.keys()) # get the trackerdict keys to see a specific hour.

demo.trackerdict[trackerkeys[0]] # This prints all trackerdict content
demo.trackerdict[trackerkeys[0]]['scene']  # This shows the Scene Object contents
demo.trackerdict[trackerkeys[0]]['scene'].module.scenex  # This shows the Module Object in the Scene's contents
demo.trackerdict[trackerkeys[0]]['scene'].sceneDict # Printing the scene dictionary saved in the Scene Object
demo.trackerdict[trackerkeys[0]]['scene'].sceneDict['tilt'] # Addressing one of the variables in the scene dictionary


# Looking at the AnalysisObj results indivudally
demo.trackerdict[trackerkeys[0]]['AnalysisObj']  # This shows the Analysis Object contents
demo.trackerdict[trackerkeys[0]]['AnalysisObj'].mattype # Addressing one of the variables in the Analysis Object

# Looking at the Analysis results Accumulated for the day:
demo.Wm2Back  # this value is the addition of every individual irradiance result for each hour simulated.

#  Access module values
demo.trackerdict[trackerkeys[0]]['scene'].module.scenex

# A pretty DataFrame of all results:
demo.trackerdict[trackerkeys[0]]['scene'].results


# <a id='step3'></a>

# ## 3. Explore Save Options
# 
# The following lines offer ways to save your trackerdict or your demo object.

# In[3]:


demo.exportTrackerDict(trackerdict = demo.trackerdict, savefile = 'results\\test_reindexTrue.csv', reindex = False)
demo.save(savefile = 'results\\demopickle.pickle')

