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


# # 21 - Weather to Module Performance
# ## Modeling Performance, an End to End Simulation
# 
# This tutorial shows how to use the new function on bifacial_radiance calculatePerformanceModule performance, as well as how to find CEC Module parameters.
# 

# In[2]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_21')

if not os.path.exists(testfolder): os.mkdir(testfolder)

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


import bifacial_radiance
import numpy as np
import pandas as pd
import pvlib 

bifacial_radiance.__version__


# ## Geting a CEC Module to pass into demo.makeModule

# In[4]:


url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
db = pd.read_csv(url, index_col=0) # Reading this might take 1 min or so, the database is big.


# Find the module that you want. In this case we know it's a SunPower of model SPR-E19-310-COM. 
# 
# Make sure you select only 1 module from the database -- sometimes there are similar names.

# In[5]:


modfilter2 = db.index.str.startswith('SunPower') & db.index.str.endswith('SPR-E19-310-COM')
print(modfilter2)
CECMod = db[modfilter2]
print(len(CECMod), " modules selected. Name of 1st entry: ", CECMod.index[0])


# In[ ]:





# In[6]:


# Selecting only two times as examples
starttime = '01_13_11';  endtime = '01_13_12'
demo = bifacial_radiance.RadianceObj('tutorial_21', path = testfolder) # Create a RadianceObj 'object'
weatherfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(weatherFile=weatherfile, starttime=starttime, endtime=endtime)
demo.setGround(0.2)


# The CEC data should be passed into the ModuleObj, either at time of creation, or sometime before it is passed into makeScene.

# In[7]:


mymodule = demo.makeModule(name='test-module', x=1, y=2, bifi=0.9, CECMod=CECMod) 


# The same data could instead be passed after the ModuleObj's definition, or at time of performance analysis:

# In[8]:


mymodule.addCEC(CECMod)


# In[9]:


# Let's make a second module, and set it to the default Prism Solar module type
mymodule2 = demo.makeModule(name='test', x=1, y=2, bifi=0.8, CECMod=None) 


# We're going to set up two scenes, each with a different module type!

# In[10]:


sceneDict = {'tilt': 0, 'azimuth': 180, 'pitch': 5,'hub_height':1.5, 'nMods':5, 'nRows': 2}
trackerdict = demo.set1axis(metdata = metdata, cumulativesky = False)
trackerdict = demo.gendaylit1axis()
trackerdict = demo.makeScene1axis(trackerdict, module = mymodule, sceneDict = sceneDict)


# Make a second scene with the other module type

# In[11]:


sceneDict2 = {'tilt': 0, 'azimuth': 180, 'pitch': 5,'hub_height':2.5, 'nMods':2, 'nRows': 1, 'originx': -15}
trackerdict = demo.makeScene1axis(trackerdict, module = mymodule2, sceneDict=sceneDict2, append=True)


# In[12]:


# Compile both scenes into one octfile.  Run 2 different analyses, one on each scene with different front and rear y scan
trackerdict = demo.makeOct1axis()
trackerdict = demo.analysis1axis(sensorsy=[1,3], append=False)
trackerdict = demo.analysis1axis(sensorsy=[3,2], sceneNum=1)


# In[13]:


# Include an AgriPV groundscan too
trackerdict = demo.analysis1axisground(sceneNum=1, sensorsground=10, customname='Silvanas_')


# In[14]:


# show the initial irradiance results before continuing:
demo.results


# ## Calculating the Performance and Exporting the Results to a CSV

# In[15]:


# Calculate performance.
pd.set_option('display.max_columns', 1000); 
compiledResults = demo.calculatePerformance1axis()
print(f'\nCompiled results:\n')
display(compiledResults)


# In[16]:


demo.exportTrackerDict(savefile=os.path.join('results','Final_Results.csv'),reindex=False)
pd.read_csv(os.path.join('results','Final_Results.csv'))


# ## Now look at gencumulativesky tracking workflow

# In[17]:


starttime = '01_13_11';  endtime = '12_13_12'
demo = bifacial_radiance.RadianceObj('tutorial_21', path = testfolder) # Create a RadianceObj 'object'
weatherfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(weatherFile=weatherfile, starttime=starttime, endtime=endtime)
#metdata = demo.readWeatherFile(weatherFile=weatherfile)
demo.setGround(0.2)
mymodule = demo.makeModule(name='test-module', x=1, y=2, bifi=0.9, CECMod=CECMod) 


# In[18]:


sceneDict = {'tilt': 0, 'azimuth': 180, 'pitch': 5,'hub_height':1.5, 'nMods':5, 'nRows': 2}
trackerdict = demo.set1axis(metdata=metdata, cumulativesky=True, limit_angle=15, backtrack=False)
trackerdict = demo.genCumSky1axis()
trackerdict = demo.makeScene1axis(trackerdict, module = mymodule, sceneDict = sceneDict)
trackerdict = demo.makeOct1axis()
trackerdict = demo.analysis1axis(modWanted = [2,4], sensorsy=[2,3])
trackerdict = demo.analysis1axisground(sensorsground=10)


# In[19]:


results = demo.calculatePerformance1axis() # saves to demo.compiledResults and results/Cumulative_Results.csv
print('\nCompiled results:\n')
display(demo.compiledResults)


# In[20]:


# Results are also automatically saved in \results\Cumulative_Results.csv
pd.read_csv(os.path.join('results','Cumulative_Results.csv'))


# In[ ]:




