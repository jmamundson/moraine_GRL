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

import glob
import os

plt.style.use('../moraine.mplstyle')

#%%

# figure size, in inches
cm = 1/2.54
fig_width = 15.6*cm
fig_height = 15.6*cm
plt.figure(figsize=(fig_width,fig_height))

width = 13
height = width*2/3.5
ax_width = width*cm/fig_width
ax_height = height*cm/fig_height
left = 2*cm/fig_width
bot = 0.5*cm/fig_height
ygap = 1.2*cm/fig_height
xgap= 0.4*cm/fig_width

width_small = 6.3
height_small = 6.3
ax_width_small = width_small*cm/fig_width
ax_height_small = width_small*cm/fig_height

ax1 = plt.axes([left, bot+ax_height_small+ygap, ax_width, ax_height])
ax1.set_axisbelow(True)
ax1.grid(visible=True, which='both', zorder=-100, alpha=0.5)

ax2 = plt.axes([left, bot, ax_width_small, ax_height_small])
ax3 = plt.axes([left+ax_width_small+xgap, bot, ax_width_small, ax_height_small])

ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xlim([555.25, 555.75])
ax2.set_ylim([6474.4, 6474.9])

ax3.set_xticks([])
ax3.set_yticks([])
ax3.set_xlim([556.25, 556.75])
ax3.set_ylim([6474.8, 6475.3])

#%% plot background image

# backgroundFile = 'taku_ortho_20231026_utm_1m.tif'
backgroundFile = 'taku_ortho_20240521_utm_1m.tif'

ds = gdal.Open(backgroundFile)
data = np.transpose(ds.ReadAsArray().astype('int'), (1,2,0))
gt = ds.GetGeoTransform()
ulx = gt[0] # UTM easting of upper left corner (top left corner of pixel)
uly = gt[3] # UTM northing of upper left corner (top left corner of pixel)
pix = gt[1] # pixel size [m]
lrx = ulx + pix*data.shape[1] # UTM easting of lower right corner (bottom right corner of pixel)
lry = uly - pix*data.shape[0] # UTM northing of lower right corner (bottom right corner of pixel)
im_extent = np.array([ulx, lrx, lry, uly])/1000.

# check the order here!!!
X = np.linspace(ulx+pix/2, lrx-pix/2, data.shape[0], endpoint=True)
Y = np.linspace(uly-pix/2, lry+pix/2, data.shape[1], endpoint=True)

# image = Image.open(backgroundFile)
# plt.imshow(image,extent=im_extent)

maskShp = shapefile.Reader('clipping_mask.shp')
maskPolygon = shape(maskShp.shapes())

if os.path.exists('mask.npy')==False:
    
    mask = np.ones(data[0].shape)
    
    for j in np.arange(0,len(X)):
            for k in np.arange(0,len(Y)):
                temp_point = Point(X[j], Y[k])
                mask[k, j] = maskPolygon.contains(temp_point)
            
    np.save('mask.npy', mask)

else: 
    mask = np.load('mask.npy')
    
    
#data[:,:,3] = data[:,:,3]*mask

ax1.imshow(data, extent=im_extent, zorder=1)



#%% plot hillshade DEMs

files = sorted(glob.glob('*zone*tif'))

for j in np.arange(0,len(files)):
    
    ds = gdal.Open(files[j])
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

    if j==0:
        ax2.imshow(data, extent=im_extent, cmap='gray')

    else:
        ax3.imshow(data, extent=im_extent, cmap='gray')

#%% plot terminus positions
base_dir = '/hdd/taku/'
terminusPositions = sorted(glob.glob(base_dir + 'uav/surveys/06_terminusPosition/*.shp'))

# color_id = np.linspace(0,1,5)

# color_index = [0, 1, 2, 2, 3, 3, 4]
# color_id = [color_id[x] for x in color_index]
color_id = np.linspace(0, 1, len(terminusPositions), endpoint=True)

for j in np.arange(0,len(terminusPositions)):
    terminus = shapefile.Reader(terminusPositions[j]).shapes()
    terminus = LineString(terminus[0].points)

    terminusX, terminusY = np.array(terminus.coords.xy)/1000
     
    if (j==0) or (np.mod(j,2)==1):
        linestyle = '-'
    else:
        linestyle = (0, (4, 1))
        
    ax1.plot(terminusX, terminusY, color=plt.cm.viridis(color_id[j]), linestyle=linestyle, zorder=2)
    ax2.plot(terminusX, terminusY, color=plt.cm.viridis(color_id[j]), linestyle=linestyle, zorder=2)
    ax3.plot(terminusX, terminusY, color=plt.cm.viridis(color_id[j]), linestyle=linestyle, zorder=2)
    
    
ax1.set_xlim([554.5, 558])
ax1.set_ylim([6474, 6476])
ax1.set_yticks(np.linspace(6474, 6476, 3, endpoint=True))
ax1.set_yticks(np.linspace(6474, 6476, 9, endpoint=True), minor=True)

# ax1.set_yticklabels(np.linspace(6474,6476,5,endpoint=True), rotation=45)
ax1.set_xticks(np.linspace(555,558, 4, endpoint=True))
ax1.set_xticks(np.linspace(554.5, 558, 15, endpoint=True), minor=True)
ax1.legend(('02 Aug 2015', '17 Oct 2021', '05 May 2022', '02 Oct 2022', '22 May 2023', '26 Oct 2023', '21 May 2024'), loc='lower right' )
ax1.set_xlabel('Easting [km]')
ax1.set_ylabel('Northing [km]')


xBox = np.array([555.25, 555.75, 555.75, 555.25, 555.25])
yBox = np.array([6474.4, 6474.4, 6474.9, 6474.9, 6474.4])
ax1.plot(xBox, yBox, color='w', zorder=1000)

xBox = np.array([556.25, 556.75, 556.75, 556.25, 556.25])
yBox = np.array([6474.8, 6474.8, 6475.3, 6475.3, 6474.8])
ax1.plot(xBox, yBox, color='w', zorder=1000)

#%% add panel labels
txt_space = 0.35 # cm

ax1.text(txt_space/width, 1-txt_space/height, 'a', transform=ax1.transAxes, va='top', ha='left')
ax1.text(555.3, 6474.85, 'b', va='top', ha='left', color='k', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])
ax1.text(556.3, 6475.25, 'c', va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])
ax2.text(txt_space/width_small, 1-txt_space/height_small, 'b', transform=ax2.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])
ax3.text(txt_space/width_small, 1-txt_space/height_small, 'c', transform=ax3.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])



#%% plot transects
profiles_shp = '../sediment_profiles/profiles.shp'
profiles = shapefile.Reader(profiles_shp).shapes()

for j in np.arange(0,len(profiles)):
    profile = LineString(profiles[j].points)
    
    X, Y = np.array(profile.coords.xy)/1000
    # ax1.plot(X,Y)



#%%
plt.savefig('fig2-terminus_position.pdf', format='pdf', dpi=300)