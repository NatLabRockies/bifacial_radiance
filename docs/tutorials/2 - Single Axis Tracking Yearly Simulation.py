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


# # 2 - Single Axis Tracking Yearly Simulation
# 
# Method <b> Gencumsky </b> has been modified to divide the yearly-cumulative sky into various skies, each one representing the cumulative irradiance for the hours at which the tracker is at a certain angle. For faster running, for a tracker that moves between 45 and -45 degrees limit angle, if only positions every 5 degrees are considered (45, 40, 35 .... -4-, -45), then only 18 skies (and 18 simulations) will be run for the whole year.
# 
# ![Example of the hemisphere cumulative sky](../images_wiki/Journal2Pics/tracking_cumulativesky.PNG)
# 
# 
# This procedure was presented in:
# 
# Ayala Pelaez S, Deline C, Greenberg P, Stein JS, Kostuk RK. Model and validation of single-axis tracking with bifacial PV. IEEE J Photovoltaics. 2019;9(3):715–21. https://ieeexplore.ieee.org/document/8644027 and https://www.nlr.gov/docs/fy19osti/72039.pdf (pre-print, conference version)
# 
# 
# ***Steps:***
# 1. <a href='#step1'> Create a folder for your simulation, and load bifacial_radiance </a> 
# 2. <a href='#step2'> Create a Radiance Object, set Albedo and Download Weather Files </a>  
# 4. <a href='#step3'> Set Tracking Angles </a>
# 5. <a href='#step4'> Generate the Sky </a> 
# 6. <a href='#step5'> Define a Module type </a>
# 7. <a href='#step6'> Create the scene </a>
# 8. <a href='#step7'> Combine Ground, Sky and Scene Objects </a>
# 9. <a href='#step8'> Analyze and get results </a>
# 10. <a href='#step9'> Clean Results </a>   
#    
# 
# And finally: <a href='#condensed'> Condensed instructions </a>

# <a id='step1'></a>

# 
# ## 1. Create a folder for your simulation, and load bifacial_radiance 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journal. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# ***testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'***
# 
# 

# In[1]:


import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_02'

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)


# This will load bifacial_radiance and other libraries from python that will be useful for this Jupyter Journal:

# In[2]:


from bifacial_radiance import *
import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object, Set Albedo, and Download and Load Weather File
# 
# These are all repeated steps from Tutorial 1, so condensing:

# In[3]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('tutorial_2', path = str(testfolder))  

albedo = 0.25
demo.setGround(albedo)

# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
# Read in the weather data pulled in above. 
metdata = demo.readWeatherFile(weatherFile = epwfile) 


# <a id='step3'></a>

# # TRACKING Workflow

# Until now, all the steps looked the same from Tutorial 1. The following section follows similar steps, but the functions are specific for working with single axis tracking.
# 
# ## 3. Set Tracking Angles
# 
# This function will read the weather file, and based on the sun position it will calculate the angle the tracker should be at for each hour. It will create metdata files for each of the tracker angles considered.

# In[4]:


limit_angle = 5 # tracker rotation limit angle. Setting it ridiculously small so this runs faster.
angledelta = 5 # sampling between the limit angles. 
backtrack = True
gcr = 0.33
cumulativesky = True # This is important for this example!
trackerdict = demo.set1axis(metdata = metdata, limit_angle = limit_angle, backtrack = backtrack, 
                            gcr = gcr, cumulativesky = cumulativesky)


# Setting backtrack to True is important in this step, so the trackers correct for self-shading when following the sun at high zenith angles. 

# <a id='step4'></a>

# ## 4. Generate the Sky
# 
# This will create the skies for each sub-metdata file created by set1axis.
# 

# In[5]:


trackerdict = demo.genCumSky1axis()


# This is how one of the cumulative sky .cal files associated with each .rad file generated look like: 
# 
# ![Example of the gencumsky1axis](../images_wiki/Journal2Pics/gencumsky1axis_example_file_structure_and_contents.PNG)
# 
# 
# Each of the values corresponds to the cumulative rradiance of one of those patches, for when the tracker is at that specific angle through the year.

# <a id='step5'></a>

# ## 5. Define the Module type
# 
# Let's make a more interesting module in this example. Let's do 2-up configuration in portrait, with the modules rotating around a 10 centimeter round torque tube. Let's add a gap between the two modules in 2-UP of 10 centimeters, as well as gap between the torque tube and the modules of 5 centimeters. Along the row, the modules are separated only 2 centimeters for this example. The torquetube is painted Metal_Grey in this example (it's one of the materials available in Ground.rad, and it is 40% reflective).
# 
# Note that starting with bifacial_radiance version 0.4.0, the module object has a new geometry generation function `addTorquetube`.  The old way of passing a properly formatted dictionary as a keyword argument will still work too.
# 

# In[6]:


x = 0.984  # meters
y = 1.7    # meters
moduletype = 'test-module'
numpanels = 2
zgap = 0.05
ygap = 0.10
xgap = 0.02

module = demo.makeModule(name=moduletype, x=x, y=y,xgap=xgap, ygap=ygap, zgap=zgap, 
                numpanels=numpanels)

module.addTorquetube(diameter=0.1, material='Metal_Grey', tubetype='round') # New torquetube generation function
print()
print(module)
print()
print(module.torquetube)


# <a id='step6'></a>

# ## 6. Make the Scene
# 
# The scene Dictionary specifies the information of the scene. For tracking, different input parameters are expected in the dictionary, such as number of rows, number of modules per row, row azimuth, hub_height (distance between the axis of rotation of the modules and the ground). 

# In[7]:


hub_height = 2.3
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'nMods': 20, 'nRows': 7}  


# To make the scene we have to create a Scene Object through the method makeScene1axis. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.

# In[8]:


trackerdict = demo.makeScene1axis(trackerdict = trackerdict, module = module, sceneDict = sceneDict) 


# <a id='step7'></a>

# ## 7. Combine Ground, Sky and Scene Objects
# 
# makeOct1axis joins the sky.rad file, ground.rad file, and the geometry.rad files created in makeScene.

# In[ ]:


trackerdict = demo.makeOct1axis(trackerdict = trackerdict)


# <a id='step8'></a>

# ## 8. Analyze and get results
# 
# We can choose to analyze any module in the Scene we have created. The default, if no modWanted or rowWanted is passed, is to sample the center module of the center row. 
# 
# For this example we will sample row 2, module 9.

# In[10]:


modWanted = 9
rowWanted = 2
trackerdict = demo.analysis1axis(trackerdict, modWanted=9, rowWanted = 2)


# Let's look at the results with more detail. The analysis1axis routine created individual result .csv files for each angle. To get a single cumulative result .csv where the irradiance is added by sensor, we need to run `calculateResults()`. This function will save a file named "results/Cumulative_Results.csv" and add a dataframe called "CompiledResults" to the radiance object.
# 

# In[12]:


results = demo.calculateResults()


# We can view the cumlative results in two ways. The first is acess them directly from the RadianceObject.

# In[13]:


demo.CompiledResults


# In[14]:


resultPath = os.path.join('results','Cumulative_Results.csv')
cumulativeResults = load.read1Result(resultPath)
cumulativeResults


# Lets take a closer look at a single result file.

# In[16]:


resultPath = os.path.join('results','irr_1axis_-5.0_Scene0_Row2_Module9.csv')
results = load.read1Result(resultPath)
results


