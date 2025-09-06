import numpy as np
from osgeo import gdal

from matplotlib import pyplot as plt
import matplotlib

from PIL import Image
import shapefile

from shapely.geometry import LineString, Point

import rasterstats
from rasterstats import zonal_stats, point_query
import glob
from scipy.interpolate import RegularGridInterpolator
#%%

def loadDEM(file):

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
base_dir = '/hdd/taku/'

terminusPositions = sorted(glob.glob(base_dir + 'uav/surveys/06_terminusPosition/*.shp'))
terminus2015 = terminusPositions[0]
terminus = shapefile.Reader(terminus2015).shapes()
terminus = LineString(terminus[0].points)


profiles_shp = './terminus_profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()

# later update for high resolution DEMs(?)
DEMs = sorted(glob.glob(base_dir + 'uav/surveys/02_takuGrid/taku_DEM*.tif'))
include = [4, 11, 15]
#index = []
DEMs = [DEMs[x] for x in include]

refDEM = ['/hdd/taku/DEMs_orthomosaics/20150802_ChrisLarsen/DEMs/taku_DEM_20150802.tif']

DEMs = refDEM + DEMs

color_id = np.linspace(0,1,len(DEMs))

fig, axes = plt.subplots(1,len(profiles))


moraine2015 = np.array([1338.3, 946.9, 431.27]) # unsure of these points

# correction for reference DEM (Larsen 2015)
elevLandingStrip = np.zeros(2)
       
stats = zonal_stats('landingStrip.shp', DEMs[0])
elevLandingStrip[0] = stats[0]['mean']    

stats = zonal_stats('landingStrip.shp', DEMs[-1])    
elevLandingStrip[1] = stats[0]['mean']    
    
dz = np.diff(elevLandingStrip) #(elevLandingStrip-elevLandingStrip[0



for j in np.arange(0,len(profiles)):
    profile = LineString(profiles[j].points)
    
    
    X, Y = np.array(profile.coords.xy)
    X, Y = np.linspace(X[0], X[-1], 1000, endpoint=True), np.linspace(Y[0], Y[-1], 1000, endpoint=True) 
    
    # create new profile with more points
    XY = np.vstack((X,Y)).T
    profile = LineString(XY)
    
    dist = np.sqrt((X-X[0])**2 + (Y-Y[0])**2)
    
    # find where profile intersects 2015 position
    xy_intersection = np.array(terminus.intersection(profile).coords[:][0])
    # distance to intersection point
    dist_intersection = np.sqrt((xy_intersection[0]-X[0])**2 + (xy_intersection[1]-Y[0])**2)
    
    for k in np.arange(0,len(DEMs)):
        xDEM, yDEM, zDEM, im_extent = loadDEM(DEMs[k])
        
        if k==0:
            zDEM =+ dz
        # extract profile; is there a better way to do this?
        raster = DEMs[k]
        elev = rasterstats.point_query(profile, raster)[0]
        
        axes[j].plot(dist-dist_intersection, elev, color=plt.cm.viridis(color_id[k]))
    
    #plt.plot(X, Y)
    
#%% DEMs
ymin = 0
ymax = 60
xmin = -300
xmax = 300

for j in np.arange(0,len(axes)):
    axes[j].set_ylim([ymin, ymax])
    axes[j].set_xlim([xmin, xmax])
    
    
    
#%%    
# DEMs = sorted(glob.glob(base_dir + 'uav/surveys/02_takuGrid/taku_DEM*.tif'))
        
# # include = [0, 1, 3, 4, 6, 7, 11, 12, 14, 16 ]
# include = [4, 15]
# DEMs = [DEMs[x] for x in include]



# elevOutwashWest = np.zeros(len(DEMs))
# elevOutwashEast = np.zeros(len(DEMs))
elevLandingStrip = np.zeros(2)
        
        # 4, 6 only for easting
        
stats = zonal_stats('landingStrip.shp', DEMs[0])
elevLandingStrip[0] = stats[0]['mean']    

stats = zonal_stats('landingStrip.shp', DEMs[-1])    
elevLandingStrip[1] = stats[0]['mean']    
    # stats = zonal_stats('outwashWest.shp', DEMs[k])
    # elevOutwashWest[k] = stats[0]['mean']
    
    # stats = zonal_stats('outwashEast.shp', DEMs[k])
    # elevOutwashEast[k] = stats[0]['mean']
    
dy = np.diff(elevLandingStrip) #(elevLandingStrip-elevLandingStrip[0]) 

# plt.figure()
# plt.plot(elevOutwashWest , '.')   
# plt.plot(elevOutwashEast ,'.')
# # plt.ylim([5.5,6.5])
