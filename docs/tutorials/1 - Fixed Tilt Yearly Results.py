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


# # 1 - Fixed-Tilt Yearly Results
# 
# This jupyter journal will walk us through the creation of the most basic fixed-tilt simulation possible with bifacial_radiance.
# We will simulate a 1-up landscape system over a white rooftop.
# 
# Steps include:
# 
# 
# 1.    <a href='#step1'> Create a folder for your simulation, and Load bifacial_radiance </a>
# 2.    <a href='#step2'> Create a Radiance Object </a> 
# 3.    <a href='#step3'> Set the Albedo </a>
# 4.    <a href='#step4'> Download Weather Files </a> 
# 5.    <a href='#step5'> Generate the Sky </a>
# 6.    <a href='#step6'> Define a Module type </a>
# 7.    <a href='#step7'> Create the scene </a> 
# 8.    <a href='#step8'> Combine Ground, Sky and Scene Objects </a> 
# 9.    <a href='#step9'> Analyze and get results </a>
# 10.   <a href='#step10'> Visualize scene options </a>  
# 
# 

# <a id='step1'></a>

# 
# ## 1. Create a folder for your simulation, and load bifacial_radiance 
# 
# First let's set the folder where the simulation will be saved. By default, this is the TEMP folder in the bifacial_radiance distribution.
# 
# The lines below find the location of the folder relative to this Jupyter Journa. You can alternatively point to an empty directory (it will open a load GUI Visual Interface) or specify any other directory in your computer, for example:
# 
# ***testfolder = r'C:\Users\sayala\Documents\RadianceScenes\Tutorials\Journal1'***
# 
# 

# In[2]:


import os
from pathlib import Path
import pandas as pd

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_01'

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)


# This will load bifacial_radiance and other libraries from python that will be useful for this Jupyter Journal:

# In[3]:


try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np


# <a id='step2'></a>

# ## 2. Create a Radiance Object

# In[4]:


# Create a RadianceObj 'object' named bifacial_example. no whitespace allowed
demo = RadianceObj('tutorial_1',str(testfolder))  


# This will create all the folder structure of the bifacial_radiance Scene in the designated testfolder in your computer, and it should look like this:
# 
# 
# ![Folder Structure](../images_wiki/Journal1Pics/folderStructure.PNG)

# <a id='step3'></a>

# ## 3. Set the Albedo

# To see more options of ground materials available (located on ground.rad), run this function without any input. 

# In[5]:


# Input albedo number or material name like 'concrete'.  
demo.setGround()  # This prints available materials.


# If a number between 0 and 1 is passed, it assumes it's an albedo value. For this example, we want a high-reflectivity rooftop albedo surface, so we will set the albedo to 0.62

# In[6]:


albedo = 0.62
demo.setGround(albedo)


# <a id='step4'></a>

# ## 4. Download and Load Weather Files
# 
# There are various options provided in bifacial_radiance to load weatherfiles. getEPW is useful because you just set the latitude and longitude of the location and it donwloads the meteorologicla data for any location. 

# In[7]:


# Pull in meteorological data using pyEPW for any global lat/lon
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.


# The downloaded EPW will be in the EPWs folder.
# 
# To load the data, use readWeatherFile. This reads EPWs, TMY meterological data, or even your own data as long as it follows TMY data format (With any time resoultion).

# In[8]:


# Read in the weather data pulled in above. 
metdata = demo.readWeatherFile(epwfile, coerce_year=2001) 


# <a id='step5'></a>

# ## 5. Generate the Sky.
# 
# Sky definitions can either be for a single time point with gendaylit function,
# or using gencumulativesky to generate a cumulativesky for the entire year.
# 

# In[9]:


fullYear = True
if fullYear:
    demo.genCumSky() # entire year.
else:
    timeindex = metdata.datetime.index(pd.to_datetime('2001-06-17 12:0:0 -7'))
    demo.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)


# The method gencumSky calculates the hourly radiance of the sky hemisphere by dividing it into 145 patches. Then it adds those hourly values to generate one single <b> cumulative sky</b>. Here is a visualization of this patched hemisphere for Richmond, VA, US. Can you deduce from the radiance values of each patch which way is North?
# 
# ![Example of the hemisphere cumulative sky](../images_wiki/Journal1Pics/cumulativesky.png)
# 
# Answer: Since Richmond is in the Northern Hemisphere, the modules face the south, which is where most of the radiation from the sun is coming. The north in this picture is the darker blue areas.

# <a id='step6'></a>

# ## 6. DEFINE a Module type
# 
# You can create a custom PV module type. In this case we are defining a module named "test-module", in landscape. The x value defines the size of the module along the row, so for landscape modules x > y. This module measures y = 0.984 x = 1.695. 
# 
# 
# <div class="alert alert-success">
# Modules in this example are 100% opaque. For drawing each cell, makeModule needs more inputs with cellLevelModule = True. You can also specify a lot more variables in makeModule like multiple modules, torque tubes, spacing between modules, etc. Reffer to the <a href="https://bifacial-radiance.readthedocs.io/en/latest/generated/bifacial_radiance.RadianceObj.makeModule.html#bifacial_radiance.RadianceObj.makeModule"> Module Documentation </a> and read the following jupyter journals to explore all your options.
# </div>
# 

# In[10]:



module_type = 'test-module' 
module = demo.makeModule(name=module_type,x=1.695, y=0.984)
print(module)


# In case you want to use a pre-defined module or a module you've created previously, they are stored in a JSON format in data/module.json, and the options available can be called with printModules:

# In[11]:



availableModules = demo.printModules()


# <a id='step7'></a>

# ## 7. Make the Scene
# 
#  The sceneDicitonary specifies the information of the scene, such as number of rows, number of modules per row, azimuth, tilt, clearance_height (distance between the ground and lowest point of the module) and any other parameter. 
#  
#  Azimuth gets measured from N = 0, so for South facing modules azimuth should equal 180 degrees
# 

# In[12]:



sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 


# To make the scene we have to create a Scene Object through the method makeScene. This method will create a .rad file in the objects folder, with the parameters specified in sceneDict and the module created above.  You can alternatively pass a string with the name of the `moduletype`.

# In[13]:



scene = demo.makeScene(module,sceneDict)


# <a id='step8'></a>

# ## 8. COMBINE the Ground, Sky, and the Scene Objects
# 
# Radiance requires an "Oct" file that combines the ground, sky and the scene object into it. 
# The method makeOct does this for us.

# In[14]:



octfile = demo.makeOct(demo.getfilelist())  


# To see what files got merged into the octfile, you can use the helper method getfilelist. This is useful for advanced simulations too, specially when you want to have different Scene objects in the same simulation, or if you want to add other custom elements to your scene (like a building, for example)

# In[15]:



demo.getfilelist()


# <a id='step9'></a>

# ## 9. ANALYZE and get Results
# 
# Once the octfile tying the scene, ground and sky has been created, we create an Analysis Object. We first have to create an Analysis object, and then we have to specify where the sensors will be located with moduleAnalysis. 
# 

# First let's create the Analysis Object

# In[16]:



analysis = AnalysisObj(octfile, demo.basename)


# Then let's specify the sensor location. If no parameters are passed to moduleAnalysis, it will scan the center module of the center row:

# In[17]:



frontscan, backscan = analysis.moduleAnalysis(scene)


# The frontscan and backscan include a linescan along a chord of the module, both on the front and back. 
# 
# ![Simple example for south facing module](../images_wiki/Journal1Pics/frontscan_backscan.png)
# Analysis saves the measured irradiances in the front and in the back on the results folder.  Prints out the ratio of the average of the rear and front irradiance values along a chord of the module.

# In[18]:



results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  


# The results are also automatically saved in the results folder. Some of our input/output functions can be used to read the results and work with them, for example:

# In[19]:



load.read1Result('results\irr_tutorial_1.csv')


# As can be seen in the results for the *Wm2Front* and *WM2Back*, the irradiance values are quite high. This is because a cumulative sky simulation was performed on <b> step 5 </b>, so this is the total irradiance over all the hours of the year that the module at each sampling point will receive. Dividing the back irradiance average by the front irradiance average will give us the bifacial gain for the year:
# 
# ![Bifacial Gain in Irradiance Formula](../images_wiki/Journal1Pics/BGG_Formula.PNG)
# 
# Assuming that our module has a bifaciality factor (rear to front performance) of 90%, our <u> bifacial gain </u> is of:

# In[20]:



bifacialityfactor = 0.9
print('Annual bifacial ratio: %0.2f ' %( np.mean(analysis.Wm2Back) * bifacialityfactor / np.mean(analysis.Wm2Front)) )


# <a id='step10'></a>

# ## 10. View / Render the Scene
# 
# If you used gencumsky or gendaylit, you can view the <b> Scene </b> by navigating on a command line to the folder and typing:
# 
# ***objview materials\ground.rad objects\test-module_C_0.20000_rtr_3.00000_tilt_10.00000_20modsx7rows_origin0,0.rad***
# 

# In[20]:



## Comment the ! line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

# !objview materials\ground.rad objects\test-module_C_0.20000_rtr_3.00000_tilt_10.00000_20modsx7rows_origin0,0.rad


# This <b> objview </b> has 3 different light sources of its own, so the shading is not representative.
# 
# ONLY If you used <b> gendaylit </b>, you can view the scene correctly illuminated with the sky you generated after generating the oct file, with 
# 
# ***rvu -vf views\front.vp -e .01 tutorial_1.oct***

# In[21]:



## Comment the line below to run rvu from the Jupyter notebook instead of your terminal.
## Simulation will stop until you close the rvu window

#!rvu -vf views\front.vp -e .01 tutorial_1.oct


# 
# The <b> rvu </b> manual can be found here: manual page here: http://radsite.lbl.gov/radiance/rvu.1.html
# 
# Or you can also use the code below from bifacial_radiance to generate an HDR rendered image of the scene. You can choose from front view or side view in the views folder:

# In[22]:


# Print a default image of the module and scene that is saved in /images/ folder. (new in v0.4.2)
scene.saveImage()

# Make a color render and falsecolor image of the scene.
analysis.makeImage('side.vp')
analysis.makeFalseColor('side.vp')


# This is how the False Color image stored in images folder should look like:
# 
# ![OpenHDR image example of False color](../images_wiki/Journal1Pics/openhdr_FalseColorExample.PNG)

# Files are saved as .hdr (high definition render) files.  Try LuminanceHDR viewer (free) to view them, or https://viewer.openhdr.org/ 
# 
# 
