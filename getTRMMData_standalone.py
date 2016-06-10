## Import the necessary libraries to run the code
## 1 year will take around 1 hour 10 minutes
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
import time
import datetime
from datetime import datetime

starttime = time.time()
TargetDirectory =  'C:\\Users\\s113332\\Documents\\TRMM\\TRMM_daily_tiff_Africa\\2006\\'
TemporaryDirectory = TargetDirectory + 'Temporary' + os.sep
#DownloadDirectory = 'N:\\TRMM\\2013\\'
DownloadDirectory = 'C:\\Users\\s113332\\Documents\\TRMM\\TRMM_data\\2006\\'
if os.path.isdir(TargetDirectory) == False:
    os.mkdir(TargetDirectory)
    if os.path.isdir(TemporaryDirectory)==False:
        os.mkdir(TemporaryDirectory)

spatial_resolution = 0.25 ## Spatial Resolution of TRMM 3B42 satellite estimates
##Coordinates of the Africa
extent = '-22, 55, -40, 40' ##Set extent to crop from global map (min longitude, max longitude, min latitude, max latitude)
tail='z.7.precipitation.bin'
FileList = os.listdir(DownloadDirectory)
tiff_FileList = []
dates = []
Daily_FileList = []

#def TRMM2DailyMaps(FileList):
TRMM = 'TRMM3B42'
# Set map calculation formula
# Daily sum of 8 files (00, 03, 06, 09, 12, 15, 18, 21) - split in two sums since grass only takes up to 6 raster maps
formula = '3*A+3*B+3*C+3*D+3*E+3*F' #Adds first 6 maps using formula 1 - multiply each by 3 to get the total sum for the 3 hour period.
formula_2 = '3*A+3*B+C' #C is the map produced by formula 1

#Establish list of days
for f in FileList:
    if f.endswith(tail): 
# Get all days - 3B42.<date>.<hour>.<product_version>.bin
        dates.append(os.path.split(f)[1][5:11])
    # Get unique dates
        unique_dates = list(set(dates))
    
# Find all files from unique day
for datestr in unique_dates:
# If all four daily maps exist
    if dates.count(datestr) == 8:
        DayFiles = []
                # Get the four maps
        for f in FileList:
            if (datestr in f):
                DayFiles.append(f)
    
        #Final output file will be in the format <datestr>_TRMM.tif
        datetime_datestr = datetime.strptime(datestr, "%y%m%d")
        new_datestr = datetime_datestr.strftime("%Y%m%d")
        out_file_final = TargetDirectory + os.sep + new_datestr + '_' + TRMM + '.tif'
        Daily_FileList.append(out_file_final)
        out_file = TargetDirectory + os.sep + datestr + '_' + TRMM + '.tif'
        
    #Only run if the file doesn't already exist:
    if os.path.isfile(out_file_final) == False and os.path.isfile(out_file) == False:
    #Run loop over all files
        for f in DayFiles:
            if f.endswith(tail): 
                tiff_filename = TemporaryDirectory + 'globalmap.tif' #Save in temporary folder
                out_filename = TemporaryDirectory+ os.path.split(f)[0] + os.path.split(f)[1][12:14]+'cropped.tif'
                tiff_FileList.append(out_filename) 
        
            ## From TRMM3B42 (Farago, 2015)
                """Step 1 """
                fp1 = open(DownloadDirectory + f, 'rb')
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
            output_raster1.SetProjection( srs.ExportToWkt() )
            output_raster1.GetRasterBand(1).WriteArray(array)

        #Reinitialize
            outband = None
            iceraster = None
            output_raster1 = None
            outarray = None
            array = None
            srs = None

        #Crop to Africa
            """ Step 4"""
            processing.runalg("gdalogr:translate",tiff_filename,100,True,"-9999.9",0,"",extent,False,5,4,75,6,1,False,0,False,"",out_filename)

        maps = []
    # Get the eight maps
        for f in tiff_FileList:
            maps.append(f)

    # Do map calculations using processing GRASS - the 3-hourly data is a mean per hour. 
    #out_file_intermediate = os.path.split(maps[0])[0] + os.sep + datestr  + '_dailysum_intermediate.tif'
    #Add first 6 maps
        layer = dataobjects.getObjectFromUri(maps[0])
        extent = str(layer.extent().xMinimum())+","+str(layer.extent().xMaximum())+","+str(layer.extent().yMinimum())+","+str(layer.extent().yMaximum())
        param = {'amap':maps[0], 'bmap':maps[1], 'cmap':maps[2], 'dmap':maps[3],'emap':maps[4], 'fmap':maps[5] ,'formula':formula, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0} #, 'outfile': out_file_intermediate}
        data = processing.runalg("grass:r.mapcalculator", param)
            
    #Add last 2 maps
        param = {'amap':maps[6], 'bmap':maps[7], 'cmap':data['outfile'],'formula':formula_2, 'GRASS_REGION_PARAMETER':extent, 'GRASS_REGION_CELLSIZE_PARAMETER':0, 'outfile':out_file_final}
        processing.runalg("grass:r.mapcalculator", param)
        
    if os.path.isfile(out_file) == True:
        os.rename(out_file, out_file_final)



try:
    #shutil.rmtree(DownloadDirectory)
    shutil.rmtree(TemporaryDirectory) # Remove Temp dir
except:
    pass
            

for f in os.listdir(TargetDirectory):
    if f.endswith('.tfw'):
        try:
            os.remove(TargetDirectory + f)
        except:
            pass

total_time = time.time()-starttime