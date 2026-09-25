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


# In[2]:


import os
from pathlib import Path

testfolder = 'TEMP'
if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print ("Your simulation will be stored in %s" % testfolder)


# In[3]:


import bifacial_radiance
import numpy as np

rad_obj = bifacial_radiance.RadianceObj('Si', str(testfolder)) 


# <a id='step1'></a>

# ## 1. Making Collectors for each number panel and xgap case

# In[4]:


rad_obj.setGround(0.2)  # This prints available materials.


# In[5]:


epwfile = rad_obj.getEPW(lat = 42.98, lon = -81.24)


# In[6]:


startdate = '04_01'     
enddate = '10_31'
metdata = rad_obj.readWeatherFile(epwfile, coerce_year=2025, starttime=startdate, endtime=enddate)


# In[7]:


metdata


# In[8]:


#rad_obj.genCumSky() # entire year.
metdata.datetime[1035] # Selected for having GHI = 982 , clear sky day. # ('2025-06-13 13:00:00-0500', tz='UTC-05:00')
timeindex = metdata.datetime.index(pd.to_datetime('2025-06-13 13:00:00 -5'))
rad_obj.gendaylit(timeindex)  # Noon, June 17th (timepoint # 4020)


# In[9]:


# CdTe


# In[10]:


description = 'CdTe 60percent transmission'
materialname = 'cdte_60trans'
RTrans = 0.6
GTrans = 0.6 
BTrans = 0.6
materialtype = 'glass'
rad_obj.addMaterial(material=materialname, Rrefl=RTrans, Grefl=GTrans, Brefl=BTrans, materialtype='glass', comment=description)


# In[11]:


description = 'CdTe 70percent transmission'
materialname = 'cdte_70trans'
RTrans = 0.7
GTrans = 0.7 
BTrans = 0.7
materialtype = 'glass'
rad_obj.addMaterial(material=materialname, Rrefl=RTrans, Grefl=GTrans, Brefl=BTrans, materialtype='glass', comment=description)


# In[12]:


description = 'CdTe 80percent transmission'
materialname = 'cdte_80trans'
RTrans = 0.8
GTrans = 0.8 
BTrans = 0.8
materialtype = 'glass'
rad_obj.addMaterial(material=materialname, Rrefl=RTrans, Grefl=GTrans, Brefl=BTrans, materialtype='glass', comment=description)


# In[16]:


cdTe60 = rad_obj.makeModule(name='cdTe60',x=1.2,y=0.6, numpanels=2, xgap = 0.15, modulematerial='cdte_60trans')
cdTe70 = rad_obj.makeModule(name='cdTe70',x=1.2,y=0.6, numpanels=2, xgap = 0.15, modulematerial='cdte_70trans')
cdTe80 = rad_obj.makeModule(name='cdTe80r',x=1.2,y=0.6, numpanels=2, xgap = 0.15, modulematerial='cdte_80trans')


# In[17]:


sceneDict1 = {'tilt':34,'pitch':5.69,'clearance_height':2.0,'azimuth':180, 'nMods': 3, 'nRows': 1, 'originx': -4.05, 'originy': 0, 'appendRadfile':True} 
sceneDict2 = {'tilt':34,'pitch':5.69,'clearance_height':2.0,'azimuth':180, 'nMods': 3, 'nRows': 1, 'originx': 0, 'originy': 0, 'appendRadfile':True} 
sceneDict3 = {'tilt':34,'pitch':5.69,'clearance_height':2.0,'azimuth':180, 'nMods': 4, 'nRows': 1, 'originx': 4.05, 'originy': 0, 'appendRadfile':True}


sceneObj1 = rad_obj.makeScene(cdTe60, sceneDict1)  
sceneObj2 = rad_obj.makeScene(cdTe70, sceneDict2, append=True)  
sceneObj3 = rad_obj.makeScene(cdTe80, sceneDict3, append=True)  


# In[18]:


octfile = rad_obj.makeOct(rad_obj.getfilelist()) 


# In[19]:


rad_obj.getfilelist()


# In[ ]:


#!objview materials\ground.rad objects\\Si_44_C_0.70_rtr_5.69_tilt_34_3modsx1rows_origin3.827,0.rad


# In[20]:


#!rvu -vf views\front.vp -e .02 -pe 0.3 -vp 0 -13.5 18.5 -vd 0 0.7 -0.7 Si.oct


# In[21]:


analysis = bifacial_radiance.AnalysisObj()


# In[22]:


groundscan = analysis.groundAnalysis(sceneObj2, modWanted=2, rowWanted=1, sensorsground=2, sensorsgroundx=2)


# In[23]:


groundscan


# In[ ]:


# Faster
#groundscan['xstart'] = -6.4
#groundscan['ystart'] = -1.2
#groundscan['Nx'] = 12
#groundscan['Ny'] = 26
#groundscan['yinc'] = 0.5
#groundscan['sx_xinc'] = 0.5
#groundscan['sx_yinc'] = 0.0


# In[24]:


# SUPER RESOLUTION 5 cm
groundscan['xstart'] = -7
groundscan['ystart'] = -1
groundscan['Nx'] = 307
groundscan['Ny'] = 120
groundscan['yinc'] = 0.05
groundscan['sx_xinc'] = 0.05
groundscan['sx_yinc'] = 0.0


# In[25]:


analysis.analysis(octfile, '_CdTE_test_noon_5cm', groundscan)  # compare the back vs front irradiance


