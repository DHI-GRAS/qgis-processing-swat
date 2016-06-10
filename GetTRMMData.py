""""
#-------------------------------------------------------------------------------
# Name:       GetTRMMClimateData
#
# Author:      Cecile Kittel

# Created:     February 2016

********************************************************
This python code
    1. Downloads TRMM 3B42 version 7 3-hourly binary files
    2. Reshapes the data in a grid of size 1440x400
    (see documentation here: ftp://meso-a.gsfc.nasa.gov/pub/trmmdocs/3B42_3B43_doc.pdf
            http://pps.gsfc.nasa.gov/Documents/filespec.TRMM.V7.pdf)
    3. Transforms the data in GeoTiff Format with WGS84 projection
    5. Aggregates the 3-hourly data into daily data
*                                                                                                        *
********************************************************
def main():
    pass

if __name__ == '__main__':
    main()

"""
# The script starts here
import urllib2
from datetime import datetime, timedelta, date
import urllib
import os
import processing
from processing.tools import dataobjects
from osgeo import gdal
from osgeo.gdalconst import *
from osgeo import osr
import shutil
import sys
import os
import os.path
import numpy as np
from numpy import ma
import scipy.io

def TRMM3B42v7Import(startDate, endDate, TRMMVar, TargetDirectory, LeftLon, RightLon, TopLat, BottomLat, log_file, progress):

	#Set initial values
    number_of_days = (endDate - startDate).days +1
    number_of_files = number_of_days*8
    #extent = '-22, 55, -40, 40'
    extent = str(LeftLon) +',' +str(RightLon)+ ',' + str(BottomLat) + ',' + str(TopLat) ##Set extent to crop from global map (min longitude, max longitude, min latitude, max latitude)
    rows = (TopLat-BottomLat)/0.25
    columns = (RightLon-LeftLon)/0.25
    maps = np.zeros((rows, columns, 8))

    log_file.write(extent)

    #Set TRMM variables for download
    product=TRMMVar[4:8]
    urlBase='ftp://disc2.nascom.nasa.gov/data/TRMM/Gridded/3B42_V7'
    tail='z.7.precipitation.bin'
    var='nlat[0:1:399],nlon[0:1:1439],precipitation[0:1:1439][0:1:399]'

    #Define and create necessary paths
    DownloadDirectory = TargetDirectory + os.sep + 'Temporary' + os.sep   # Temporary Download directory contains downloaded .bin files and intermediate tif files

    if not os.path.isdir(TargetDirectory):
        os.mkdir(TargetDirectory)

    # Create Temp download folder
    if not os.path.isdir(DownloadDirectory):
        os.mkdir(DownloadDirectory)


    #loop through the start,end months
    FileList = []
    iteration = 0
    iDate=startDate

    while iDate<=endDate:

        iYear="%04d"%(iDate.year)
        iMonth="%02d"%(iDate.month)
        iDay="%02d"%(iDate.day)
        iDOY="%03d"%iDate.timetuple().tm_yday
        iYMD=iYear[2:4]+iMonth+iDay

        progress_percent = iteration / float(number_of_files) * 100

        # output file saved to DownloadDirectory, with name convention "3B43_yymmdd.hhz.7.precipitation.bin*
        for n in range(0,24,3):
            UrlToRead = urlBase + '/' + iYear + iMonth + '/' + product +'.'+iYMD +'.'+str(n).zfill(2)+ tail
            dst_file = DownloadDirectory + product + '.' + iYMD + '.'+str(n).zfill(2)+tail
            iteration +=1
            progress_percent = iteration / float(number_of_files) * 100
            progress.setPercentage(progress_percent)

            if os.path.isfile(dst_file) == False:
                outfp = open(dst_file,'wb')
                outfp.write(urllib2.urlopen(UrlToRead).read())
                outfp.close()

            text = open(dst_file,'r').read()
            # Check if data is issued on the given day
            if text.find('data file is not present') == -1 and text.find('Not Found') == -1:
                FileList.append(dst_file)
            else:
                os.remove(dst_file)
                break

        iDate+=timedelta(days=1)

    # Convert BIN files to GeoTIFF for wanted resolution
    progress.setConsoleInfo("Translating to GeoTIFF...")
    progress.setPercentage(0)
    TIFF_FileList = bin2GeoTiff_TRMM_WGS84(FileList, extent, tail, log_file, progress)

    # Convert to daily maps for wanted region
    progress.setConsoleInfo("Computing daily maps...")
    progress.setPercentage(0)
    Daily_FileList = TRMM2DailyMaps(TIFF_FileList, TRMMVar, extent, TargetDirectory, maps, log_file, progress)

    for f in os.listdir(DownloadDirectory):
        try:
    	#shutil.rmtree(DownloadDirectory)
	    	os.remove(DownloadDirectory)# Remove Temp dir
        except:
		  pass

    for f in os.listdir(TargetDirectory):
		if f.endswith('.tfw'):
			try:
				os.remove(TargetDirectory + f)
			except:
				pass

    return iteration


