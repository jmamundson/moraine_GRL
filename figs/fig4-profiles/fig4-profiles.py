#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 13:24:06 2025

@author: jason
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patheffects

import shapefile

from shapely.geometry import LineString, Point, Polygon, shape
import fiona

import rasterstats
from rasterstats import zonal_stats, point_query
import glob
import os

plt.style.use('../moraine.mplstyle')

import datetime as dt

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
    formatted_date = date_object.strftime("%Y/%-m/%-d")

    return formatted_date


#%% set up figure
cm = 1/2.54
fig_width = 15.6*cm
fig_height = 13.6*cm
fig, ax = plt.subplots(3, 2, figsize=(fig_width,fig_height))
ax = ax.ravel()


full_width = 13.5
width = 6.2
height = width*2/3.5
ax_width = width*cm/fig_width
ax_height = height*cm/fig_height
cbar_height = 0.2*cm/fig_height
left = 1.8*cm/fig_width
bot = 1.1*cm/fig_height
ygap = 0.6*cm/fig_height
xgap = 0.6*cm/fig_width #(full_width-2*width)*cm/fig_width


# ax1 = plt.axes([left, bot+ygap, ax_width, ax_height])
# ax2 = plt.axes([left+ax_width+xgap, bot+ygap, ax_width, ax_height])



ax[0].set_position([left, bot + 2*ygap + 2*ax_height, ax_width, ax_height])
ax[1].set_position([left+ax_width+xgap, bot + 2*ygap + 2*ax_height, ax_width, ax_height])

ax[2].set_position([left, bot+ygap+ax_height, ax_width, ax_height])
ax[3].set_position([left+ax_width+xgap, bot + ygap + ax_height, ax_width, ax_height])

ax[4].set_position([left, bot, ax_width, ax_height])
ax[5].set_position([left+ax_width+xgap, bot, ax_width, ax_height])

ax[0].set_ylabel('Elevation [m]')
ax[2].set_ylabel('Elevation [m]')
ax[4].set_ylabel('Elevation [m]')

ax[4].set_xlabel('Longitudinal coordinate [m]')
ax[5].set_xlabel('Longitudinal coordinate [m]')

ax[0].set_xticklabels('')
ax[1].set_xticklabels('')
ax[2].set_xticklabels('')
ax[3].set_xticklabels('')

ax[1].set_yticklabels('')
ax[3].set_yticklabels('')
ax[5].set_yticklabels('')

txt_space = 0.35 # cm

panel_labels = ['a', 'b', 'c', 'd', 'e', 'f']

for k in np.arange(0,len(panel_labels)):
    ax[k].text(txt_space/width, 1-txt_space/height, panel_labels[k], transform=ax[k].transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1010) 
#ax2.text(txt_space/width, 1-txt_space/height, r'b  2024/8/3$-$2023/7/27', transform=ax2.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1010) 
#ax3.text(txt_space/width, 1-txt_space/(im_height*fig_height/cm), 'c  2023/5/22', transform=ax3.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')]) 


#%%
# ax1.set_axisbelow(True)
# ax1.grid(visible=True, which='both', zorder=-100, alpha=0.5)
# ax1.set_xlim([554.5, 558])
# ax1.set_ylim([6474, 6476])
# ax1.set_yticks(np.linspace(6474, 6476, 3, endpoint=True))
# ax1.set_yticks(np.linspace(6474, 6476, 9, endpoint=True), minor=True)
# ax1.set_xticks(np.linspace(555,558, 4, endpoint=True))
# ax1.set_xticks(np.linspace(554.5, 558, 15, endpoint=True), minor=True)
# ax1.set_xlabel('Easting [km]')
# ax1.set_ylabel('Northing [km]')

# ax2.set_axisbelow(True)
# ax2.grid(visible=True, which='both', zorder=-100, alpha=0.5)
# ax2.set_xlim([554.5, 558])
# ax2.set_ylim([6474, 6476])
# ax2.set_yticks(np.linspace(6474, 6476, 3, endpoint=True))
# ax2.set_yticks(np.linspace(6474, 6476, 9, endpoint=True), minor=True)
# ax2.set_xticks(np.linspace(555,558, 4, endpoint=True))
# ax2.set_xticks(np.linspace(554.5, 558, 15, endpoint=True), minor=True)
# ax2.set_xlabel('Easting [km]')
# ax2.set_ylabel('Northing [km]')