# In[27]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Load CSV ---
df = pd.read_csv(r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\docs\Studies\TEMP\results\irr__CdTE_test_noon_5cm_Row1_Module2.csv')   # columns: x, y, z, mattype, Wm2Front

# --- Sort so y increases first, then x ---
df = df.sort_values(['x', 'y'])

# --- Get unique coordinate axes ---
xs = np.sort(df['x'].unique())
ys = np.sort(df['y'].unique())

# --- Reshape Wm2Front into 2D array ---
# IMPORTANT: df is sorted so reshape works correctly
Z = df['Wm2Front'].values.reshape(len(xs), len(ys))

# --- Plot heatmap ---
plt.figure(figsize=(8,6))
plt.imshow(Z.T, origin='lower',
           extent=[xs.min(), xs.max(), ys.min(), ys.max()],
           aspect='auto')

plt.colorbar(label='Ground Irradiance W/m²')
plt.xlabel('X coordinate (West <-> East) [m]')
plt.ylabel('yY coordinate (South <-> North) [m]')
#plt.title('Ground Irradiance')
plt.show()


# In[28]:


## Seasonal
rad_obj.genCumSky() # entire year.
octfile = rad_obj.makeOct(rad_obj.getfilelist()) 
rad_obj.getfilelist()


# In[29]:


analysis.analysis(octfile, '_CdTE_test_Season_5cm', groundscan)  # compare the back vs front irradiance


# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Load CSV ---
df = pd.read_csv(r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\docs\Studies\TEMP\results\irr__CdTE_test_Season_5cm_Row1_Module2.csv')

# --- Sort so y increases first, then x ---
df = df.sort_values(['x', 'y'])

# --- Get unique coordinate axes ---
xs = np.sort(df['x'].unique())
ys = np.sort(df['y'].unique())

# --- Reshape Wm2Front into 2D array ---
Z = df['Wm2Front'].values.reshape(len(xs), len(ys))

# --- Convert Wh/m² → kWh/m² ---
Z = Z / 1000.0     # <<< THIS LINE FIXES THE 1e6 SCALE ISSUE

# --- Plot heatmap ---
plt.figure(figsize=(8,6))
plt.imshow(Z.T, origin='lower',
           extent=[xs.min(), xs.max(), ys.min(), ys.max()],
           aspect='auto')

plt.colorbar(label='Ground Insolation kWh/m²-season')
plt.xlabel('X coordinate (West <-> East) [m]')
plt.ylabel('Y coordinate (South <-> North) [m]')
plt.show()


# In[ ]:


print("Max Wh/m²-season:", df['Wm2Front'].max())
print("Max kWh/m²-season:", df['Wm2Front'].max() / 1000)


# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Load CSV ---
df = pd.read_csv(r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\docs\Studies\TEMP\results\irr__CdTE_test_Season_5cm_Row1_Module2.csv')

# --- Sort so y increases first, then x ---
df = df.sort_values(['x', 'y'])

# --- Get unique coordinate axes ---
xs = np.sort(df['x'].unique())
ys = np.sort(df['y'].unique())

# --- Reshape Wm2Front into 2D array ---
Z = df['Wm2Front'].values.reshape(len(xs), len(ys))

# --- Normalize by max to get Insolation Fraction ---
Zmax = Z.max()
Z = Z / Zmax       # values now between 0 and 1

# --- Plot heatmap ---
plt.figure(figsize=(8,6))
plt.imshow(Z.T, origin='lower',
           extent=[xs.min(), xs.max(), ys.min(), ys.max()],
           aspect='auto',
           vmin=0, vmax=1)   # enforce 0–1 scale

plt.colorbar(label='Insolation Fraction (0–1)')
plt.xlabel('X coordinate (West <-> East) [m]')
plt.ylabel('Y coordinate (South <-> North) [m]')
plt.show()

print("Max value in dataset:", Zmax)


# In[ ]:


target_x = -4
target_y = 0.2

# compute distance to each row
df['dist'] = np.sqrt((df['x'] - target_x)**2 + (df['y'] - target_y)**2)

# pick closest row
closest = df.loc[df['dist'].idxmin()]

print("Closest grid point:", closest[['x', 'y']].to_dict())
print("Wm2Front value:", closest['Wm2Front'])
print("Normalized value:", closest['Wm2Front'] / df['Wm2Front'].max())


# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Load CSV ---
df = pd.read_csv(r'C:\Users\sayala\Documents\GitHub\bifacial_radiance\docs\Studies\TEMP\results\irr__CdTE_test_Season_5cm_Row1_Module2.csv')

# --- Sort so y increases first, then x ---
df = df.sort_values(['x', 'y'])

# --- Get coordinate grids ---
xs = np.sort(df['x'].unique())
ys = np.sort(df['y'].unique())

# --- Reshape data ---
Z = df['Wm2Front'].values.reshape(len(xs), len(ys))

# --- Normalize for Insolation Fraction ---
Zmax = Z.max()
Znorm = Z / Zmax

# --- Create meshgrid for contour plot ---
X, Y = np.meshgrid(xs, ys, indexing='ij')

# --- Plot contour ---
plt.figure(figsize=(8,6))
contour = plt.contourf(X, Y, Znorm, levels=20, cmap='viridis')

plt.colorbar(contour, label='Insolation Fraction (0–1)')
plt.xlabel('X coordinate (m)')
plt.ylabel('Y coordinate (m)')
plt.title('Insolation Fraction Contour Plot')

plt.show()


# In[ ]:




