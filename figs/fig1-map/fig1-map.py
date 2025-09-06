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

import rasterio

plt.style.use('../moraine.mplstyle')


#%%



cm = 1/2.54
fig_width = 10.5*cm
fig_height = 13.5*cm
plt.figure(figsize=(fig_width,fig_height))

width = 8
height = width*(6524.5-6473.5)/(561-522.5)
cbar_height = 0.2*cm/fig_height
ax_width = width*cm/fig_width
ax_height = height*cm/fig_height

left = 2*cm/fig_width
bot = 1.1*cm/fig_height
ygap = 1.2*cm/fig_height
xgap= 0.4*cm/fig_width

inset_width = 4*cm/fig_width
inset_height = 4*cm/fig_height
inset_left = 2*cm/fig_width
inset_bot = ax_height - inset_height + 0.9*cm/fig_height + bot + ygap + cbar_height

ax1 = plt.axes([left, bot+cbar_height+ygap, ax_width, ax_height])

ax_cbar = plt.axes([left, bot, ax_width, cbar_height])

#inset_bot = bot - 1*cm/fig_height
ax2 = plt.axes([inset_left, inset_bot, inset_width, inset_height])
ax2.set_xticks([])
ax2.set_yticks([])


#%% load hillshade

ds = gdal.Open('arcticDEM/taku_hillshade.tif')
data = ds.ReadAsArray().astype('int')
gt = ds.GetGeoTransform()
ulx = gt[0] # UTM easting of upper left corner (top left corner of pixel)
uly = gt[3] # UTM northing of upper left corner (top left corner of pixel)
pix = gt[1] # pixel size [m]
lrx = ulx + pix*data.shape[1] # UTM easting of lower right corner (bottom right corner of pixel)
lry = uly - pix*data.shape[0] # UTM northing of lower right corner (bottom right corner of pixel)
im_extent = np.array([ulx, lrx, lry, uly])/1000.

X = np.linspace(ulx+pix/2, lrx-pix/2, data.shape[0], endpoint=True)
Y = np.linspace(uly-pix/2, lry+pix/2, data.shape[1], endpoint=True)

    
ax1.imshow(data, extent=im_extent, cmap='gray', alpha=0.75)

#%%
outline = shapefile.Reader('outline/taku_glims_outline_2014.shp').shapes()
# note that outline includes "internal rocks"

for j in np.arange(0,len(outline)):
    feature = LineString(outline[j].points)
    featureX, featureY = np.array(feature.coords.xy)/1000
    
    ax1.plot(featureX, featureY, color='k', zorder=1000)
    
#%%
ds = gdal.Open('./ITS_Live/ITS_LIVE_composite_utm_cropped.tif')
v = ds.ReadAsArray()



# ds = gdal.Open('taku_vx.tif')
# vx = ds.ReadAsArray()

# ds = gdal.Open('taku_vy.tif')
# vy = ds.ReadAsArray()

#speed = np.sqrt(vx**2 + vy**2)

gt = ds.GetGeoTransform()
ulx = gt[0] # UTM easting of upper left corner (top left corner of pixel)
uly = gt[3] # UTM northing of upper left corner (top left corner of pixel)
pix = gt[1] # pixel size [m]
lrx = ulx + pix*v.shape[1] # UTM easting of lower right corner (bottom right corner of pixel)
lry = uly - pix*v.shape[0] # UTM northing of lower right corner (bottom right corner of pixel)
im_extent = np.array([ulx, lrx, lry, uly])/1000.

X = np.linspace(ulx+pix/2, lrx-pix/2, v.shape[1], endpoint=True)
Y = np.linspace(uly-pix/2, lry+pix/2, v.shape[0], endpoint=True)



# mask out areas outside the glacier
shp_files = sorted(glob.glob('glims_download_67032/fid*tif'))
shp_files.remove('glims_download_67032/fid_72.tif')

glacier = 'glims_download_67032/fid_72.tif'

ds = gdal.Open(glacier)
glacierData = ds.ReadAsArray()

for j in np.arange(0,len(shp_files)):
    ds = gdal.Open(shp_files[j])
    internalRock = ds.ReadAsArray()
    glacierData = glacierData-internalRock
    
glacierData[glacierData==0]=np.nan

with rasterio.open('./ITS_Live/ITS_LIVE_composite_utm_cropped.tif') as src:
    # band1 = src.read(1)
    # print('Band1 has shape', band1.shape)
    # arrays_dict[formatted_date] = band1
    meta = src.meta.copy() 

with rasterio.open('./ITS_Live/ITS_LIVE_composite_UTM_Taku.tif', 'w', **meta) as dst:
    dst.write(glacierData.astype(rasterio.float32), 1)

ax1.imshow(glacierData, extent=im_extent, vmin=0, vmax=500, alpha=1)


cbar_ticks = np.linspace(0, 500, 5, endpoint=True)
cmap = matplotlib.cm.viridis
bounds = cbar_ticks
norm = matplotlib.colors.Normalize(vmin=0, vmax=500)
cb = matplotlib.colorbar.ColorbarBase(ax_cbar, cmap=cmap, norm=norm,
                                orientation='horizontal', alpha=1)#,extend='min')
cb.set_label('Speed [m a$^{-1}$]')



#%% zoom in area
xBox = np.array([554.5, 558, 558, 554.5, 554.5])
yBox = np.array([6474, 6474, 6476, 6476, 6474])

ax1.fill(xBox, yBox, color='w', zorder=1001, alpha=0.5, edgecolor='k')

# ax1.annotate('study area', xy=(554.5-3, 6475), xytext=(540-3, 6475),
             # arrowprops=dict(edgecolor=None, facecolor='black', width=1, headwidth=1, headlength=6), va='center', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])

ax1.text((558+554.5)/2, (6470+6474)/2, 'study area', ha='center', va='center', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])

#%% map of alaska
ak = shapefile.Reader('alaska/alaska_censusdotgov.shp')

# this is a multipolygon shapefile

shape = ak.shapeRecords()[0]
parts = shape.shape.parts
for j in np.arange(0, len(parts)):
    start = parts[j]
    
    if j<len(parts)-1:
        stop = parts[j+1]
        feature = LineString(shape.shape.points[start:stop])
    else:
        feature = LineString(shape.shape.points[start:])
        
    featureX, featureY = np.array(feature.coords.xy)
    ax2.fill(featureX, featureY, 'w', edgecolor='k', linewidth=1)
    ax2.plot(1145657, 1108294, '^', color=plt.cm.viridis(1.0), markersize=3)

ax2.axis('equal')
ax2.patch.set_alpha(0)
ax2.set_axis_off()

#ax2.set_xlim([-1200000, 1600000])
#ax2.set_ylim([00000,2800000])


#%% labels
ax1.set_xlabel('Easting [km]')
ax1.set_ylabel('Northing [km]')

plt.savefig('fig1-map.pdf', format='pdf', dpi=300)