# # ax1_cb = plt.axes([left, bot, ax_width, cbar_height])
# # ax2_cb = plt.axes([left+ax_width+xgap, bot, ax_width, cbar_height])

# ax1_cb = plt.axes([left, bot + cbar_height + 2*ygap + ax_height, ax_width, cbar_height])
# ax2_cb = plt.axes([left, bot, ax_width, cbar_height])

# ax = [ax1, ax2]
# ax_cb = [ax1_cb, ax2_cb]

# im_height = 2*cbar_height + 2*ax_height + 3*ygap
# ax3 = plt.axes([left+ax_width+xgap, bot, ax_width, im_height])
# ax3.set_xticks([])
# ax3.set_yticks([])

#%%



DEM = '/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/DEMs/Taku_terminus.tif'


# flight = '/hdd2/taku/bedmachine/thickness/OIB/shp/IRUAFHF2_20140821-203038.shp'
# termX = 554219
# termY = 6474577


flight = '/hdd2/taku/bedmachine/thickness/OIB/shp/IRUAFHF2_20140821-201742.shp'
terminus2015 = '/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/Taku_Aug2_2015_terminus.shp'

extendedX = 556675
extendedY = 6474266
# extendedPt = Point(extendedX, extendedY, 0) # add point to extend flight line shape file so that it passes the terminus



# termX = 556369
# termY = 6474854

# termPt = Point(termX, termY, 0)

shp = shapefile.Reader(flight)
records = shp.records()






northing = np.array([records[x][0] for x in np.arange(0,len(records))])
easting = np.array([records[x][1] for x in np.arange(0,len(records))])
surface = np.array([records[x][2] for x in np.arange(0,len(records))])
bed = np.array([records[x][3] for x in np.arange(0,len(records))])


elevation = point_query(flight, DEM)
elevation = np.array(elevation, dtype='float64')

# if flight == '/hdd2/taku/bedmachine/thickness/OIB/shp/IRUAFHF2_20140821-201742.shp':
#     easting = [x for x in easting[::-1]]
#     northing = [x for x in northing[::-1]]
#     bed = [x for x in bed[::-1]]
#     elevation = [x for x in elevation[::-1]] # from DEM
#     surface = [x for x in surface[::-1]] # from OIB


eastingT = np.concatenate((easting, np.linspace(easting[-1], extendedX, 1000, endpoint=True)))
northingT = np.concatenate((northing, np.linspace(northing[-1], extendedY, 1000, endpoint=True)))



flightLine = LineString(np.array([eastingT,northingT]).T)



# import terminus and create LineString
with fiona.open(terminus2015, 'r') as source:
    for feature in source:
        xy = feature['geometry']['coordinates']

termLine2015 = LineString(xy)


# intersection of terminus
termPt = flightLine.intersection(termLine2015)
termEasting = termPt.coords.xy[0]
termNorthing = termPt.coords.xy[1]

termElev = np.array(point_query(termPt, DEM))

# termPt.coordsXY

elevation = point_query(flightLine, DEM)[0]



distT = np.sqrt(np.diff(northingT)**2 + np.diff(eastingT)**2)
distT = np.concatenate((np.array([0]), np.cumsum(distT)))

dist = np.sqrt(np.diff(northing)**2 + np.diff(easting)**2)
dist = np.concatenate((np.array([0]), np.cumsum(dist)))


distCorr = distT[eastingT>termEasting][0]


# plt.plot(distT-distCorr,elevation, 'k')
# plt.plot(dist-distCorr, bed, 'k')
# plt.plot(np.array([dist[-1]-distCorr, 0]), np.array([bed[-1], termElev[0]]), 'k:')



#%% drone DEMs

profiles_shp = '../sediment_profiles/profiles.shp' # use correct file!!!
profiles = shapefile.Reader(profiles_shp).shapes()

drone_files = sorted(glob.glob('/hdd2/taku/uav/surveys/02_takuGrid/taku_DEM_*.tif'))
index = [4, 11, 15, 19]
drone_files = [drone_files[x] for x in index]


