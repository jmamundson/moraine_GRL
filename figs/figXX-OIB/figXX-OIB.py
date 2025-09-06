#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 13:24:06 2025

@author: jason
"""

import numpy as np
from matplotlib import pyplot as plt
import shapefile

from shapely.geometry import LineString, Point, Polygon, shape
import fiona

import rasterstats
from rasterstats import zonal_stats, point_query
import glob
import os

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


plt.plot(distT-distCorr,elevation, 'k')
plt.plot(dist-distCorr, bed, 'k')
plt.plot(np.array([dist[-1]-distCorr, 0]), np.array([bed[-1], termElev[0]]), 'k:')



#%% drone DEMs
profiles_shp = '../sediment_profiles/profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()
profile = LineString(profiles[0].points)

#-- re-order and add points to profile
X, Y = np.array(profile.coords.xy)
if Y[1]>Y[0]:
    Y = np.flip(Y)
    X = np.flip(X)
    
X = np.linspace(X[0], X[1], 1000, endpoint=True)
Y = np.linspace(Y[0], Y[1], 1000, endpoint=True)
profile = LineString(list(zip(X,Y)))


drone_files = sorted(glob.glob('/hdd2/taku/uav/surveys/01_utm/taku_DEM_*.tif'))

index = [4, 11] #, 16, 20]

drone_files = [drone_files[x] for x in index]

shpBase = '/hdd2/taku/uav/surveys/06_terminusPosition/'
termShp = [shpBase + 'taku_' + os.path.basename(x)[9:17] + '_terminus.shp' for x in drone_files]



#droneZ = point_query(flightLine, drone)[0]

#plt.plot(distT-distCorr, droneZ, 'r')



for j in np.arange(0, len(drone_files)):
    # import terminus and create LineString
    with fiona.open(termShp[j], 'r') as source:
        for feature in source:
            xy = feature['geometry']['coordinates']
    
    termLine = LineString(xy)

    termPt = profile.intersection(termLine)

    termPt2015 = profile.intersection(termLine2015) # relative to 2015 term position

    dterm = np.sqrt((np.array(termPt2015.coords.xy[0])-np.array(termPt.coords.xy[0]))**2+(np.array(termPt2015.coords.xy[1])-np.array(termPt.coords.xy[1]))**2)

    dist = np.sqrt(np.diff(X)**2 + np.diff(Y)**2)
    dist = np.concatenate((np.array([0]), np.cumsum(dist)))

    distAdj = np.sqrt((termPt.coords.xy[0]-X[0])**2 + (termPt.coords.xy[1]-Y[0])**2) # distance to 2015 terminus

    color_id = np.linspace(0.5, 1-0.1, len(drone_files))

    dist = dist-distAdj

    droneZ = np.array(point_query(profile, drone_files[j])[0]).astype('float64')
    plt.plot(dist[dist<=0]-dterm, droneZ[dist<=0], ':', color=plt.cm.Blues(color_id[j])) # dark equals more recent
    plt.plot(dist[dist>=0]-dterm, droneZ[dist>=0], color=plt.cm.Blues(color_id[j])) # dark equals more recent
    
plt.ylim([0, 50])


#%%

extendedZ = point_query(extendedPt, DEM)

easting = np.concatenate((np.array([termX]), easting))
northing = np.concatenate((np.array([termY]), northing))



elevation = np.concatenate((np.array(termZ), elevation))




thickness = np.concatenate((np.array([0]), thickness))
bed = elevation - thickness


dist = np.sqrt(np.diff(northing)**2 + np.diff(easting)**2)
dist = np.concatenate((np.array([0]), np.cumsum(dist)))


plt.plot(dist,bed)
plt.plot(dist,elevation)

droneDEM = '/hdd2/taku/uav/surveys/02_takuGrid/taku_DEM_20250714.tif'

