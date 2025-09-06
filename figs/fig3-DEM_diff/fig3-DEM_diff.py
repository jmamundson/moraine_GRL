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
fig_height = 12.6*cm
plt.figure(figsize=(fig_width,fig_height))

full_width = 13
width = 6.2
height = width*2/3.5
ax_width = width*cm/fig_width
ax_height = height*cm/fig_height
cbar_height = 0.2*cm/fig_height
left = 2*cm/fig_width
bot = 1.1*cm/fig_height
ygap = 1.2*cm/fig_height
xgap= (full_width-2*width)*cm/fig_width


# ax1 = plt.axes([left, bot+ygap, ax_width, ax_height])
# ax2 = plt.axes([left+ax_width+xgap, bot+ygap, ax_width, ax_height])


ax1 = plt.axes([left, bot + 3*ygap + ax_height + 2*cbar_height, ax_width, ax_height])
ax2 = plt.axes([left, bot+ygap+cbar_height, ax_width, ax_height])

ax1.set_axisbelow(True)
ax1.grid(visible=True, which='both', zorder=-100, alpha=0.5)
ax1.set_xlim([554.5, 558])
ax1.set_ylim([6474, 6476])
ax1.set_yticks(np.linspace(6474, 6476, 3, endpoint=True))
ax1.set_yticks(np.linspace(6474, 6476, 9, endpoint=True), minor=True)
ax1.set_xticks(np.linspace(555,558, 4, endpoint=True))
ax1.set_xticks(np.linspace(554.5, 558, 15, endpoint=True), minor=True)
ax1.set_xlabel('Easting [km]')
ax1.set_ylabel('Northing [km]')

ax2.set_axisbelow(True)
ax2.grid(visible=True, which='both', zorder=-100, alpha=0.5)
ax2.set_xlim([554.5, 558])
ax2.set_ylim([6474, 6476])
ax2.set_yticks(np.linspace(6474, 6476, 3, endpoint=True))
ax2.set_yticks(np.linspace(6474, 6476, 9, endpoint=True), minor=True)
ax2.set_xticks(np.linspace(555,558, 4, endpoint=True))
ax2.set_xticks(np.linspace(554.5, 558, 15, endpoint=True), minor=True)
ax2.set_xlabel('Easting [km]')
ax2.set_ylabel('Northing [km]')

# ax1_cb = plt.axes([left, bot, ax_width, cbar_height])
# ax2_cb = plt.axes([left+ax_width+xgap, bot, ax_width, cbar_height])

ax1_cb = plt.axes([left, bot + cbar_height + 2*ygap + ax_height, ax_width, cbar_height])
ax2_cb = plt.axes([left, bot, ax_width, cbar_height])

ax = [ax1, ax2]
ax_cb = [ax1_cb, ax2_cb]

im_height = 2*cbar_height + 2*ax_height + 3*ygap
ax3 = plt.axes([left+ax_width+xgap, bot, ax_width, im_height])
ax3.set_xticks([])
ax3.set_yticks([])


#%%
photo = Image.open('./photo/terminus_photo.jpg')
ax3.imshow(photo)
npix_y = -np.diff(ax3.get_ylim())
npix_x = npix_y*ax_width*fig_width/(im_height*fig_height)
ax3.set_xlim([ax3.get_xlim()[1]-npix_x, ax3.get_xlim()[1]])

moraine2015 = shapefile.Reader('./photo/moraine2015.shp').shapes()

for j in np.arange(0,len(moraine2015)):
    moraine = LineString(moraine2015[j].points)
    x, y = moraine.coords.xy
    x = np.array(x)
    y = np.array(y)
    
    ax3.plot(x, -y, color=plt.cm.viridis(1))

ax3.text(2100, 2950, '2015 moraine', color=plt.cm.viridis(1), va='top', ha='center', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')]) 

retreat = shapefile.Reader('./photo/arrow.shp').shapes()
retreat = LineString(retreat[0].points)
x, y = retreat.coords.xy
x, y = np.array(x), -np.array(y)
ax3.annotate('', xy=(x[0],y[0]), xytext=(x[1],y[1]), arrowprops=dict(arrowstyle='<|-|>', edgecolor=plt.cm.viridis(1), facecolor=plt.cm.viridis(1)))
ax3.text(np.mean(x)+50, np.mean(y)+50, r'$\sim 80$ m', color=plt.cm.viridis(1), va='top', ha='center', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')])

#%%
mask = np.load('../fig2-terminus_position/mask.npy')

base_dir = '/hdd2/taku/'
DEMs = sorted(glob.glob(base_dir + 'uav/surveys/02_takuGrid/taku_DEM*.tif'))
orthos = sorted(glob.glob(base_dir + 'uav/surveys/02_takuGrid/taku_ortho*.tif'))
# include = [0, 1, 3, 4, 6, 7, 11, 12, 14, 16 ]
# include = [1, 6, 13] # spring
#include = [4, 11, 15, 19] # summer
include = [11, 15] # summers 2023 and 2024
# include = [0, 5, 12] # fall
# include = [1, 3, 4, 5] # 2022
# include = [6, 10, 11, 12] # 2023
DEMs = [DEMs[x] for x in include]
orthos = [orthos[x] for x in include]



refDEM = ['/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/DEMs/taku_DEM_20150802.tif']
refOrtho = ['/hdd2/taku/DEMs_orthomosaics/20150802_ChrisLarsen/orthos/taku_ortho_20150802.tif']

DEMs = refDEM + DEMs
orthos = refOrtho + orthos


# first find offset for refDEM
elevLandingStrip = np.zeros(2)
       
stats = zonal_stats('landingStrip.shp', DEMs[0])
elevLandingStrip[0] = stats[0]['mean']    

stats = zonal_stats('landingStrip.shp', DEMs[-1])    
elevLandingStrip[1] = stats[0]['mean']    
    
dz = np.diff(elevLandingStrip)

# load hillshade for background
hillshade = base_dir + '/uav/surveys/03_hillshades/taku_DEM_20240803.tif'
xDEM, yDEM, hillshade, im_extent = loadgeotiff(hillshade)
_, _, hillshadeMask, _ = loadgeotiff(orthos[-1])
hillshadeMask = hillshadeMask[3,:,:]
hillshadeMask[hillshadeMask<=0] = np.nan
hillshadeMask[hillshadeMask>0] = 1

# then plot DEM differences

for j in np.arange(0,len(DEMs)-1):

    xDEM, yDEM, data1, im_extent = loadgeotiff(DEMs[j])
    _, _, data2, _ = loadgeotiff(DEMs[j+1])

    
    _, _, mask1, _ = loadgeotiff(orthos[j])
    mask1 = mask1[3,:,:]
    mask1[mask1<=0] = np.nan
    mask1[mask1>0] = 1

    _, _, mask2, _ = loadgeotiff(orthos[j+1])
    mask2 = mask2[3,:,:]
    mask2[mask2<=0] = np.nan
    mask2[mask2>0] = 1

    data1 = data1*mask1
    data2 = data2*mask2

    if j==0:
        v_amp = 6
    else:
        v_amp = 2
        
    ax[j].imshow(hillshade*hillshadeMask, extent=im_extent*1e-3, cmap='gray', zorder=1000)
    ax[j].imshow((data2-data1), extent=im_extent*1e-3, cmap='coolwarm_r', alpha=0.75, vmin=-v_amp, vmax=v_amp, zorder=1000)
    
    cbar_ticks = np.linspace(-v_amp, v_amp, 5, endpoint=True)
    bounds = cbar_ticks
    norm = matplotlib.colors.Normalize(vmin=-v_amp, vmax=v_amp)
    cb = matplotlib.colorbar.ColorbarBase(ax_cb[j], cmap='coolwarm_r', norm=norm,
                                    orientation='horizontal', ticks=cbar_ticks, alpha=0.75)#,extend='min')
    cb.set_label('Elevation difference [m]')

# annotations
txt_space = 0.35 # cm
ax1.text(txt_space/width, 1-txt_space/height, r'a  2023/7/27$-$2015/8/2', transform=ax1.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1010) 
ax2.text(txt_space/width, 1-txt_space/height, r'b  2024/8/3$-$2023/7/27', transform=ax2.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1010) 
ax3.text(txt_space/width, 1-txt_space/(im_height*fig_height/cm), 'c  2023/5/22', transform=ax3.transAxes, va='top', ha='left', path_effects=[patheffects.withStroke(linewidth=2, foreground='w')]) 

ax1.annotate('moraine failure', (556.05,6474.55), (556.5, 6474.2), arrowprops=dict(arrowstyle='->', facecolor='black'), path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1001)

ax2.annotate('moraine backfilling', (555.8,6474.74), (556.5, 6474.2), arrowprops=dict(arrowstyle='->', facecolor='black'), path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1001)


landingStrip = shapefile.Reader('./landingStripBox.shp').shapes()
landingStrip = LineString(landingStrip[0].points)
x, y = landingStrip.coords.xy
x = np.concatenate((x, [x[0]]))*1e-3
y = np.concatenate((y, [y[0]]))*1e-3

ax1.plot(x,y,'k--', zorder=1003)
ax2.plot(x,y,'k--', zorder=1003)

vegetatedAreas = shapefile.Reader('./vegetatedAreas.shp').shapes()
for j in np.arange(0, len(vegetatedAreas)):
    area = LineString(vegetatedAreas[j].points)
    x, y = area.coords.xy
    x, y = np.array(x)*1e-3, np.array(y)*1e-3

    ax1.plot(x,y,'w-', zorder=1002)
    ax2.plot(x,y,'w-', zorder=1002)

oozyFlats = [None]*3
stats = zonal_stats('oozyFlats.shp', DEMs[0])
oozyFlats[0] = stats[0]['mean']    

stats = zonal_stats('oozyFlats.shp', DEMs[1])
oozyFlats[1] = stats[0]['mean']    

stats = zonal_stats('oozyFlats.shp', DEMs[2])
oozyFlats[2] = stats[0]['mean']    

print(oozyFlats)

oozyFlats_shp = shapefile.Reader('oozyFlats.shp')
oozyFlats_line = LineString(oozyFlats_shp.shapeRecords()[0].shape.points)
x, y = oozyFlats_line.coords.xy
x, y = np.array(x)*1e-3, np.array(y)*1e-3
ax1.plot(x, y, color='k', zorder=1010)
ax2.plot(x, y, color='k', zorder=1010)

ax1.annotate('Oozy Flats', (557.45,6475.25), (557.6, 6474.75), ha='center', arrowprops=dict(arrowstyle='->', facecolor='black'), path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1001)
ax2.annotate('Oozy Flats', (557.45,6475.25), (557.6, 6474.75), ha='center', arrowprops=dict(arrowstyle='->', facecolor='black'), path_effects=[patheffects.withStroke(linewidth=2, foreground='w')], zorder=1001)

plt.savefig('fig3-DEM.pdf', format='pdf', dpi=300)