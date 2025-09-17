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


# # 8 - Electrical Mismatch Method
# 
# Nonuniform rear-irradiance on bifacial PV systems can cause additional mismatch loss, which may not be appropriately captured in PV energy production estimates and software.
# 
# <img src="../images_wiki/AdvancedJournals/Mismatch_Definition_Example.PNG" width="600">
# 
# The **analysis.py** module in bifacial_radiance comes with functions to calculate power output, electrical mismatch, and some other irradiance calculations. This is the procedure used for this proceedings and submitted journals, which have much more detail on the procedure. 
# 
# * Deline, C., Ayala Pelaez, S., MacAlpine, S., Olalla, C. Estimating and Parameterizing Mismatch Power Loss in Bifacial Photovoltaic Systems. Progress in PV 2020, https://doi.org/10.1002/pip.3259
# 
# * Deline C, Ayala Pelaez S, MacAlpine S, Olalla C. Bifacial PV System Mismatch Loss Estimation & Parameterization. Presented in: 36th EU PVSEC, Marseille Fr. Slides: https://www.nrel.gov/docs/fy19osti/74885.pdf. Proceedings: https://www.nrel.gov/docs/fy20osti/73541.pdf
# 
# * Ayala Pelaez S, Deline C, MacAlpine S, Olalla C. Bifacial PV system mismatch loss estimation. Poster presented at the 6th BifiPV Workshop, Amsterdam 2019. https://www.nrel.gov/docs/fy19osti/74831.pdf and http://bifipv-workshop.com/index.php?id=amsterdam-2019-program 
# 
# Ideally **mismatch losses M** should be calculated for the whole year, and then the **mismatch loss factor to apply to Grear "Lrear"** required by due diligence softwares can be calculated:
# 
# <img src="../images_wiki/AdvancedJournals/Lrear_solving.PNG" width="400">
# 
# In this journal we will explore calculating mismatch loss M for a reduced set of hours. A procedure similar to that in Tutorial 3 will be used to generate various hourly irradiance measurements in the results folder, which the mismatch.py module will load and analyze. Analysis is done with PVMismatch, so this must be installed.
# 
# ## STEPS:
#     1. Run an hourly simulation
#     2. Do mismatch analysis on the results.
# 
# 

# <a id='step1'></a>

# ### 1. Run an hourly simulation
# 
# This will generate the results over which we will perform the mismatch analysis. Here we are doing only 1 day to make this faster.

# In[2]:


import bifacial_radiance
import os 
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'/ 'Tutorial_08')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)

simulationName = 'tutorial_8'
moduletype = "PVmodule"
albedo = 0.25 
lat = 37.5   
lon = -77.6

# Scene variables
nMods = 20
nRows = 7
hub_height = 1.5 # meters
gcr = 0.33

# Traking parameters
cumulativesky = False
limit_angle = 60 
angledelta = 0.01 
backtrack = True 

#makeModule parameters
x = 1
y = 2
xgap = 0.01
zgap = 0.05
ygap = 0.0  # numpanels=1 anyways so it doesnt matter anyway
numpanels = 1
axisofrotationTorqueTube = True
diameter = 0.1
tubetype = 'Oct'    
material = 'black'
tubeParams = {'diameter':diameter,
              'tubetype':tubetype,
              'material':material,
              'axisofrotation':axisofrotationTorqueTube,
              'visible':True}

# Analysis parmaeters
startdate = '11_06_08'       # Options: mm_dd, mm_dd_HH, mm_dd_HHMM, YYYY-mm-dd_HHMM
enddate = '11_06_10'
sensorsy = 12

demo = bifacial_radiance.RadianceObj(simulationName, path=testfolder)  
demo.setGround(albedo) 
epwfile = demo.getEPW(lat,lon) 
metdata = demo.readWeatherFile(epwfile, starttime=startdate, endtime=enddate) 
mymodule = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap,
                           ygap = ygap, zgap=zgap, numpanels=numpanels, tubeParams=tubeParams)
pitch = mymodule.sceney/gcr
sceneDict = {'pitch':pitch,'hub_height':hub_height, 'nMods': nMods, 'nRows': nRows}  
demo.set1axis(limit_angle = limit_angle, backtrack = backtrack, gcr = gcr, cumulativesky = cumulativesky)
demo.gendaylit1axis()
demo.makeScene1axis(module=mymodule, sceneDict=sceneDict) 
demo.makeOct1axis()
demo.analysis1axis(sensorsy = sensorsy);


# <a id='step2'></a>

# ### 2. Do mismatch analysis on the results
# 
# There are various things that we need to know about the module at this stage.
# 
# * Orientation: If it was simulated in portrait or landscape orientation. 
# * Number of cells in the module: options right now are 72 or 96
# * Bifaciality factor: this is how well the rear of the module performs compared to the front of the module, and is a spec usually found in the datasheet. 
# 
# Also, if the number of sampling points (`sensorsy`) from the result files does not match the number of cells along the panel orientation, downsampling or upsamplinb will be peformed. For this example, the module is in portrait mode (y > x), so there will be 12 cells along the collector width (**numcellsy**), and that's why we set **sensorsy = 12** during the analysis above. 
# 
# These are the re-sampling options. To downsample, we suggest sensorsy >> numcellsy (for example, we've tested sensorsy = 100,120 and 200)
#     - Downsamping by Center - Find the center points of all the sensors passed 
#     - Downsampling by Average - averages irradiances that fall on what would consist on the cell
#     - Upsample
# 

# In[3]:


resultfolder = os.path.join(testfolder, 'results')
writefiletitle = "Mismatch_Results.csv" 

portraitorlandscape='portrait' # Options are 'portrait' or 'landscape'
bififactor=0.9 # Bifaciality factor DOES matter now, as the rear irradiance values will be multiplied by this factor.
numcells= 72# Options are 72 or 96 at the moment.
downsamplingmethod = 'byCenter' # Options are 'byCenter' or 'byAverage'.
bifacial_radiance.mismatch.analysisIrradianceandPowerMismatch(testfolder=resultfolder, writefiletitle=writefiletitle, portraitorlandscape=portraitorlandscape, 
                                                              bififactor=bififactor, numcells=numcells)

print ("Your hourly mismatch values are now saved in the file above! :D")


# <div class="alert alert-warning">
# We hope to add more content to this journal for next release so check back! Particularly how to use the Mad_fn to make the mismatch calculation faster, as per the proceedings and publication above!
# </div>
