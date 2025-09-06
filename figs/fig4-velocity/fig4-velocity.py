import numpy as np
import gdal

from matplotlib import pyplot as plt
import matplotlib

from PIL import Image
import shapefile

from shapely.geometry import LineString, Point, Polygon

import rasterstats
from rasterstats import zonal_stats, point_query
import glob
from scipy.interpolate import RegularGridInterpolator

import os

import datetime as dt
#%%
def loadgeotiff(file):

    ds = gdal.Open(file)
    data = ds.ReadAsArray()
    #data[data<0] = np.nan
    
    gt = ds.GetGeoTransform()
    ulx = gt[0] # UTM easting of upper left corner (top left corner of pixel)
    uly = gt[3] # UTM northing of upper left corner (top left corner of pixel)
    pix = gt[1] # pixel size [m]
    lrx = ulx + pix*data.shape[1] # UTM easting of lower right corner (bottom right corner of pixel)
    lry = uly - pix*data.shape[0] # UTM northing of lower right corner (bottom right corner of pixel)
    im_extent = np.array([ulx, lrx, lry, uly])

    # check the order here!!!
    xDEM = np.linspace(ulx+pix/2, lrx-pix/2, data.shape[1], endpoint=True)
    yDEM = np.linspace(uly-pix/2, lry+pix/2, data.shape[0], endpoint=True)    

    return(xDEM, yDEM, data, im_extent)

#%%

X = np.array([555000, 555500, 555500, 555000, 555000])
Y = np.array([6474700, 6474700, 6475200, 6475200, 6474700])
XY = np.vstack((X,Y)).T
zone1 = Polygon(XY)

# transverse profile
X, Y = np.linspace(555000, 557400, 100, endpoint=True), np.linspace(6474700, 6475800, 100, endpoint=True) 
XY = np.vstack((X,Y)).T
transverse_distance = np.sqrt((X-X[0])**2+(Y-Y[0])**2)
transverse_profile = LineString(XY)


profiles_shp = '../sediment_profiles/terminus_profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()



vvFiles = sorted(glob.glob('/home/jason/projects/taku/uav/surveys/05_lk_grids/*vv.tif'))
speedMean = np.zeros(len(vvFiles))
speed = np.zeros(len(vvFiles))
t = [None]*len(vvFiles)
#x, y, data, im_extent = loadgeotiff(vvFiles[0])

color_id = np.linspace(0, 1, len(vvFiles), endpoint=True)

fig, axes = plt.subplots(1,len(profiles)-1)

for j in np.arange(0,len(profiles)-1):
    profile = LineString(profiles[j].points)
    
    X, Y = np.array(profile.coords.xy)
    X, Y = np.linspace(X[0], X[-1], 100, endpoint=True), np.linspace(Y[0], Y[-1], 100, endpoint=True) 
    
    # create new profile with more points
    XY = np.vstack((X,Y)).T
    profile = LineString(XY)
    
    dist = np.sqrt((X-X[0])**2 + (Y-Y[0])**2)
    
    for k in np.arange(0, len(vvFiles)):
    
        file = os.path.basename(vvFiles[k])
        YYYYmmdd = file[5:13]
        
        t[k] = dt.datetime.strptime(YYYYmmdd,'%Y%m%d')
        
        stats = zonal_stats(zone1, vvFiles[k], nodata=None)
        speedMean[k] = stats[0]['mean']   
        
        velocity = rasterstats.point_query(profile, vvFiles[k])[0]
        #axes[j].plot(dist, velocity, color=plt.cm.viridis(color_id[k]))
        axes[j].plot(dist, velocity, color=plt.cm.viridis((t[k].timetuple().tm_yday-100)/200))

for j in np.arange(0,len(axes)):    
    axes[j].set_xlim([0, 1500])
    axes[j].set_ylim([0, 150])
# plt.plot(t, speedMean)

#%%
dem = '/home/jason/projects/taku/uav/surveys/03_hillshades/taku_DEM_20230629.tif'
xd, yd, elev, dem_extent = loadgeotiff(dem)

vxFiles = sorted(glob.glob('/home/jason/projects/taku/uav/surveys/05_lk_grids/*vx.tif'))
vyFiles = sorted(glob.glob('/home/jason/projects/taku/uav/surveys/05_lk_grids/*vx.tif'))

vxFiles = vxFiles[6]
vyFiles = vyFiles[6]

x, y, vx, extent = loadgeotiff(vxFiles)
_, _, vy, _ = loadgeotiff(vyFiles)

dx = x[1]-x[0]
div = np.gradient(vx, axis=1)/dx + np.gradient(vy, axis=0)/dx

plt.imshow(elev, extent=dem_extent, cmap='gray')
plt.imshow(div, extent=extent, alpha=0.5)
plt.colorbar()
# plt.clim([])