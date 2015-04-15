"""
***************************************************************************
    ASS_module1_PrepData.py
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

# Import modules
from matplotlib.pylab import *
import numpy
import os
import csv
from datetime import date, timedelta
from ASS_utilities import EstimateLosses

def MakedrainsTo(src_folder):
    """Creating drainsTo from the fig.fig file"""
    filename = src_folder + os.sep + 'fig.fig'
    watershed_file = open(filename,'r').readlines()

    routes = {}
    add = {}

    for l in watershed_file:
        try:
            if int(l[11:16]) == 2:
                routes[int(l[16:22])] = [int(l[22:28]),int(l[28:34])]
            elif int(l[11:16]) == 5:
                add[int(l[16:22])] = [int(l[22:28]),int(l[28:34])]
        except:
            pass

    nbrch = min(routes.keys())-1        #The total number of reaches in the basin
    catch = {}
    for c in routes.keys():
        reach = routes[c][0]
        inflow = routes[c][1]
        catch[reach] = [inflow]
        if reach == inflow:
            pass
        else:
            j = [1]
            while j:
                new_inflow = []
                for n in catch[reach]:
                    if n <= nbrch:
                        new_inflow.append(n)
                    else:
                        try:
                            for m in add[n]:
                                new_inflow.append(m)
                        except:
                            new_inflow.append(routes[n][1])
                catch[reach] = new_inflow
                j = [i for i in catch[reach] if i > nbrch]

    catchs=sorted(catch, key=lambda k: len(catch[k]))

    drainsTo_dict = {}
    for i in range(1,nbrch+1):
        tempIndex = []
        for k in catchs:
            for m in range(0,len(catch[k])):
                if catch[k][m] == i:
                    tempIndex.append(k)
                else:
                    pass
        drainsTo_dict[i] = tempIndex

    drainsTo = numpy.zeros([nbrch])
    for j in range (0,nbrch):
        if len(drainsTo_dict[j+1])>1:
            drainsTo[j] = (int(drainsTo_dict[j+1][1]))
        else:
            drainsTo[j] = 0             #outlets are assigned 0

    return(drainsTo)

def GetMuskingumParameters(nbrch,src_folder):
    """Getting the Muskingum parameters from the .rte and basins.bsn files"""

    #Getting the lengths, widths, depths, slope and Manning n of the reaches from the .rte files
    width = numpy.zeros([nbrch])
    length = numpy.zeros([nbrch])
    depth = numpy.zeros([nbrch])
    slope = numpy.zeros([nbrch])
    manning_n = numpy.zeros([nbrch])

    for rch in range(1,nbrch+1):
        filename = src_folder + os.sep + str(rch).zfill(5).ljust(9,'0') +'.rte'
        if os.path.isfile(filename):
            rte_file = open(filename,'r')
            rte = rte_file.readlines()
            rte_file.close
            width[rch-1] = float(rte[1][0:20])      #Average width of main channel at top of bank [m]
            length[rch-1] = float(rte[4][0:20])     #Average length of main channel [km]
            depth[rch-1] = float(rte[2][0:20])      #Main channel depth, from top of bank to bottom [m]
            slope[rch-1] = float(rte[3][0:20])      #Main channel slope [m/m]
            manning_n[rch-1] = float(rte[5][0:20])  #Manning's nvalue for main channel

    #Getting the Muskingum parameters from the basins.bsn file
    if os.path.isfile(src_folder + os.sep + 'basins.bsn'):
        bsn_file = open(src_folder + os.sep + 'basins.bsn','r')
        bsn = bsn_file.readlines()
        bsn_file.close
        MSK_CO1 = float(bsn[58][0:20])    #Calibration coefficient used to control impact of the storage time constant (Km) for normal flow
        MSK_CO2 = float(bsn[59][0:20])    #Calibration coefficient used to control impact of the storage time constant (Km) for low flow
        MSK_X = float(bsn[60][0:20])

    z_ch = 2.                            #p. 429 in the SWAT documentation
    width_btm = width -2*2*depth        #Calculation the bottom withs
    for i in range(0,len(width_btm)):
        if width_btm[i]<=0:
            width_btm[i] = 0.5*width[i]
        else:
            pass

    depth_add = 1.                                                  #Depth added to bottom (after Milzow, 2010)
    A_ch = width_btm*depth+z_ch*depth*depth+depth_add*width_btm/2.  #Cross sectional area of flow in the channel for modified channel geometry (see Milzow, 2010)
    A_ch_01 = width_btm*0.1*depth+z_ch*0.1*depth*0.1*depth+depth_add*width_btm/2.  #Cross sectional area when flow is 0.1 bankfull for modified channel geometry (see Milzow, 2010)
##    A_ch = (width_btm+z_ch*depth)*depth+0.5*width_btm               #Cross sectional area of flow in the channel
##    A_ch_01 = (width_btm+z_ch*0.1*depth)*0.1*depth+0.5*width_btm    #Cross sectional area when flow is 0.1 bankfull

    P_ch = (width_btm*width_btm+(depth_add*z_ch)**2)**0.5+2*depth*(1+z_ch**2)**0.5       #Wetted perimeter of the channel for modified channel geometry (see Milzow, 2010)
    P_ch_01 = (width_btm*width_btm+(depth_add*z_ch)**2)**0.5+2*0.1*depth*(1+z_ch**2)**0.5  #Wetted perimeter of the channel when flow is 0.1 bankfull for modified channel geometry (see Milzow, 2010)

    R_ch = A_ch/P_ch                                #Hydraulic radius for bankfull flow
    R_ch_01 = A_ch_01/P_ch_01                       #Hydraulic radius for 0.1 bankfull flow

    c_k = (5.0/3.0)*((R_ch**(2.0/3.0)*slope**(1.0/2.0))/manning_n)          #Celerity for bankfull
    c_k_01 = (5.0/3.0)*((R_ch_01**(2.0/3.0)*slope**(1.0/2.0))/manning_n)    #Celerity for 0.1 bankfull

    K_1 = 1000*length/c_k/86400                           #K for bankfull in days
    K_01 = 1000*length/c_k_01/86400                       #K for 0.1 bankfull in days

    msk1 = MSK_CO1/(MSK_CO1+MSK_CO2)             # (msk_co1 + msk_co2 = 1.) See line 130 in rtmusk.f in SWAT source code
    msk2 = MSK_CO2/(MSK_CO1+MSK_CO2)
    MSK_CO1 = msk1
    MSK_CO2 = msk2

    K = (MSK_CO1*K_1+MSK_CO2*K_01)
    X = numpy.ones([nbrch])*MSK_X

    return(X,K)

def GetInput(src_folder,nbrch,header,Startdate,Enddate):
    """Getting the runoff from the output.sub file"""

    filename = src_folder + os.sep + 'output.sub'
    deli= [6,4,9,6,10,10,10,10,10,10,10,10,10,10,10,10,10,10]
    area = numpy.genfromtxt(filename, delimiter=deli, skip_header = header, usecols=4)
    data = numpy.genfromtxt(filename, delimiter=deli, skip_header = header, usecols=13)

    totsub = nbrch                          #Total number of subbasins in the SWAT model
    days = int(Enddate-Startdate)+1         #Number of days for which the data should be read. Has to be <= than the total number of days simulated
    WYLD_Qmm = numpy.zeros([days,totsub])
    for p in range(0,totsub):
        for i in range(0,days):
            WYLD_Qmm[i,p] = data[i*totsub+(p)]

    #Get WYLD in m3/day
    WYLD_Q = numpy.zeros([days,totsub])
    RR = numpy.zeros([days,totsub])

    for i in range(0,totsub):
        WYLD_Q[:,i] = WYLD_Qmm[:,i]*area[i]*1000/86400       #WYLD_Q in m3/s

    RR = WYLD_Q

    return(RR)

def DefaultErrorModel(nbrch):
    """Create defaults for the error model"""

    alphaerr = numpy.ones([nbrch])*-99.0
    q = identity(nbrch)*-99.0

    return(alphaerr,q)


def CreateTextFiles(nbrch, src_folder, Ass_folder, header, Startdate, Enddate):
    #Creating text files - Assimilation file and runoff files.

    Reach = arange(1,nbrch+1,1)

    (X,K) = GetMuskingumParameters(nbrch,src_folder)
    (drainsTo) = MakedrainsTo(src_folder)

    Runoff = []
    for i in range(1,nbrch+1):
        Runoff.append('runoff' + str(i) +'.txt')

    (LOSS) = EstimateLosses(src_folder,Startdate,Enddate,nbrch)

    (alphaerr,q) = DefaultErrorModel(nbrch)

    with open(Ass_folder + os.sep + 'Assimilationfile.txt', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=' ')
        file_writer.writerow(['Reach'] + ['X'] +  ['K']  + ['DrainsTo'] + ['Runoff'] +['alphaerr'] + ['Loss_fraction'])
        for j in range(0,nbrch):
            file_writer.writerow([str(Reach[j])]+ [str(X[j])]+[str(K[j])[0:10]]+[str(drainsTo[j])]
            +[str(Runoff[j])]+[str(alphaerr[j])] + [str(LOSS[j])])
    with open(Ass_folder + os.sep + 'Assimilationfile_q.txt', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=' ')
        file_writer.writerow(['q'])
        for k in range(0,nbrch):
            file_writer.writerow(q[k])

    (RR) = GetInput(src_folder,nbrch,header,Startdate,Enddate)
    days = int(Enddate - Startdate)+1  #Number of days for which the data should be read.
    startdate = num2date(Startdate)
    dates = [startdate + timedelta(days=i) for i in range(0,days)]

    RR_reach = numpy.zeros([days])
    for j in range(0,nbrch):
        RR_reach = RR[0:days,j]
        f = open(Ass_folder + os.sep + 'runoff' + str(j+1) + ".txt", "w")
        f.write('Dates' + '       ' + 'Runoff [m3/s]'+ '\n')
        for k in range(0,len(RR_reach)):
            f.write(str(dates[k])[0:10]+ ' ' +str(RR_reach[k])+'\n')
        f.close
