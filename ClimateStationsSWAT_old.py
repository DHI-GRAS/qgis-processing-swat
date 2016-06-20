"""
***************************************************************************
   ClimateStationsSWAT.py
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
"""

from datetime import date, timedelta
import os
import numpy
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

class ClimateStationsSWAT_old(GeoAlgorithmExecutionException):

    def __init__(self, stations_filename):
        if os.path.isfile(stations_filename):
            self.station_filename = stations_filename
            self.station_id = []
            self.station_lati = []
            self.station_long = []
            self.station_elev = []

            # Reading station file
            station_file = open(stations_filename,'r').readlines()
            for line in station_file:
                try:
                    int(line[0:6])
                    self.station_id.append(line[0:6])
                    self.station_lati.append(float(line[37:42])/100)
                    self.station_long.append(float(line[43:49])/100)
                    self.station_elev.append(int(line[50:55]))
                except ValueError:
                    pass

            # Convert id's to dictionary
            self.station_id_dict = {}
            for i in self.station_id:
                self.station_id_dict[int(i)] = i
        else:
            raise GeoAlgorithmExecutionException('No such file: \"' + stations_filename + '\" ')


    def readSWATpcpFiles(self, log_file):
        """Reading the SWAT .pcp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)

        # Reading .pcp files to numpy array
        pcp_array = None
        pcp_dates = []
        for i in station_id_sorted:
            station_pcp_filename = station_folder + os.sep + self.station_id_dict[i] + '.pcp'
            if os.path.isfile(station_pcp_filename):
                pcp_file = open(station_pcp_filename,'r').readlines()
                if pcp_array == None:
                    pcp_array = numpy.zeros([len(pcp_file)-4,len(station_id_sorted)],dtype=numpy.float)
                for n in range(4,len(pcp_file)):
                    if i == 1:
                        pcp_dates.append(pcp_file[n][0:7])
                    pcp_array[n-4,i-1] = float(pcp_file[n][7:12])
            else:
                raise GeoAlgorithmExecutionException('No .pcp file found: \"' + station_pcp_filename + '\" ')

        if pcp_dates != []:
            # From Julian day to date
            last_pcp_date = date(int(pcp_dates[-1][0:4]),1,1) + timedelta(days=int(pcp_dates[-1][4:7])-1)
            first_pcp_date = date(int(pcp_dates[0][0:4]),1,1) + timedelta(days=int(pcp_dates[0][4:7])-1)
##            log_file.write("First day of pcp in .pcp file: %s \n"%first_pcp_date.strftime('%Y%m%d'))
##            log_file.write("Last day of pcp in .pcp file: %s \n"%last_pcp_date.strftime('%Y%m%d'))
        else:
            last_pcp_date = None
            first_pcp_date = None

        return pcp_dates, first_pcp_date, last_pcp_date, pcp_array


    def readSWATtmpFiles(self,log_file):
        """Reading the SWAT .tmp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)

        # Reading old .tmp files to numpy array
        tmp_max_array = None
        tmp_min_array = None
        tmp_dates = []
        for i in station_id_sorted:
            station_tmp_filename = station_folder + os.sep + self.station_id_dict[i] + '.tmp'
            if os.path.isfile(station_tmp_filename):
                tmp_file = open(station_tmp_filename,'r').readlines()
                if tmp_max_array == None:
                    tmp_max_array = numpy.zeros([len(tmp_file)-4,len(station_id_sorted)],dtype=numpy.float)
                    tmp_min_array = numpy.zeros([len(tmp_file)-4,len(station_id_sorted)],dtype=numpy.float)
                for n in range(4,len(tmp_file)):
                    if i == 1:
                        tmp_dates.append(tmp_file[n][0:7])
                    tmp_max_array[n-4,i-1] = float(tmp_file[n][7:12])
                    tmp_min_array[n-4,i-1] = float(tmp_file[n][12:17])
            else:
                raise GeoAlgorithmExecutionException('No .tmp file found: \"' + station_pcp_filename + '\" ')

        if tmp_dates != []:
            # From Julian day to date
            last_tmp_date = date(int(tmp_dates[-1][0:4]),1,1) + timedelta(days=int(tmp_dates[-1][4:7])-1)
            first_tmp_date = date(int(tmp_dates[0][0:4]),1,1) + timedelta(days=int(tmp_dates[0][4:7])-1)