for k in np.arange(0,len(profiles)):
    profile = LineString(profiles[k].points)
    
    #-- re-order and add points to profile
    X, Y = np.array(profile.coords.xy)
    if Y[1]>Y[0]:
        Y = np.flip(Y)
        X = np.flip(X)
        
    dx = 0.5 # desired grid spacing
    
    theta = np.arctan(np.diff(Y)/np.diff(X)) # angle of profile
    
    X = np.arange(X[0], X[1], dx*np.cos(theta))
    Y = np.arange(Y[0], Y[1], dx*np.sin(theta))
    
    # X = np.linspace(X[0], X[1], 200, endpoint=True)
    # Y = np.linspace(Y[0], Y[1], 200, endpoint=True)
         
    profile = LineString(list(zip(X,Y)))
    
    dist = np.sqrt(np.diff(X)**2 + np.diff(Y)**2)
    dist = np.concatenate((np.array([0]), np.cumsum(dist)))
    
    
    #X = np.linspace(555768, 555948, 1000, endpoint=True)
    #Y = np.linspace(6474918, 6474535, 1000, endpoint=True)
    #profile = LineString(list(zip(X,Y)))
    
    
    
    shpBase = '/hdd2/taku/uav/surveys/06_terminusPosition/'
    termShp = [shpBase + 'taku_' + os.path.basename(x)[9:17] + '_terminus.shp' for x in drone_files]
    dates = [convert_date_format(os.path.basename(x)[9:17]) for x in drone_files]
    
    
    #droneZ = point_query(flightLine, drone)[0]
    
    #plt.plot(distT-distCorr, droneZ, 'r')
    


    termPt2015 = profile.intersection(termLine2015) # relative to 2015 term position
    DEM2015 = np.array(point_query(profile, DEM)[0]).astype('float64')
    
    # reset distance array so that it is centered on 2015 terminus position
    dist = dist - np.sqrt((termPt2015.coords.xy[0] - X[0])**2 + (termPt2015.coords.xy[1] - Y[0])**2)
    
    ax[k].plot(dist[dist>0], DEM2015[dist>0], 'r', zorder=1000, label='2015/8/2')
    ax[k].plot(dist[dist<=0], DEM2015[dist<=0], 'r--', zorder=1000)
    
    # ax[k].fill(np.array([-200,-200,0]), np.array([-200*0.06, 0, 0]) + np.min(DEM2015[dist<=0]), color=(0, 0, 0, 0.1), zorder=0, linewidth=0) 

    
    for j in np.arange(0, len(drone_files)):
        # import terminus and create LineString
        with fiona.open(termShp[j], 'r') as source:
            for feature in source:
                xy = feature['geometry']['coordinates']
        
        termLine = LineString(xy)
    
        termPt = profile.intersection(termLine)
    
        
    
        termOffset = np.sqrt((np.array(termPt2015.coords.xy[0])-np.array(termPt.coords.xy[0]))**2+(np.array(termPt2015.coords.xy[1])-np.array(termPt.coords.xy[1]))**2)
    
       
        color_id = np.linspace(0.5, 1, len(drone_files))
    
    
        droneZ = np.array(point_query(profile, drone_files[j])[0]).astype('float64')
        ax[k].plot(dist[dist<=-termOffset], droneZ[dist<=-termOffset], '--', color=plt.cm.Blues(color_id[j])) # dark equals more recent
        ax[k].plot(dist[dist>-termOffset], droneZ[dist>=-termOffset], color=plt.cm.Blues(color_id[j]), label=dates[j]) # dark equals more recent
        
        # testing this idea...
        

ax[0].legend(bbox_to_anchor=(1 + 0.5*(xgap/ax_width),1.2), loc='upper center', ncols=5)
#fig.legend(ncols=5)

for k in np.arange(0,len(profiles)):        
    ax[k].set_ylim([5, 25])
    ax[k].set_xlim([-200,100])

   

ax[0].set_ylabel('Elevation [m]')
ax[2].set_ylabel('Elevation [m]')
ax[4].set_ylabel('Elevation [m]')

ax[4].set_xlabel('Longitudinal coordinate [m]')
ax[5].set_xlabel('Longitudinal coordinate [m]')


#plt.savefig('fig4-profiles.pdf', format='pdf', dpi=300)

#%%

# extendedZ = point_query(extendedPt, DEM)

# easting = np.concatenate((np.array([termX]), easting))
# northing = np.concatenate((np.array([termY]), northing))



# elevation = np.concatenate((np.array(termZ), elevation))




# thickness = np.concatenate((np.array([0]), thickness))
# bed = elevation - thickness


# dist = np.sqrt(np.diff(northing)**2 + np.diff(easting)**2)
# dist = np.concatenate((np.array([0]), np.cumsum(dist)))


# plt.plot(dist,bed)
# plt.plot(dist,elevation)

# droneDEM = '/hdd2/taku/uav/surveys/02_takuGrid/taku_DEM_20250714.tif'

