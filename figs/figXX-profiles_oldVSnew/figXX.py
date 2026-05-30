import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patheffects
import pandas

from shapely.geometry import LineString
import shapefile
import rasterstats
import fiona
import datetime as dt

from PIL import Image

import glob
import os

from scipy.optimize import curve_fit

def model(x, m):
    return m * x

plt.style.use('../moraine.mplstyle')

def convert_date_format(date_string):
    """
    Converts a date string from YYYYmmdd format to YYYY/mm/dd format.

    Args:
        date_string (str): The date string in YYYYmmdd format (e.g., "20231026").

    Returns:
        str: The date string in YYYY/mm/dd format (e.g., "2023/10/26").
    """
    # Parse the input string into a datetime object
    date_object = dt.datetime.strptime(date_string, "%Y%m%d")

    # Format the datetime object into the desired output string format
    formatted_date = date_object.strftime("%Y-%m-%d")

    return formatted_date

photo = Image.open('20200731-163852.jpg')

#%%

cm = 1/2.54
fig_width = 15.6*cm
fig_height = 19.2*cm
fig, ax = plt.subplots(2, 1, figsize=(fig_width,fig_height))
ax = ax.ravel()


full_width = 13.5
width = 6.2
height = 8
ax_width = full_width*cm/fig_width
ax_height = height*cm/fig_height
cbar_height = 0.2*cm/fig_height
left = 1.8*cm/fig_width
bot = 1.1*cm/fig_height
ygap = 0.6*cm/fig_height
xgap = 0.6*cm/fig_width #(full_width-2*width)*cm/fig_width


# ax1 = plt.axes([left, bot+ygap, ax_width, ax_height])
# ax2 = plt.axes([left+ax_width+xgap, bot+ygap, ax_width, ax_height])



#ax[0].set_position([left, bot + (2*ygap + ax_height)*2, 2*ax_width+xgap, (2*ax_width+xgap)*3/5])
ax[0].set_position([left, bot + 2*ygap + ax_height, ax_width, ax_height])
ax[1].set_position([left, bot, ax_width, ax_height])

#ax[2].set_position([left+0.6*ax_width, bot + 2*ygap + 1.6*ax_height, 0.38*ax_width, 0.38*ax_height])

axInset = ax[0].inset_axes([0.62, 0.6, 0.36, 0.35])

#ax[0].set_ylabel('Elevation [m]')
ax[0].set_ylabel('Elevation [m]')
ax[1].set_ylabel('Elevation [m]')

ax[0].set_xlabel('Longitudinal coordinate [m]')
ax[1].set_xlabel('Longitudinal coordinate [m]')

# ax[0].set_xticklabels('')
# ax[0].set_yticklabels('')
# ax[0].set_xticks([])
# ax[0].set_yticks([])

#ax[2].set_yticklabels('')

xmin = -800
xmax = 200
ymin = -25
ymax = 125

ax[0].set_xlim([xmin, xmax])
ax[0].set_ylim([ymin, ymax])
ax[0].set_xticks(np.arange(xmin,xmax+1,100))
ax[0].set_yticks(np.arange(ymin,ymax+1,25))

ax[1].set_xlim([xmin, xmax])
ax[1].set_ylim([ymin, ymax])
ax[1].set_xticks(np.arange(xmin,xmax+1,100))
ax[1].set_yticks(np.arange(ymin,ymax+1,25))

axInset.set_xlim([-200,150])
axInset.set_ylim([5,20])
axInset.set_yticks([])
axInset.set_xticks([])
#ax[2].set_xticks(np.arange(-800,200,200))

#ax[1].set_yticks([-25,0,25,50,75,100,125])


txt_space = 0.35 # cm

panel_labels = ['a', 'b']#, 'c']

for k in np.arange(0,len(panel_labels)):
    ax[k].text(txt_space/full_width, 1-txt_space/height, panel_labels[k], transform=ax[k].transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1010) 


ax[0].indicate_inset_zoom(axInset, edgecolor="black")
# ax[0].set_xlim([0,2500])
# ax[0].set_ylim([0,1500])
# ax[0].invert_yaxis()
#%%

RES2016 = 'Radar_points_archive_2016_Truffer.csv'

DEM2015 = 'Taku_terminus.tif'
terminus2015 = '/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/Taku_Aug2_2015_terminus.shp'

drone_files = sorted(glob.glob('/hdd2/taku/uav/surveys/02_takuGrid/taku_DEM_*.tif'))
index = [4, 11, 15, 19]
drone_files = [drone_files[x] for x in index]
color_id = np.linspace(0.5, 1, len(drone_files))

shpBase = '/hdd2/taku/uav/surveys/06_terminusPosition/'
termShp = [shpBase + 'taku_' + os.path.basename(x)[9:17] + '_terminus.shp' for x in drone_files]
dates = [convert_date_format(os.path.basename(x)[9:17]) for x in drone_files]

# import terminus and create LineString
with fiona.open(terminus2015, 'r') as source:
    for feature in source:
        xy = feature['geometry']['coordinates']

termLine2015 = LineString(xy)




### Read 2016 radar data, and assume that reflection is directly below the Tx-Rx pair
data = pandas.read_csv(RES2016)
data['thickness'] = np.sqrt(data['Calculated path distance (m)']**2/4 - data['Rx-Tx spacing (m)']**2/4)

## get radar points that are near the profiles; these were determine by comparing in QGIS
# western profile
indexWest = [34, 35, 36, 37, 38, 39]
dataWest = data.loc[data['Radar station'].isin(indexWest)]
dataWest = dataWest.sort_values(by = 'thickness', ascending=False)

# eastern profile
indexEast = [29, 30, 31, 128, 54, 55, 56] # maybe also 53, but it looks bad
dataEast = data.loc[data['Radar station'].isin(indexEast)]
dataEast = dataEast.sort_values(by = 'thickness', ascending=False)

