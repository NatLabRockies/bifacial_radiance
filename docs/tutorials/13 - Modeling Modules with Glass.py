#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This information helps with debugging and getting support :)
import sys, platform
import pandas as pd
import bifacial_radiance as br
print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("bifacial_radiance version ", br.__version__)


# # 13 - Modeling Modules with Glass
# 
# 
# This journal shows how to add glass to the modules. It also shows how to sample irradiance on the surface of the glass, as well as on the surface of the module. Surface of the module is slightlyt less irradiance due to fresnel losses (a.k.a. Angle of Incidence losses (AOI))
# 
# Some examples of the module with glass we'll create:
# 
# ![Bottom Reflection](../images_wiki/Journal13Pics/Glass_bottom_reflection.PNG)
# ![Side closeup](../images_wiki/Journal13Pics/Glass_side_closeup.PNG)
# ![Tiled view](../images_wiki/Journal13Pics/Glass_tilted_reflection.PNG)
# 

# In[1]:


import os
from bifacial_radiance import *
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP' / 'Tutorial_13')
if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print ("Your simulation will be stored in %s" % testfolder)


# In[2]:


demo = RadianceObj('tutorial_13',str(testfolder))  
demo.setGround(0.30)  # This prints available materials.
epwfile = demo.getEPW(lat = 37.5, lon = -77.6)  # This location corresponds to Richmond, VA.
metdata = demo.readWeatherFile(epwfile) 
demo.gendaylit(8)  # January 1 4pm (timepoint # 8)\


# ## Modeling example with glass

# In[3]:


module_type = 'test-module' 

numcellsx = 6
numcellsy = 12
xcell = 0.156
ycell = 0.156
xcellgap = 0.02
ycellgap = 0.02

visible = True
diameter = 0.15
tubetype = 'round'
material = 'Metal_Grey'
xgap = 0.1
ygap = 0
zgap = 0.05
numpanels = 1
axisofrotationTorqueTube = False
glass = True

cellLevelModuleParams = {'numcellsx': numcellsx, 'numcellsy':numcellsy, 
                         'xcell': xcell, 'ycell': ycell, 'xcellgap': xcellgap, 'ycellgap': ycellgap}

mymodule = demo.makeModule(name=module_type, x=1, y=1, xgap=xgap, ygap=ygap, 
                           zgap=zgap, numpanels=numpanels, glass=glass, z=0.0002)
mymodule.addTorquetube(material=material, tubetype=tubetype, diameter=diameter,
                      axisofrotation=axisofrotationTorqueTube, recompile=False)
mymodule.addCellModule(**cellLevelModuleParams)

sceneDict = {'tilt':0,'pitch':5.5,'hub_height':1.0,'azimuth':90, 'nMods': 20, 'nRows': 1, 'originx':0, 'originy':0} 
scene = demo.makeScene(module_type, sceneDict)
octfile = demo.makeOct(demo.getfilelist())  


# ## Advanced Rendering:
# 
# The images at the beginning of the journal can be made pretty with advanced rendering. This is the workflow:
# 
#     rvu -> rpict -> pcond -> pfilt -> ra_tiff -> convert
# 
# In detail:
# 
# ***1. Use rvu to view the oct file***
# 
#     rvu 1axis_07_01_08.oct 
# 
# Use aim and origin to move around, zoom in/out, etc. Save a view file with view render.
# 
# ***2. Run rpict to render the image to hdr***
# 
# This is the time consuming step. It takes between 1 and 3 hours depending on how complex the geometry is.
# 
#     rpict -x 4800 -y 4800 -i -ps 1 -dp 530 -ar 964 -ds 0.016 -dj 1 -dt 0.03 -dc 0.9 -dr 5 -st 0.12 -ab 5 -aa 0.11 -ad 5800 -as 5800 -av 25 25 25 -lr 14 -lw 0.0002 -vf render.vf bifacial_example.oct > render.hdr
# 
# 
# ***3. Run pcond to mimic human visual response***
# 
#     pcond -h render.hdr > render.pcond.hdr
# 
# 
# ***4. Resize and adjust exposure with pfilt***
# 
#     pfilt -e +0.2 -x /4 -y /4 render.pcond.hdr > render.pcond.pfilt.hdr
# 
# 
# ***5. Convert hdr to tif***
# 
#     ra_tiff render.pcond.pfilt.hdr render.tif
# 
# 
# ***6. Convert tif to png with imagemagick convert utility***
# 
#     convert render.tif render.png
# 
# 
# ***7. Annotate the image with convert***
# 
#     convert render.png -fill black -gravity South -annotate +0+5 'Created with NREL bifacial_radiance https://github.com/NatLabRockies/bifacial_radiance' render_annotated.png
# 

# In[4]:


analysis = AnalysisObj(octfile, demo.basename)


# ## Scanning Outside of the module, the surface of the glass

# In[5]:


frontscan, backscan = analysis.moduleAnalysis(scene)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  
load.read1Result('results\irr_tutorial_13.csv')


# ## Scanning Inside of the module, the surface of the cells

# In[6]:


frontscan, backscan = analysis.moduleAnalysis(scene, frontsurfaceoffset=0.05, backsurfaceoffset = 0.05)
results = analysis.analysis(octfile, demo.basename, frontscan, backscan)  
load.read1Result('results\irr_tutorial_13.csv')


# In[ ]:




