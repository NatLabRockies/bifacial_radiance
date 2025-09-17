#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This information helps with debugging and getting support :)
import sys, platform
import pandas as pd
import bifacial_radiance as br
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# # 3 - Single Axis Tracking Hourly
# 
# Example demonstrating the use of doing hourly smiulations with Radiance gendaylit for 1-axis tracking. This is a medium level example because it also explores a couple subtopics:
# 
# ***Subtopics:***
# * The structure of the tracker dictionary "trackerDict".
# * How to calculate GCR 
# * How to make a cell-level module
# * Various methods to use the trackerdictionary for analysis.
#  
# ***Doing full year simulations with gendaylit:***
# 
# Performing the simulation hour by hour requires either a good computer or some patience, since there are ~4000 daylight-hours in the year. With a 32GB RAM, Windows 10 i7-8700 CPU @ 3.2GHz with 6 cores this takes 1 day. The code also allows for multiple cores or HPC use -- there is documentation/examples inside the software at the moment, but that is an advanced topic. The procedure can be broken into shorter steps for one day or a single timestamp simulation which is exemplified below.
# 
# ***Steps:***
# 1. <a href='#step1'> Load bifacial_radiance </a>
# 2. <a href='#step2'> Define all your system variables </a>
# 3. <a href='#step3'> Create Radiance Object, Set Albedo and Weather </a>
# 4. <a href='#step4'> Make Module: Cell Level Module Example </a>
# 5. <a href='#step5'> Calculate GCR</a>
# 6. <a href='#step6'> Set Tracking Angles </a>
# 7. <a href='#step7'> Generate the Sky </a>
# 8. <a href='#step8'> Make Scene 1axis </a>
# 9. <a href='#step9a'> Make Oct and AnalyzE 1 HOUR </a>
# 10. <a href='#step9b'> Make Oct and Analye Range of Hours </a>
# 11. <a href='#step9c'>  Make Oct and Analyze All Tracking Dictionary </a>
# 
# And finally: <a href='#condensed'> Condensed Version: All Tracking Dictionary </a> 

# <a id='step1'></a>

# 
# ## 1. Load bifacial_radiance 
# 
# <u>Pay attention: different importing method:</u>
# 
# So far we've used "from bifacial_radiance import *" to import all the bifacial_radiance files into our working space in jupyter. For this journal we will do a "import bifacial_radiance" . This method of importing requires a different call for some functions as you'll see below. For example, instead of calling demo = RadianceObj(path = testfolder) as on Tutorial 2, in this case we will neeed to do demo = bifacial_radiance.RadianceObj(path = testfolder). 

# In[2]:


import bifacial_radiance
import numpy as np
import os # this operative system to do teh relative-path testfolder for this example.
import pprint    # We will be pretty-printing the trackerdictionary throughout to show its structure.
from pathlib import Path


# <a id='step2'></a>

# ## 2. Define all your system variables
# 
# Just like in the condensed version show at the end of Tutorial 2, for this tutorial we will be starting all of our system variables from the beginning of the jupyter journal, instead than throughout the different cells (for the most part)

# In[3]:


testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_03'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)
    
    
simulationName = 'tutorial_03'    # For adding a simulation name when defning RadianceObj. This is optional.
moduletype = 'test-module'    # We will define the parameters for this below in Step 4.
albedo = "litesoil"      # this is one of the options on ground.rad
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 2.3 # meters
pitch = 10 # meters      # We will be using pitch instead of GCR for this example.

# Traking parameters
cumulativesky = False
limit_angle = 45 # tracker rotation limit angle
angledelta = 0.01 # we will be doing hourly simulation, we want the angle to be as close to real tracking as possible.
backtrack = True 

#makeModule parameters
# x and y will be defined later on Step 4 for this tutorial!!
xgap = 0.01
ygap = 0.10
zgap = 0.05
numpanels = 2
axisofrotation = True  #  the scene will rotate around the torque tube, and not the middle of the bottom surface of the module
diameter = 0.1
tubetype = 'Oct'    # This will make an octagonal torque tube.
material = 'black'   # Torque tube of this material (0% reflectivity)


# <a id='step3'></a>

# ## 3. Create Radiance Object, Set Albedo and Weather
# 
# Same steps as previous two tutorials, so condensing it into one step. You hopefully have this down by now! :)
# 
# 
# <div class="alert alert-warning">
# Notice that we are doing bifacial_radiance.RadianceObj because we change the import method for this example!
# </div>
# 
# We now constrain the days of our analysis in the readWeatherFile import step.  For this example we are doing just two days in January. Format has to be a 'MM_DD' or 'YYYY-MM-DD_HHMM'

# In[4]:


demo = bifacial_radiance.RadianceObj(simulationName, path = str(testfolder))  # Adding a simulation name. This is optional.
demo.setGround(albedo) 
epwfile = demo.getEPW(lat=lat, lon=lon) #r'EPWs\USA_VA_Richmond.724010_TMY2.epw'#

starttime = '01_13';  endtime = '01_14'
metdata = demo.readWeatherFile(weatherFile=epwfile, starttime=starttime, endtime=endtime) 


# <a id='step4'></a>

# ## 4. Make Module: Cell Level Module Example
# 
# Instead of doing a opaque, flat single-surface module, in this tutorial we will create a module made up by cells. We can define variuos parameters to make a cell-level module, such as cell size and spacing between cells. To do this, we will pass a dicitonary with the needed parameters to makeModule, as shown below.  
# 
# NOTE: in v0.4.0 some keywords and methods for doing a CellModule and Torquetube simulation were changed.
# 
# <div class="alert alert-warning">
# Since we are making a cell-level module, the dimensions for x and y of the module will be calculated by the software -- dummy values can be initially passed just to get started, but these values are overwritten by addCellModule()
#     </div>

# In[5]:


numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02


mymodule = demo.makeModule(name=moduletype,  x=1, y=1, xgap=xgap, ygap=ygap, 
                           zgap=zgap, numpanels=numpanels) 
mymodule.addTorquetube(diameter=diameter, material=material,
                       axisofrotation=axisofrotation, tubetype=tubetype)
mymodule.addCellModule(numcellsx=numcellsx, numcellsy=numcellsy,
                       xcell=xcell, ycell=ycell, xcellgap=xcellgap, ycellgap=ycellgap)

print(f'New module created. x={mymodule.x}m,  y={mymodule.y}m')
print(f'Cell-module parameters: {mymodule.cellModule}')


# <a id='step5'></a>

# ## 5. Calculate GCR
# 
# In this example we passed the parameter "pitch". Pitch is the spacing between rows (for example, between hub-posts) in a field.
# To calculate Ground Coverage Ratio (GCR), we must relate the pitch to the collector-width by:
#     
# ![GCR = CW / pitch](../images_wiki/Journal3Pics/Equation_GCR.PNG)
# 
# The collector width for our system must consider the number of panels and the y-gap:
#     
# ![CW](../images_wiki/Journal3Pics/Equation_CW.PNG)
#     
# Collector Width gets saved in your module parameters (and later on your scene and trackerdict) as "sceney". You can calculate your collector width with the equation, or you can use this method to know your GCR:

# In[6]:


# For more options on makemodule, see the help description of the function.  
# Details about the module are stored in the new ModuleObj 
CW = mymodule.sceney
gcr = CW / pitch
print ("The GCR is :", gcr)
print(f"\nModuleObj data keys: {mymodule.keys}")


# <a id='step6'></a>

# ## 6. Set Tracking Angles
# 
# This function will read the weather file, and based on the sun position it will calculate the angle the tracker should be at for each hour. It will create metdata files for each of the tracker angles considered.
# 
# For doing hourly simulations, remember to set **cumulativesky = False** here!

# In[7]:


trackerdict = demo.set1axis(metdata=metdata, limit_angle=limit_angle, backtrack=backtrack, 
                            gcr=gcr, cumulativesky=False)


# In[8]:


print ("Trackerdict created by set1axis: %s " % (len(demo.trackerdict))) 


# set1axis initializes the trackerdictionary Trackerdict. Trackerdict contains all hours selected from the weatherfile as keys. For example: trackerdict['2021-01-13_1200']. It is a return variable on many of the 1axis functions, but it is also stored inside of your Radiance Obj (i.e. demo.trackerdict). In this journal we are storing it as a variable to mute the option (otherwise it prints the returned trackerdict contents every time)
# 

# In[9]:


display(trackerdict['2021-01-13_1200'])


# All of the following functions add up elements to trackerdictionary to keep track (ba-dum tupzz) of the Scene and simulation parameters. In advanced journals we will explore the inner structure of trackerdict. For now, just now it exists :)

# <a id='step7'></a>

# ## 7. Generate the Sky
# 
# 
# We will create skies for each hour we want to model with the function gendaylit1axis. 
# 
# For this example we are doing just two days in January. The ability to limit the time using gendaylit1axis is deprecated.  Use readWeatherFile instead.

# In[10]:


trackerdict = demo.gendaylit1axis() 


# Since we passed startdate and enddate to gendaylit, it will prune our trackerdict to only the desired days.
# Let's explore our trackerdict:

# In[11]:


trackerkeys = sorted(trackerdict.keys())
print ("Trackerdict option of hours are: ", trackerkeys)
print ("")
print ("Contents of trackerdict for sample hour:")
display(trackerdict[trackerkeys[0]])


# <a id='step8'></a>

# ## 8. Make Scene 1axis
# 
# We can use gcr or pitch fo our scene dictionary.

# In[12]:


sceneDict = {'pitch': pitch,'hub_height':hub_height, 'nMods':nMods, 'nRows': nRows}  

# making the different scenes for the 1-axis tracking for the dates in trackerdict2.
trackerdict = demo.makeScene1axis(trackerdict=trackerdict, module=mymodule, sceneDict=sceneDict) 


# The scene parameteres are now stored in the trackerdict. To view them and to access them:
#     

# In[13]:


display(trackerdict[trackerkeys[0]])


# In[14]:


pprint.pprint(demo.trackerdict[trackerkeys[5]]['scenes'][0].__dict__)


# <a id='step9a'></a>

