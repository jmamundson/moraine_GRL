import numpy as np
from osgeo import gdal

from matplotlib import pyplot as plt
import matplotlib
from matplotlib import patheffects

from PIL import Image
import shapefile

from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import shape
from shapely.geometry import MultiPolygon

import glob
import os

plt.style.use('../moraine.mplstyle')

base_dir = '/hdd/taku/'
import sys
sys.path.append(base_dir + 'manuscripts/moraine_GRL/figs/')
import scripts

import rasterstats
from scipy.interpolate import LinearNDInterpolator
import matplotlib as mpl

#%%
# radar transect

data = np.loadtxt(base_dir + 'radar/2023/profile_007/gps_topo_007.txt')

easting = data[:,0]
northing = data[:,1]
h_surf = data[:,2]
dist = data[:,3]
H = data[:,4]


# plt.plot(dist, h_surf, dist, h_surf-H)
# plt.ylabel('Elevation [m]')
# plt.xlabel('Distance [m]')
# plt.legend(['Glacier surface', 'Glacier bed'])


#%% 2003/04 radar data
RES_0304 = np.loadtxt(base_dir + 'radar/RES_0304/res_2003_2004_summary.txt')

RES = {'northing':RES_0304[:,1], 'easting':RES_0304[:,2], 'surface':RES_0304[:,3], 'bed':RES_0304[:,-1]}

points = list(zip(RES['easting'], RES['northing']))
bed_interpolator = LinearNDInterpolator(points, RES['bed'])
surface_interpolator = LinearNDInterpolator(points, RES['surface'])


profiles_shp = '../sediment_profiles/profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()
profile = LineString(profiles[3].points)
X, Y = np.array(profile.coords.xy)

if Y[1]>Y[0]:
    Y = np.flip(Y)
    X = np.flip(X)
    
X = np.linspace(X[0], X[1], 200, endpoint=True)
Y = np.linspace(Y[0], Y[1], 200, endpoint=True)
dist = np.sqrt((X-X[0])**2 + (Y-Y[0])**2)

bed = bed_interpolator(X,Y)
surface = surface_interpolator(X,Y)

terminusX = 556582.9
terminusY = 6475131.7
terminusZ = 26.40
terminusDist = np.sqrt((terminusX-X[0])**2 + (terminusY-Y[0])**2)




profile = LineString(list(zip(X,Y)))

DEM2024_tif = base_dir + 'uav/surveys/02_takuGrid/taku_DEM_20240803.tif'
DEM2024_elev = np.array(rasterstats.point_query(profile, DEM2024_tif)[0])

DEM2015_tif = base_dir + 'DEMs_orthomosaics/20150802_ChrisLarsen/DEMs/Taku_terminus.tif'
DEM2015_elev = np.array(rasterstats.point_query(profile, DEM2015_tif)[0])

IfSAR_tif = base_dir + 'DEMs_orthomosaics/IfSAR/taku_IfSAR_utm.tif'
IfSAR_elev = np.array(rasterstats.point_query(profile, IfSAR_tif)[0])

DEM2003_tif = base_dir + 'DEMs_orthomosaics/2002-2005_RJM/2002/2002 dtm5m blanked3.tif'
DEM2003_elev = np.array(rasterstats.point_query(profile, DEM2003_tif)[0])

SRTM_tif = base_dir + 'DEMs_orthomosaics/SRTM/SRTM_Taku_utm.tif'
SRTM_elev = np.array(rasterstats.point_query(profile, SRTM_tif)[0])

mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=plt.cm.viridis([0.1, 0.3, 0.5, 0.7, 0.9, 0.3]))
plt.figure()
plt.plot(dist, SRTM_elev, dist, DEM2003_elev, dist, IfSAR_elev,
         dist, DEM2015_elev, dist, DEM2024_elev, dist, bed)
plt.legend(['SRTM: 2000', 'Aerial photos: 2003', 'IfSAR: 2011', 'Aerial photos: 2015', 'Drone: 2024'])


#%%

profiles_shp = '../sediment_profiles/profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()
profile = LineString(profiles[3].points)

#-- re-order and add points to profile
X, Y = np.array(profile.coords.xy)
if Y[1]>Y[0]:
    Y = np.flip(Y)
    X = np.flip(X)
    
X = np.linspace(X[0], X[1], 100, endpoint=True)
Y = np.linspace(Y[0], Y[1], 100, endpoint=True)
profile = LineString(list(zip(X,Y)))
#--

dist = np.sqrt((X-X[0])**2 + (Y-Y[0])**2)

files = sorted(glob.glob(base_dir + 'uav/surveys/02_takuGrid/taku_DEM*tif'))
files.pop(-4)

for j in np.arange(0,len(files)):
    h = np.array(rasterstats.point_query(profile, files[j])[0], dtype='float')
    # h = h-np.mean(h[np.logical_and(dist>=840, dist<=880)])
    plt.plot(dist, h, color=plt.cm.viridis(j/len(files)))    
    