##            log_file.write("First day of tmp in .tmp file: %s \n"%first_tmp_date.strftime('%Y%m%d'))
##            log_file.write("Last day of tmp in .tmp file: %s \n"%last_tmp_date.strftime('%Y%m%d'))
        else:
            last_tmp_date = None
            first_tmp_date = None

        return tmp_dates, first_tmp_date, last_tmp_date, tmp_max_array, tmp_min_array


    def writeSWATpcpFiles(self, pcp_juliandates, pcp_array, log_file):
        """Write the SWAT .pcp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)

        # Writing .pcp files
        for i in station_id_sorted:
            station_pcp_filename = station_folder + os.sep + self.station_id_dict[i] + '.pcp'
            if os.path.isfile(station_pcp_filename):
                old = open(station_pcp_filename, "r").readlines() # read everything in the file
                with open(station_pcp_filename, "w") as f:
                    for l in range(0,4): # Write header
                        f.write(old[l])
                    for l in range(0,len(pcp_juliandates)): # Write array to file
                        f.write(pcp_juliandates[l])
                        f.write(("%.1f" %pcp_array[l,i-1]).zfill(5))
                        f.write('\n')
            else:
                raise GeoAlgorithmExecutionException('No .pcp file found:: \"' + station_pcp_filename + '\" ')


    def writeSWATtmpFiles(self, tmp_juliandates, tmp_max_array, tmp_min_array, log_file):
        """Write the SWAT .pcp files for all stations in station file"""
        station_folder = os.path.split(self.station_filename)[0]

        # Sort id's
        station_id_sorted = sorted(self.station_id_dict)

        # Writing .pcp files
        for i in station_id_sorted:
            station_tmp_filename = station_folder + os.sep + self.station_id_dict[i] + '.tmp'
            if os.path.isfile(station_tmp_filename):
                old = open(station_tmp_filename, "r").readlines() # read everything in the file
                with open(station_tmp_filename, "w") as f:
                    for l in range(0,4): # Write header
                        f.write(old[l])
                    for l in range(0,len(tmp_juliandates)): # Write array to file
                        f.write(tmp_juliandates[l])
                        f.write(("%.1f" %tmp_max_array[l,i-1]).zfill(5))
                        f.write(("%.1f" %tmp_min_array[l,i-1]).zfill(5))
                        f.write('\n')

            else:
                raise GeoAlgorithmExecutionException('No .tmp file found: \"' + station_tmp_filename + '\" ')

    def writeSWATrunClimateFiles(self, InOut_folder, log_file):

        dirs = os.listdir(InOut_folder)
        pcp_file, tmp_file, watershed_file = False, False, False
        # Get files
        for f in dirs:
            if '.pcp' in f:
                pcp_file = InOut_folder + os.sep + f
            if '.tmp' in f:
                tmp_file = InOut_folder + os.sep + f
            if '.fig' in f:
                watershed_file = InOut_folder + os.sep + f

        if not (pcp_file or tmp_file or watershed_file):
            raise GeoAlgorithmExecutionException('Missing SWAT files in folder: \"' + InOut_folder + '\" ')

        sub_info = {}
        watershed_lines = open(watershed_file,'r').readlines()
        # connect subbasin to sub file
        for i in range(0,len(watershed_lines)):
            if 'subbasin' in watershed_lines[i]:
                sub_info[int(watershed_lines[i][22:28])] = {'sub_file':watershed_lines[i+1][10:23]}

        # Add info on lat, long and elevation
        for i in range(0,len(self.station_id)):
            sub_info[int(self.station_id[i])]['lat'] = self.station_lati[i]
            sub_info[int(self.station_id[i])]['long'] = self.station_long[i]
            sub_info[int(self.station_id[i])]['elev'] = self.station_elev[i]

        # Get subbasin info
        pcp_stations = []
        tmp_stations = []
        for sub in sub_info.keys():
            sub_lines = open(InOut_folder + os.sep + sub_info[sub]['sub_file'],'r').readlines()
            sub_info[sub]['pcp_station'] = int(sub_lines[6][0:16])
            sub_info[sub]['tmp_station'] = int(sub_lines[7][0:16])
            pcp_stations.append(sub_info[sub]['pcp_station'])
            tmp_stations.append(sub_info[sub]['tmp_station'])

        log_file.write(str(sub_info))
        # Get data
        pcp_dates, first_pcp_date, last_pcp_date, pcp_array = self.readSWATpcpFiles(None)
        tmp_dates, first_tmp_date, last_tmp_date, tmp_max_array, tmp_min_array = self.readSWATtmpFiles(None)

        # Put all info into numpy arrays and get lines to write
        pcp_DataLines = pcp_dates
        pcp_stations_array = numpy.zeros([3,max(pcp_stations)])
        new_pcp_array = numpy.zeros(pcp_array.shape)
        for i in range(1,max(pcp_stations)+1):
            pcp_station = sub_info[i]['pcp_station']
            pcp_stations_array[0,pcp_station-1] = sub_info[i]['lat']
            pcp_stations_array[1,pcp_station-1] = sub_info[i]['long']
            pcp_stations_array[2,pcp_station-1] = sub_info[i]['elev']
            new_pcp_array[:,pcp_station-1] = pcp_array[:,i-1]
        for i in range(0,max(pcp_stations)):
            for n in range(0,pcp_array.shape[0]):
                pcp_DataLines[n] = pcp_DataLines[n] + ('%.1f' %new_pcp_array[n,i]).zfill(5)

        tmp_DataLines = tmp_dates
        tmp_stations_array = numpy.zeros([3,max(tmp_stations)])
        new_tmp_max_array = numpy.zeros(tmp_max_array.shape)
        new_tmp_min_array = numpy.zeros(tmp_min_array.shape)
        for i in range(1,max(tmp_stations)+1):
            tmp_station = sub_info[i]['tmp_station']
            tmp_stations_array[0,tmp_station-1] = sub_info[i]['lat']
            tmp_stations_array[1,tmp_station-1] = sub_info[i]['long']
            tmp_stations_array[2,tmp_station-1] = sub_info[i]['elev']
            new_tmp_max_array[:,tmp_station-1] = tmp_max_array[:,i-1]
            new_tmp_min_array[:,tmp_station-1] = tmp_min_array[:,i-1]
        for i in range(0,max(tmp_stations)):
            for n in range(0,tmp_max_array.shape[0]):
                tmp_DataLines[n] = tmp_DataLines[n] + ('%.1f' %new_tmp_max_array[n,i]).zfill(5) + ('%.1f' %new_tmp_min_array[n,i]).zfill(5)

        # Defining headers
        title = 'Precipitation Input File ' + pcp_file + ' ' + date.today().strftime('%Y%m%d') + '\n'
        LatLine = 'Lati   '
        LongLine = 'Long   '
        ElevLine = 'Elev   '
        for i in range(0,max(pcp_stations)):
            LatLine = LatLine + '%5s' %('%.1f' %pcp_stations_array[0,i])
            LongLine = LongLine + '%5s' %('%.1f' %pcp_stations_array[1,i])
            ElevLine = ElevLine + '%5s' %int(pcp_stations_array[2,i])
        # Write file
        with open(pcp_file, "w") as f:
                    f.write(title)
                    f.write(LatLine)
                    f.write('\n')
                    f.write(LongLine)
                    f.write('\n')
                    f.write(ElevLine)
                    f.write('\n')
                    for l in pcp_DataLines: # Write array to file
                        f.write(l)
                        f.write('\n')

        # Defining headers
        title = 'Temperature Input File ' + tmp_file + ' ' + date.today().strftime('%Y%m%d') + '\n'
        LatLine = 'Lati   '
        LongLine = 'Long   '
        ElevLine = 'Elev   '
        for i in range(0,max(pcp_stations)):
            LatLine = LatLine + '%10s' %('%.1f' %tmp_stations_array[0,i])
            LongLine = LongLine + '%10s' %('%.1f' %tmp_stations_array[1,i])
            ElevLine = ElevLine + '%10s' %int(tmp_stations_array[2,i])
        # Write file
        with open(tmp_file, "w") as f:
                    f.write(title)
                    f.write(LatLine)
                    f.write('\n')
                    f.write(LongLine)
                    f.write('\n')
                    f.write(ElevLine)
                    f.write('\n')
                    for l in tmp_DataLines: # Write array to file
                        f.write(l)
                        f.write('\n')
        return(last_pcp_date,last_tmp_date)