def bin2GeoTiff_TRMM_WGS84(FileList, extent, tail, log_file, progress):
    """Translates from binary data source to GeoTIFF files."""
    iteration = 0

    spatial_resolution = 0.25 ## Spatial Resolution of TRMM 3B42 satellite estimates
	##Coordinates of the Thailand Catchment (the area of interest for this study

    tiff_FileList = []
    for f in FileList:
		# Append new filename to list

        if f.endswith(tail):
            tiff_filename = os.path.split(f)[0] + os.sep + 'globalmap.tif' #Save in temporary folder
            out_filename = os.path.split(f)[0] + os.sep + os.path.split(f)[1].split(tail)[0]+'cropped.tif'
            tiff_FileList.append(out_filename)
            if os.path.isfile(out_filename) == False:
		## From TRMM3B42 (Farago, 2015)
                """Step 1 """
                fp1 = open(f, 'rb')
                data_string1 = fp1.read()
                fp1.close()

                """ Step 2."""
            ## the data are recorded like "4-byte float"
                dt=np.dtype('>f4')
                array = np.fromstring(data_string1, dt)
                array=array.reshape((400, 1440))
                array=np.asarray(array, dtype='Float32')
                array = np.flipud(array)
                """ Step 3 """
                output_raster1 = gdal.GetDriverByName('GTiff').Create(tiff_filename,1440, 400, 1, gdal.GDT_Float32)
                #GDALCreate(hDriver, Filename, nXsize, nYsize, nbands)
                geotransform = (-180, 0.25 ,0.0 ,50, 0.0, -0.25)
                    # geotransform[0]: top left x
                    # geotransform[1]: w-e pixel resolution
                    # geotransform[2]: rotation, 0 if image is "north up"
                    # geotransform[3]: top left y
                    # geotransform[4]: rotation, 0 if image is "north up"
                    # geotransform[5]: n-s pixel resolution
                output_raster1.SetGeoTransform(geotransform)
                outband = output_raster1.GetRasterBand(1)
                #outband.SetNoDataValue(-9999.9)
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

                #Crop to region of interest
                """ Step 4"""
                processing.runalg("gdalogr:translate",tiff_filename,100,True,"-9999.9",0,"",extent,False,5,4,75,6,1,False,0,False,"",out_filename)
                iteration += 1
                # Show progress
                progress.setPercentage(iteration/float(len(FileList)) * 100)

    return tiff_FileList


def TRMM2DailyMaps(FileList, TRMM, extent, TargetDirectory, maps, log_file, progress):
    """Calculate daily precipitation from 3-hourly mm/hour files """
    iteration = 0

    # Set map calculation formula
    # Daily sum of 8 files (00, 03, 06, 09, 12, 15, 18, 21) - spilit in two sums since grass only takes up to 6 raster maps
    formula = '3*A+3*B+3*C+3*D+3*E+3*F'
    formula_2 = '3*A+3*B+C'
    corners = extent.split(',')
    LeftLon = float(corners[0])
    RightLon = float(corners[1])
    BottomLat = float(corners[-2])
    TopLat = float(corners[-1])
    rows = int((TopLat-BottomLat)/0.25)
    columns = int((RightLon-LeftLon)/0.25)


    # Get all days - 3B42.<date>.<hour>.<product_version>.HDF.Z
    dates = []
    Daily_FileList = []
    for f in FileList:
    	dates.append(os.path.split(f)[1][5:11])

    # Get unique dates
    unique_dates = list(set(dates))

    # Calculate daily maps
    for datestr in unique_dates:
        #Final output file will be in the format <datestr>_TRMM.tif
        datetime_datestr = datetime.strptime(datestr, "%y%m%d")
        new_datestr = datetime_datestr.strftime("%Y%m%d")
        temporary_name = os.path.split(f)[0] + os.sep + 'daily_rain.tif'
        out_file= TargetDirectory + os.sep + new_datestr + '_' + TRMM + '.tif'
        Daily_FileList.append(out_file)

        if os.path.isfile(out_file) == False: #Check the file doesn't already exist
        	# If all eight daily maps exist
            if dates.count(datestr) == 8:
                log_file.write(datestr)
                #maps = np.zeros((400,1440,8))
                map_number = 0
            	# Get the eight maps
                for f in FileList:
                    if (datestr in f):
                    # Get the eight maps, open them and save in matrix
                        log_file.write(f)
                        crop = gdal.Open(f)
                        myarray = np.array(crop.GetRasterBand(1).ReadAsArray())
                        ##Define Nan = -9999.9
                        myarray[myarray==-9999.9]=np.nan
                        maps[:,:,map_number] = 3*myarray
                        map_number += 1


                    #Once all maps have been added, calculate daily precipitation. No data value is now "nan"
                TRMMdaily = np.sum(maps, axis = 2)
                TRMMdaily_= gdal.GetDriverByName('GTiff').Create(temporary_name,columns, rows, 1, gdal.GDT_Float32)
                geotransform = (LeftLon, 0.25 ,0.0 ,TopLat, 0.0, -0.25)
                # geotransform[0]: top left x
                # geotransform[1]: w-e pixel resolution
                # geotransform[2]: rotation, 0 if image is "north up"
                # geotransform[3]: top left y
                # geotransform[4]: rotation, 0 if image is "north up"
                # geotransform[5]: n-s pixel resolution
                TRMMdaily_.SetGeoTransform(geotransform)     ## Specify its coordinates
                outband = TRMMdaily_.GetRasterBand(1)
                outband.WriteArray(TRMMdaily)
                srs = osr.SpatialReference()
                srs.SetWellKnownGeogCS('WGS84')
                TRMMdaily_.SetProjection( srs.ExportToWkt() )   ## Exports the coordinate system to the file
                outband = None
                srs = None
                TRMMdaily_ = None
                TRMMdaily = None
                processing.runalg("gdalogr:translate",temporary_name,100,True,"-9999.9",0,"",extent,False,5,4,75,6,1,False,0,False,"",out_file)
        #Per datestr, 8 files have been processed per step
        iteration = iteration + 8

		# Show progress
        progress.setPercentage(iteration / float(len(FileList))*100)

    return Daily_FileList