dataList = [dataWest, dataEast]

### Now import the shapefile that contains the two profiles
profile_shp = './profile.shp'

for j in np.arange(0,2):

    profile = shapefile.Reader(profile_shp).shapes()[j]
    profile = LineString(profile.points)
    
    
    # shapefile only has start and end points; add points in between
    X, Y = np.array(profile.coords.xy)
    X, Y = np.linspace(X[0], X[-1], 1000, endpoint=True), np.linspace(Y[0], Y[-1], 1000, endpoint=True) 
    
    # stack the new points and create a LineString for extract profiles with rasterstats
    XY = np.vstack((X,Y)).T
    profile = LineString(XY)
    
    ### Extra surface elevations from DEMs
    elev2015 = rasterstats.point_query(profile, DEM2015)[0]
    
    
    # UTM coordinates of starting point of the profile
    X0 = X[0]
    Y0 = Y[0]
    
    # substract starting coordinates so that the profile starts at (0,0)
    X = X-X0
    Y = Y-Y0
    
    # determine azimuth of profile and create rotation matrix to find distance along the profile
    theta = np.arctan(Y[-1]/X[-1])
    rot = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
    XY = np.matmul(rot, np.vstack((X,Y)))
    
    
    # find where the profile intersects the 2015 terminus, relative to profile starting point
    termPt = profile.intersection(termLine2015)
    termEasting = termPt.coords.xy[0] - X0
    termNorthing = termPt.coords.xy[1] - Y0
    termElev = np.array(rasterstats.point_query(termPt, DEM2015))
    
    termXY = np.matmul(rot, np.vstack((termEasting, termNorthing)))
    xTerm2015 = termXY[0] # terminus location in 2015
    
    x_prof = XY[0,:]-xTerm2015
    
    # Now find the loax.indicate_inset_zoom(ax_inset, edgecolor="black")cation of the radar points in the rotated coordinate system
    Tx_x = (dataList[j]['Tx_x']-X0).values
    Tx_y = (dataList[j]['Tx_y']-Y0).values
    XY_radar = np.matmul( rot, np.vstack((Tx_x, Tx_y)) )
    
    x_radar = XY_radar[0,:] - xTerm2015
    
    # extract the thickness and calculate the bed elevation
    thickness = dataList[j]['thickness'].values
    bed_radar = dataList[j]['Tx_z'].values-thickness
    
    x_radar = np.append(x_radar, 0)
    bed_radar = np.append(bed_radar, termElev)
    
    # add terminus position (STILL TO DO)
    #x_radar = np.append(x_radar, 0)
    #bed_radar = np.append(bed_radar, 7.55)
        
    ax[j].plot(x_prof, elev2015, color='r', label='2015-08-02')
    #popt, _ = curve_fit(model, x_radar, bed_radar-7.55 )
    #slope = popt[0]
    
    if j==0:
        axInset.plot(x_prof, elev2015, color='r', label='2015-08-02')
    
    for k in np.arange(0, len(drone_files)):
        elevDrone = rasterstats.point_query(profile, drone_files[k])[0]
        ax[j].plot(x_prof, elevDrone, color=plt.cm.Blues(color_id[k]))
    
        if j==0:
            axInset.plot(x_prof, elevDrone, color=plt.cm.Blues(color_id[k]))
    
        # import terminus for given file and create LineString
        with fiona.open(termShp[k], 'r') as source:
            for feature in source:
                xy = feature['geometry']['coordinates']
        
            termLine = LineString(xy)
    
            termPt = profile.intersection(termLine)
    
            # relative to (X0, Y0)
            termEasting = termPt.coords.xy[0] - X0
            termNorthing = termPt.coords.xy[1] - Y0
            termElev = np.array(rasterstats.point_query(termPt, drone_files[k]))
    
            termXY = np.matmul(rot, np.vstack((termEasting, termNorthing)))
            xTerm = termXY[0] - xTerm2015 # terminus location in 2015
    
        ax[j].plot(xTerm, termElev, '.', color=plt.cm.Blues(color_id[k]), markersize=8, zorder=1000, label=dates[k])
        if j==0:
            axInset.plot(xTerm, termElev, '.', color=plt.cm.Blues(color_id[k]), markersize=8, zorder=1000, label=dates[k])

#plt.plot(x_prof, elev2003, color='C2')
    ax[0].legend(loc="lower center",          # Use the bottom-center of the legend box as the anchor point
                 bbox_to_anchor=(0.5, 1.02),  # Center it horizontally (0.5), place it slightly above the top (1.02)
                 ncol=5 ) #plt.legend(['2015', '2025', '2003'])

#plt.plot(x_radar, data['Tx_z'].values, '.')
    ax[j].plot(x_radar, bed_radar, '--', marker='.', color='r', markersize=8)
    if j==0:
        axInset.plot(x_radar, bed_radar, '--', marker='.', color='r', markersize=8)
#ax[0].inset_axes(ax[2], xlim=(-200,100), ylim=(10,20), edgecolor="black")

#ax[0].imshow(photo)

#DEM2003 = 'taku2003test.tif'
#RES0304 = 'Taku_RES_thickness_2003-04.csv'
#elev2003 = rasterstats.point_query(profile, DEM2003)[0]
#data0304 = pandas.read_csv(RES0304)
#data0304 = data0304.iloc[29:35]
#data0304 = data0304.sort_values(by='thickness (m)', ascending=False)
#XY = np.matmul(rot, np.vstack((data0304['Easting (m)'].values-X0, data0304['northing (m)'].values-Y0)))
#x03 = XY[0,:]

plt.savefig('figXX-profiles_new.pdf', format='pdf', dpi=300)
