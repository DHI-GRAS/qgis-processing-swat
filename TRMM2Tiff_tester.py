## Import the necessary libraries to run the code
import sys
import os
import os.path
import numpy as np
from numpy import ma
from osgeo import gdal
from osgeo.gdalconst import *
import sys
import osgeo.osr as osr
import processing
from processing.tools import dataobjects
import scipy.io
import shutil

starttime = time.time()

TargetDirectory = 'C:\\Users\\s113332\\Documents\\TRMM\\2014\\'
TemporaryDirectory = TargetDirectory + 'Temporary' + os.sep
DownloadDirectory = TargetDirectory + 'Download' + os.sep

#if already one, remove temporary folder to remove heavy tiff files.
#try:
#    shutil.rmtree(TemporaryDirectory) # Remove Temp dir
#except:
#    pass
#os.mkdir(TemporaryDirectory) #Create again

spatial_resolution = 0.25 ## Spatial Resolution of TRMM 3B42 satellite estimates
##Coordinates of the Thailand Catchment (the area of interest for this study
extent = '-22, 55, -40, 40' ##Set extent to crop from global map (min longitude, max longitude, min latitude, max latitude)
tail='z.7.precipitation.bin'
FileList = os.listdir(DownloadDirectory)

tiff_FileList = []
for f in FileList:
    # Append new filename to list

    if f.endswith(tail): 
        tiff_filename = TemporaryDirectory + 'globalmap.tif' #Save in temporary folder
        out_filename = TemporaryDirectory+ os.path.split(f)[0] + os.path.split(f)[1].split(tail)[0]+'cropped.tif'
        tiff_FileList.append(out_filename) 
        
    ## From TRMM3B42 (Farago, 2015)
        """Step 1 """
        fp1 = open(DownloadDirectory+f, 'rb')
        data_string1 = fp1.read()
        fp1.close()

    """ Step 2."""
    ## the data are recorded like "4-byte float"
    dt=np.dtype('>f4')
    array = np.fromstring(data_string1, dt)

    ## convert the binary strings to a NumPy array
    array=array.reshape((400, 1440))
    array=np.asarray(array, dtype='Float32')
    array = np.flipud(array) ##This data needs to be flipped on the y axis as it comes out upside down, but does not need to be rotated.

    """ Step 3 """
    output_raster1 = gdal.GetDriverByName('GTiff').Create(tiff_filename,1440, 400, 1, gdal.GDT_Float32)
    geotransform = (-180, 0.25 ,0.0 ,50, 0.0, -0.25)
    	# geotransform[0]: top left x
        # geotransform[1]: w-e pixel resolution
        # geotransform[2]: rotation, 0 if image is "north up"
        # geotransform[3]: top left y
        # geotransform[4]: rotation, 0 if image is "north up"
        # geotransform[5]: n-s pixel resolution
    output_raster1.SetGeoTransform(geotransform)
    outband = output_raster1.GetRasterBand(1)
    outband.WriteArray(array)
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')                ## Set the projection: WGS84
    ##srs.ImportFromEPSG(4326)                     ## This one specifies WGS84 lat long.
    output_raster1.SetProjection( srs.ExportToWkt() )
    output_raster1.GetRasterBand(1).WriteArray(array)
    #outband.FlushCache()

    #Reinitialize
    outband = None
    iceraster = None
    output_raster1 = None
    outarray = None
    array = None
    srs = None

    #Crop to Africa
    """ Step 4"""
    processing.runalg("gdalogr:translate",tiff_filename,100,True,"",0,"",extent,False,5,4,75,6,1,False,0,False,"",out_filename)


#def TRMM2DailyMaps(FileList):
TRMM = 'TRMM3B42'
    # Set map calculation formula
    # Daily sum of 8 files (00, 03, 06, 09, 12, 15, 18, 21) - spilit in two sums since grass only takes up to 6 raster maps
formula = '3*A+3*B+3*C+3*D+3*E+3*F'
formula_2 = '3*A+3*B+C'

tiff_FileList = []
TempFileList = os.listdir(TemporaryDirectory)
for f in TempFileList:
    if f.endswith('cropped.tif'):
        tiff_FileList.append(f)

# Get all days - 3B42.<date>.<hour>.<product_version>.HDF.Z
dates = []
Daily_FileList = []
for f in tiff_FileList:
    dates.append(os.path.split(f)[1][5:11])

    # Get unique dates
unique_dates = list(set(dates))

    # Calculate daily maps
for datestr in unique_dates:
    # If all four daily maps exist
    if dates.count(datestr) == 8:
        maps = []
        # Get the four maps
        for f in tiff_FileList:
            if (datestr in f):
                maps.append(TemporaryDirectory + f)

        # Do map calculations using processing GRASS - the 3-hourly data is a mean per hour. 
        #out_file_intermediate = os.path.split(maps[0])[0] + os.sep + datestr  + '_dailysum_intermediate.tif'
        out_file = TargetDirectory + os.sep + datestr + '_' + TRMM + '.tif'
        Daily_FileList.append(out_file)
        if os.path.isfile(out_file) == False:
        #Add first 6 maps
            layer = dataobjects.getObjectFromUri(maps[0])
            extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
            param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3],'emap':maps[4], 'fmap':maps[5] ,'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0} #, 'outfile': out_file_intermediate}
            data = processing.runalg("grass:r.mapcalculator", param)
            
            #Add last 2 maps
            param = {'amap':maps[6], 'bmap':maps[7], 'cmap':data['outfile'],'formula':formula_2, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file}
            processing.runalg("grass:r.mapcalculator", param)
        

try:
    #shutil.rmtree(DownloadDirectory) 
    shutil.rmtree(TemporaryDirectory)# Remove Temp dir
except:
    pass
            

for f in os.listdir(TargetDirectory):
    if f.endswith('.tfw'):
        try:
            os.remove(TargetDirectory + f)
        except:
            pass
            
totaltime =  time.time() - starttime