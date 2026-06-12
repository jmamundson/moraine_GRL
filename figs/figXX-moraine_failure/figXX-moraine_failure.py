import numpy as np
from osgeo import gdal

from matplotlib import pyplot as plt
import matplotlib
from matplotlib import patheffects


from PIL import Image
import shapefile

from shapely.geometry import LineString, Point, Polygon, shape

import rasterstats
from rasterstats import zonal_stats, point_query
import glob
from scipy.interpolate import RegularGridInterpolator

plt.style.use('../moraine.mplstyle')

#%%

def loadgeotiff(file):

    ds = gdal.Open(file)
    data = ds.ReadAsArray().astype('float32')
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

#%% set up figure
cm = 1/2.54
fig_width = 15.6*cm
fig_height = 13.8*cm
fig = plt.figure(figsize=(fig_width,fig_height))

full_width = 13
photo_width = full_width*cm/fig_width
photo_height = full_width/1.5*cm/fig_height
width = 6.2
height = width*1/2
ax_width = width*cm/fig_width
ax_height = height*cm/fig_height
cbar_height = 0.2*cm/fig_height
left = 2*cm/fig_width
bot = 1.1*cm/fig_height
ygap = 0.5*1.2*cm/fig_height
xgap= 0.6*cm/fig_width #(full_width-2*width)*cm/fig_width


# ax1 = plt.axes([left, bot+ygap, ax_width, ax_height])
# ax2 = plt.axes([left+ax_width+xgap, bot+ygap, ax_width, ax_height])


ax1 = plt.axes([left, bot, ax_width, ax_height])
ax2 = plt.axes([left+ax_width+xgap, bot, ax_width, ax_height])
ax3 = plt.axes([left, bot+ax_height+ygap, photo_width, photo_height])
ax4 = plt.axes([left + photo_width - (0.9*ax_width+xgap), (bot+ax_height+ygap) + photo_height - (0.9*ax_height+ygap), 0.9*ax_width, 0.9*ax_height])

ax1.set_axisbelow(True)
#ax1.grid(visible=True, which='both', zorder=-100, alpha=0.5)
ax1.set_xlim([555, 557])
ax1.set_ylim([6474, 6475])
ax1.set_yticks(np.linspace(6474, 6475, 2, endpoint=True))
ax1.set_yticks(np.linspace(6474, 6475, 5, endpoint=True), minor=True)
ax1.set_xticks(np.linspace(555, 557, 3, endpoint=True))
ax1.set_xticks(np.linspace(555, 557, 9, endpoint=True), minor=True)
ax1.set_xlabel('Easting [km]')
ax1.set_ylabel('Northing [km]')

ax2.set_axisbelow(True)
#ax2.grid(visible=True, which='both', zorder=-100, alpha=0.5)
ax2.set_xlim([555, 557])
ax2.set_ylim([6474, 6475])
ax2.set_yticks(np.linspace(6474, 6475, 2, endpoint=True))
ax2.set_yticks(np.linspace(6474, 6475, 5, endpoint=True), minor=True)
ax2.set_yticklabels('')
ax2.set_xticks(np.linspace(555, 557, 3, endpoint=True))
ax2.set_xticks(np.linspace(555, 557, 9, endpoint=True), minor=True)
ax2.set_xlabel('Easting [km]')
ax2.set_ylabel('')

ax3.set_xticks([])
ax3.set_yticks([])

ax4.set_xticks([0, 50, 100])
ax4.set_xticklabels([0,50,100], path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax4.set_xlim([0,100])
ax4.set_yticks([4,8,12])
ax4.set_yticklabels([4,8,12], path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax4.set_ylim([4,12])
ax4.set_xlabel('Distance [m]', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax4.set_ylabel('Elevation [m]', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])

# ax1_cb = plt.axes([left, bot, ax_width, cbar_height])
# ax2_cb = plt.axes([left+ax_width+xgap, bot, ax_width, cbar_height])


ax = [ax1, ax2, ax3, ax4]

txt_space = 0.35 # cm
ax1.text(txt_space*cm/fig_width/ax1.get_position().width, 1-txt_space*cm/fig_height/ax1.get_position().height, 'b  2020/9/14', transform=ax1.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')], zorder=1010)

ax2.text(txt_space*cm/fig_width/ax2.get_position().width, 1-txt_space*cm/fig_height/ax2.get_position().height, 'c  2021/6/19', transform=ax2.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')], zorder=1010) 
ax3.text(txt_space*cm/fig_width/ax3.get_position().width, 1-txt_space*cm/fig_height/ax3.get_position().height, 'a  2020/7/31', transform=ax3.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')], zorder=1010) 
ax4.text(txt_space*cm/fig_width/ax4.get_position().width, 1-txt_space*cm/fig_height/ax4.get_position().height, 'd', transform=ax4.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')], zorder=1010) 


ax4.text(0,12,'A', ha='center', va='bottom', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax4.text(100,12,'A$^\prime$', ha='center', va='bottom', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])

#%
file1 = '/hdd2/taku/DEMs_orthomosaics/WorldView_ChrisMcNeil/orthos/20200914_104001005F0DD500_1040010060144400_ortho_cropped.tif'
file2 = '/hdd2/taku/DEMs_orthomosaics/WorldView_ChrisMcNeil/orthos/20210619_104001006A4BDD00_104001006AAA9000_ortho_cropped.tif'
photo = './20200731-163909.jpg'

DEM2015 = '/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/DEMs/Taku_terminus.tif'
DEM2023 = '/hdd2/taku/uav/surveys/02_takuGrid/taku_DEM_20230727.tif'

x1, y1, image1, im_extent = loadgeotiff(file1)
x2, y2, image2, im_extent = loadgeotiff(file2)

photoAerial = Image.open(photo)
photoArray = np.array(photoAerial)

photo_shp = shapefile.Reader('photoOutline.shp')
photo_line = LineString(photo_shp.shapeRecords()[0].shape.points)
x, y = photo_line.coords.xy

terrace_shp = shapefile.Reader('terraceProfile.shp')
terrace_line = LineString(terrace_shp.shapeRecords()[0].shape.points)
terraceX, terraceY = np.array(terrace_line.coords.xy)

terraceX, terraceY = np.linspace(terraceX[0], terraceX[-1], 1000, endpoint=True), np.linspace(terraceY[0], terraceY[-1], 1000, endpoint=True) 
dist = np.sqrt((terraceX-terraceX[0])**2+(terraceY-terraceY[0])**2)
# stack the new points and create a LineString for extract profiles with rasterstats
XY = np.vstack((terraceX,terraceY)).T
profile = LineString(XY)
 
### Extra surface elevations from DEMs
elev2015 = np.array(rasterstats.point_query(profile, DEM2015)[0])+0.45
elev2023 = np.array(rasterstats.point_query(profile, DEM2023)[0])



ax[0].imshow(image1, extent=im_extent*1e-3, cmap='gray', vmin=100, vmax=700)        
ax[1].imshow(image2, extent=im_extent*1e-3, cmap='gray', vmin=50, vmax=200)    

ax[0].fill(np.array(x)*1e-3, np.array(y)*1e-3,'w', alpha=0.2)
ax[0].plot(np.array(x)*1e-3, np.array(y)*1e-3,'w', alpha=0.8)

ax[0].plot(terraceX*1e-3, terraceY*1e-3, 'r', linewidth=1)
ax[0].text(terraceX[0]*1e-3-0.01, terraceY[0]*1e-3+0.01, 'A', ha='right', va='bottom', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax[0].text(terraceX[-1]*1e-3+0.01, terraceY[-1]*1e-3-0.01, 'A$^\prime$', ha='left', va='top', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
           

ax[2].imshow(photoAerial)
ax[2].annotate('moat', arrowprops=dict(arrowstyle='-|>', edgecolor='k', facecolor='k'), xy=(1400,1260), xytext=(700,1500), xycoords='data', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax[2].annotate('fluvial terrace', arrowprops=dict(arrowstyle='-|>', edgecolor='k', facecolor='k'), xy=(2450,2230), xytext=(2525,1890), xycoords='data', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax[2].text(1190, 1840, 'outwash plain', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])
ax[2].text(200, 1000, 'Norris River', path_effects=[patheffects.withStroke(linewidth=0.75, foreground='w')])

color_id = np.linspace(0.5,1,4)
ax[3].plot(dist, elev2015, 'r', label='2025/8/2')
ax[3].plot(dist, elev2023, color=plt.cm.Blues(color_id[1]), label='2023/7/27')
ax[3].legend()

#%%

plt.savefig('figXX-moraine_failure.pdf', format='pdf', dpi=300)