# ## 9. Make Oct and Analyze 
# 
# ### A. Make Oct and Analyze 1Hour
# 
# There are various options now to analyze the trackerdict hours we have defined. We will start by doing just one hour, because it's the fastest. Make sure to select an hour that exists in your trackerdict!
# 
# Options of hours:

# In[15]:


print(trackerkeys)


# In[16]:


demo.makeOct1axis(singleindex='2021-01-13_0800')
results = demo.analysis1axis(singleindex='2021-01-13_0800')
temp = results['2021-01-13_0800']['AnalysisObj'][0].results
print('\n\nHourly bifi gain: {:0.3}'.format(sum(temp['Wm2Back'][0]) / sum(temp['Wm2Front'][0])))


# The trackerdict now contains information about the octfile, as well as the Analysis Object results

# In[17]:


print ("\n Contents of trackerdict for sample hour after analysis1axis: ")
display(trackerdict[trackerkeys[0]])


# In[18]:


pprint.pprint(trackerdict[trackerkeys[0]]['AnalysisObj'][0].__dict__)


# <a id='step9b'></a>

# ### B. Make Oct and Analye Range of Hours

# You could do a list of indices following a similar procedure:

# In[19]:


for time in ['2021-01-13_0900','2021-01-13_1300']:  
    demo.makeOct1axis(singleindex=time)
    trackerdict=demo.analysis1axis(singleindex=time)


# In[19]:


results = demo.results


# In[20]:


print('Accumulated hourly bifi gain: {:0.3}'.format(results.Wm2Back.sum().sum() / results.Wm2Front.sum().sum()))


# In[21]:


display(results)


# Note that the bifacial gain printed above is for the accumulated irradiance between the hours modeled so far. 
# That is, demo.Wm2Back and demo.Wm2Front are for January 13, 8AM, 9AM and  1 PM. Compare demo.Wm2back below with what we had before:

# In[20]:





# To print the specific bifacial gain for a specific hour, you can use the following: (for results index 0)

# In[22]:


index = 0
print(f"Gain for timestamp {results.loc[index,'timestamp']}: " +       f"{sum(results.loc[index,'Wm2Back']) / sum(results.loc[index,'Wm2Front']):0.3}")


# In[21]:





# <a id='step9c'></a>

# ### C. Make Oct and Analyze All Tracking Dictionary
# 
# This takes considerably more time, depending on the number of entries on the trackerdictionary. If no **starttime** and **endtime** were specified on STEP **readWeatherFile, this will run ALL of the hours in the year (~4000 hours).**
# 

# In[25]:


demo.makeOct1axis()
results = demo.analysis1axis()


# In[30]:


print('Accumulated hourly bifi gain for all the trackerdict: {:0.3}'.format(
    demo.results.loc[:,'Wm2Back'].sum().sum() / demo.results.loc[:,'Wm2Front'].sum().sum()))


# In[ ]:





# <div class="alert alert-warning">
# Remember you should clean your results first! This will have torquetube and sky results if performed this way so don't trust this simplistic bifacial_gain examples.
# </div>

# <a id='condensed'></a>

# ## Condensed Version: All Tracking Dictionary
# 
# This is the summarized version to run gendaylit for each entry in the trackingdictionary.

# In[ ]:


import bifacial_radiance
import os 

simulationName = 'Tutorial 3'
moduletype = 'Custom Cell-Level Module'    
testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')
albedo = "litesoil"    
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 2.3 # meters
pitch = 10 # meters    

# Traking parameters
cumulativesky = False
limit_angle = 45 # degrees 
angledelta = 0.01 # 
backtrack = True 

#makeModule parameters
# x and y will do not need to be defined as they are calculated internally for cell-level modules
xgap = 0.01
ygap = 0.10
zgap = 0.05
numpanels = 2

cellModuleParams = {'numcellsx': 6, 
'numcellsy': 12,
'xcell': 0.156,
'ycell': 0.156,
'xcellgap': 0.02,
'ycellgap': 0.02}



torquetube = True
axisofrotation = True  # the scene will rotate around the torque tube, and not the middle of the bottom surface of the module
diameter = 0.1
tubetype = 'Oct'    # This will make an octagonal torque tube.
material = 'black'   # Torque tube material (0% reflectivity)
tubeParams = {'diameter':diameter,
              'tubetype':tubetype,
              'material':material,
              'axisofrotation':axisofrotation}

startdate = '11_06'     
enddate = '11_06'
demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate)  
mymodule = bifacial_radiance.ModuleObj(name=moduletype, xgap=xgap, ygap=ygap,   
                zgap=zgap, numpanels=numpanels, cellModule=cellModuleParams, tubeParams=tubeParams)
sceneDict = {'pitch':pitch, 'hub_height':hub_height, 'nMods': nMods, 'nRows':nRows}  
demo.set1axis(limit_angle=limit_angle, backtrack=backtrack, gcr=gcr, cumulativesky=cumulativesky)
demo.gendaylit1axis()
demo.makeScene1axis(module=mymodule, sceneDict=sceneDict) #makeScene creates a .rad file with 20 modules per row, 7 rows.
demo.makeOct1axis()
demo.analysis1axis()
print(demo.results)