plt.ylim([0,100])

#%%
# find points that are now uncovered
# index = np.logical_and(RES_all['northing']<6474825, RES_all['thickness']<50)
# index = RES_all['northing']<6474825
RES = {'northing':RES_0304[-4:,0], 'easting':RES_0304[-4:,1], 'thickness':RES_0304[-4:,2]}

DEM_tif = base_dir + 'DEMs_orthomosaics/2002-2005_RJM/2004/Taku_Jun04 blanked3.tif'
# DEM_tif = base_dir + 'DEMs_orthomosaics/2002-2005_RJM/2004/Taku_Aug04 blanked3.tif'
# DEM_tif = base_dir + 'DEMs_orthomosaics/2002-2005_RJM/2003/taku2003testblanked3.tif'
# DEM_tif = base_dir + 'DEMs_orthomosaics/2002-2005_RJM/2002/2002 dtm5m blanked3.tif'
xDEM, yDEM, DEM2004, im_extent = scripts.loadDEM(DEM_tif)

plt.imshow(DEM2004, extent=im_extent, cmap='gray', vmin=0, vmax=200)
# plt.plot(RES['easting'], RES['northing'], '+')

bed2004 = np.zeros(len(RES['thickness']))
surface2024 = np.zeros(len(RES['thickness']))

DEM2024_tif = base_dir + 'uav/surveys/02_takuGrid/taku_DEM_20240803.tif'

for j in np.arange(0, len(RES['thickness'])):
    pt = Point([RES['easting'][j], RES['northing'][j]])
    z = rasterstats.point_query(pt, DEM_tif)[0]
    bed2004[j] = z - RES['thickness'][j]
    surface2024[j] = rasterstats.point_query(pt, DEM2024_tif)[0]
    
dz = surface2024-bed2004


#%% 2015 radar data
file1 = base_dir + 'radar/2014-16/data/Radar_points_archive_2016_Amundson.csv'
file2 = base_dir + 'radar/2014-16/data/Radar_points_archive_2016_Truffer.csv'

data = np.loadtxt(file2, skiprows=1, usecols=(6,7,8,11,12,13,16,-1), delimiter=',')
Tx = {'easting':data[:,0], 'northing':data[:,1], 'elevation':data[:,2]}
Rx = {'easting':data[:,3], 'northing':data[:,4], 'elevation':data[:,5]}

separation = data[:,-2] # transmitter-receiver separation [m]
path_length = data[:,-1]
thickness = 0.5*np.sqrt(path_length**2 - separation**2) 

RES = {'easting':(Tx['easting']+Rx['easting'])/2, 'northing':(Tx['northing']+Tx['northing'])/2, 
       'elevation':Tx['elevation'], 'thickness':thickness, 'bed':Tx['elevation']-thickness}

# plt.scatter(RES['easting']*1e-3, RES['northing']*1e-3, 10, RES['bed'], cmap=plt.cm.viridis, vmin=-100, vmax=0)    

bed2016 = np.zeros(len(RES['thickness']))
surface2024 = np.zeros(len(RES['thickness']))

for j in np.arange(0, len(RES['thickness'])):
    pt = Point([RES['easting'][j], RES['northing'][j]])
    z = rasterstats.point_query(pt, DEM2024_tif)[0]
    if z is None:
        bed2016[j] = np.nan
        surface2024[j] = np.nan
    else:
        bed2016[j] = z - RES['thickness'][j]
        surface2024[j] = rasterstats.point_query(pt, DEM2024_tif)[0]
    
dz = surface2024-bed2016

# plt.scatter(RES['easting']*1e-3, RES['northing']*1e-3, 10, RES['bed'], cmap=plt.cm.viridis, vmin=-100, vmax=100)    


#%%
ortho = base_dir + 'uav/surveys/02_takuGrid/taku_ortho_20240803.tif'
hillshade_DEM = base_dir + 'uav/surveys/03_hillshades/taku_DEM_20240803.tif'
_, _, image, _ = scripts.loadOrtho(ortho)
_, _, hillshade, im_extent = scripts.loadDEM(hillshade_DEM)

mask = np.array(image[:,:,3], dtype='float')
mask[mask<=0] = np.nan
mask[mask>0] = 1

plt.imshow(hillshade*mask, cmap='gray', extent=im_extent*1e-3)
plt.scatter(RES['easting']*1e-3, RES['northing']*1e-3, 20, dz, vmin=20, vmax=30)
plt.colorbar(label='Elevation difference [m]')
plt.xlim([554.5, 558])
plt.ylim([6474, 6476])
plt.xlabel('Easting, m')
plt.ylabel('Northing, m')
plt.title('2024/8/3 - 2003/?/?')
# plt.clabel('Elevation difference [m]')