"""
***************************************************************************
   SENSAN_utilities.py
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

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy
import os
import math
from SWAT_SENSAN_specs import SWAT_SENSAN_specs
SENSAN_specs = SWAT_SENSAN_specs()

def read_SENSAN_control(snsfile):
    if os.path.isfile(snsfile):
        data =[]
        sns_file = open(snsfile,'r')
        sns = sns_file.readlines()
        sns_file.close
        data.append(sns[3].split()[0]) # No. of parameters
        data.append(sns[3].split()[1]) # No. of observations
        data.append(sns[7].split()[0]) # ABSFLE
        data.append(sns[8].split()[0]) # RELFLE
        data.append(sns[9].split()[0]) # SENSFLE
        sns_info = data
        return(sns_info)

def CSS_SENSAN(SRC_FOLDER, sns_info):
    pct_devfile = SRC_FOLDER + os.sep + 'pct_dev.dat'
    pvfile = SRC_FOLDER + os.sep + SENSAN_specs.VARFLE
    pct_dev = float(numpy.genfromtxt(pct_devfile))/100.
    no_par = int(sns_info[0])
    no_obs = int(sns_info[1])
    no_total = no_obs+no_par
    no_header = math.ceil(no_total/1000.)

    if os.path.isfile(SRC_FOLDER +os.sep + SENSAN_specs.RELFLE):
        file = SRC_FOLDER +os.sep + SENSAN_specs.RELFLE            # out2.dat
        f = open(file, 'r')
        # Skip header
        i = 0
        header = []
        while i < no_header:
            line = f.readline()
            line = line.strip()             # remove spaces
            columns = line.split()          # split into columns
            for c in range(0,len(columns)):
                header.append(columns[c])
            i = i+1
        # Extract data
        data = numpy.zeros([no_par+1,no_total],dtype=float)
        j = 0
        for line in f:
            line = line.strip()             # remove spaces
            columns = line.split()          # split into columns
            for c in range(0,len(columns)):
                data[j,c] = columns[c]
            if len(columns) < 1000:
                j = j+1
        # Exclude baseline run and parameter values
        relO = data[1:,no_par:]
        # Calculate CSS
        CSS = numpy.zeros([no_par],dtype = float)
        for j in range(0,no_par):
            n = 0
            for i in range(0,no_obs):
                if relO[j,i]  < 1e+34:
                    CSS[j] = CSS[j] + abs(relO[j,i]/pct_dev)
                    n = n+1
                    if i == no_obs-1:
                        CSS[j] = CSS[j]/n

    dict = {header[0:no_par][i]:CSS[i] for i in range(0,len(header[0:no_par]))}
    CSS_sort = [x for x in dict.iteritems()]
    CSS_sort.sort(key=lambda x: x[1]) # sort by value
    CSS_sort.reverse()
    CSS_sorted = numpy.zeros([no_par,1],dtype = float)
    p = []
    for i in range(0,no_par):
        CSS_sorted[i] = CSS_sort[i][1]
        p.append(CSS_sort[i][0])

    f = open(SRC_FOLDER + os.sep + 'CSS_output'+".txt", "w")
    for i in range(0,no_par):
        f.write(CSS_sort[i][0] +' '+ str(CSS_sort[i][1]) + ' \r\n')
    f.close

    width = 0.9
    plt.bar(numpy.arange(no_par), CSS_sorted, width, color='b',log=True) # Might add an if statement to figure out whether y-axis should be log.
    plt.ylabel('Composite Scaled Sensitivity (-)')
    plt.xticks(numpy.arange(no_par)+width/2, p, size='xx-small', rotation=90)
    figname = SRC_FOLDER + os.sep + 'CSS_barplot.pdf'
    plt.savefig(figname)
    plt.show()