# There are various things to notice:
# 
# I. The materials column has a specific format that will tell you if you are sampling the correct module:
# 
#                                 a{ModWanted}.{rowWanted}.a{numPanel}.{moduletype}.material_key
# 
# * Since for this journal numPanels = 2, numPanel can either be 0 or 1, for the East-most and West-most module in the collector width.
# * numPanel, ModWanted and RowWanted are indexed starting at 0 in the results.
# * material_key is from the surface generated inside radiance. Usually it is 6457 for top surface of the module and .2310 for the bottom one. 
# 
# II. Sensors sample always in the same direction. For this N-S aligned tracker, that is East-most to West. For this 2-up portrait tracker which is 3.5 meters, 20x7 rows and we are sampling module 9 on row 2, the East to West sampling goes from 22.6 m to 19.81 m = 2.79m. It is not exatly 3.5 because the sensors are spaced evenly through the collector width (CW): 
# 
# 
# ![Sensors spaced along collector width](../images_wiki/Journal2Pics/spaced_sensors.PNG)
# 
# III. When there is a ygap in the collector width (2-UP or more configuration), some of the sensors might end up sampling the torque tube, or the sky. You can see that in the materials columns. This also happens if the number of sensors is quite high, the edges of the module might be sampled instead of the sensors. For this reason, before calculating bifacial gain these results must be cleaned. For more advanced simulations, make sure you clean each result csv file individually.  We provide some options on load.py but some are very use-specific, so you might have to develop your own cleaning tool (or let us know on issues!)
# 
# <div class="alert alert-warning">
# Important: If you have torquetubes and y-gap values, make sure you clean your results.
# </div>
# 

# <a id='step9'></a>

# ## 9. Clean Results
# 
# We have two options for cleaning results. The simplest one is <b>load.cleanResults</b>, but there is also a deepClean for specific purposes.
# 
# cleanResults will find materials that should not have values and set them to NaN.

# In[ ]:


results_clean = load.cleanResult(results)
results_clean


# These are the total irradiance values over all the hours of the year that the module at each sampling point will receive. Dividing the back irradiance average by the front irradiance average will give us the bifacial gain for the year:
# 
# ![Bifacial Gain in Irradiance Formula](../images_wiki/Journal1Pics/BGG_Formula.PNG)
# 
# Assuming that our module from Prism Solar has a bifaciality factor (rear to front performance) of 90%, our <u> bifacial gain </u> is of:

# In[ ]:


bifacialityfactor = 0.9
print('Annual bifacial ratio: %0.3f ' %( np.nanmean(results_clean.Wm2Back) * bifacialityfactor / np.nanmean(results_clean.Wm2Front)) )


# <a id='condensed'></a>

# ## CONDENSED VERSION
# Everything we've done so far in super short condensed version:

# In[19]:


import pandas as pd
startdate = pd.to_datetime('2021-05-01 6:0:0') #
    #                pd.to_datetime('2021-06-01 6:0:0'),
    #                pd.to_datetime('2021-07-01 6:0:0'),
    #                pd.to_datetime('2021-08-01 6:0:0'),
    #                pd.to_datetime('2021-09-01 6:0:0'),
    #                pd.to_datetime('2021-05-01 6:0:0')]
enddate = pd.to_datetime('2021-05-31 6:0:0')# ,       # May
    #                pd.to_datetime('2021-06-30 20:0:0'),   # June


# In[ ]:


albedo = 0.25
lat = 37.5
lon = -77.6
nMods = 20
nRows = 7
hub_height = 2.3
gcr = 0.33
moduletype = 'test-module'  # this must already exist since we are not calling makeModule in this CONDENSED example.
#testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal2'
limit_angle = 50
angeldelta = 5
backtrack = True
gcr = gcr
modWanted = 9
rowWanted = 2
cumulativesky = True

import bifacial_radiance
demo = RadianceObj('test') 
demo.setGround(albedo)
epwfile = demo.getEPW(lat, lon) 
metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate, coerce_year=2021)
demo.set1axis(limit_angle=limit_angle, backtrack=backtrack, gcr=gcr, cumulativesky=cumulativesky)
demo.genCumSky1axis()
sceneDict = {'gcr': gcr,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  # orientation deprecated on v.0.2.4.
demo.makeScene1axis(module=moduletype, sceneDict=sceneDict)
demo.makeOct1axis()
demo.analysis1axis(modWanted=modWanted, rowWanted=rowWanted);


# In[21]:


res = demo.calculatePerformance1axis()


# In[22]:


res


# In[ ]:




