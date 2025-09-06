import numpy as np
from osgeo import gdal


def loadDEM(file):
    '''
    
    Parameters
    ----------
    file : location of geotiff

    Returns
    -------
    xDEM : x-coordinates of pixel centers
    yDEM : y-coordinates of pixel centers
    data : elevation data
    im_extent : DEM bounding box (outside edges of pixels)

    '''
    

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


def loadOrtho(file):
    '''
    load drone orthophoto

    Parameters
    ----------
    file : locate of geotiff

    Returns
    -------
    xDEM : x-coordinates of pixel centers
    yDEM : y-coordinates of pixel centers
    data : image data
    im_extent : image bounding box (outside edges of pixels)

    '''
    
    ds = gdal.Open(file)
    data = np.transpose(ds.ReadAsArray().astype('int'), (1,2,0))
    gt = ds.GetGeoTransform()
    ulx = gt[0] # UTM easting of upper left corner (top left corner of pixel)
    uly = gt[3] # UTM northing of upper left corner (top left corner of pixel)
    pix = gt[1] # pixel size [m]
    lrx = ulx + pix*data.shape[1] # UTM easting of lower right corner (bottom right corner of pixel)
    lry = uly - pix*data.shape[0] # UTM northing of lower right corner (bottom right corner of pixel)
    im_extent = np.array([ulx, lrx, lry, uly])
    
    # check the order here!!!
    xOrtho = np.linspace(ulx+pix/2, lrx-pix/2, data.shape[0], endpoint=True)
    yOrtho = np.linspace(uly-pix/2, lry+pix/2, data.shape[1], endpoint=True)
    
    return(xOrtho, yOrtho, data, im_extent)