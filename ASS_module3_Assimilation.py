"""
***************************************************************************
   ASS_module3_Assimilation.py
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
from ASS_utilities import ReadObsFlowsAss
from ASS_utilities import LoadData
from ASS_utilities import MuskSetupFlows
from SWAT_output_format_specs import SWAT_output_format_specs
OUTSPECS = SWAT_output_format_specs()

def kf_flows(obs_file, Ass_folder, nbrch, Enddate, Startdate, RR_enddate, RR_startdate):
    """Returns deterministic and assimilated discharges"""
#-------------------------------------------------------------------------------

# x deterministic run
# x2 and x3 will be the baseline and assimilation runs and P2 and P3 the
# covariances

#-------------------------------------------------------------------------------
    days = int(Enddate-Startdate)+1

    #Getting the observed data for the assimilation
    if os.path.isfile(obs_file):
        Q_obs = ReadObsFlowsAss(obs_file)
        Q_obs = Q_obs[find(numpy.isnan(Q_obs[:,1])==0),:]
        Q_obs[:,0] = Q_obs[:,0] + OUTSPECS.PYEX_DATE_OFFSET
        if sum(Q_obs[:,0] >= Startdate) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] >= Startdate),:]
        if sum(Q_obs[:,0] <= Enddate-8) > 0:
            Q_obs = Q_obs[find(Q_obs[:,0] <= Enddate),:]

    #Getting input data and parameters
    (X,K,drainsTo,alphaerr,q,RR,nbrch_add, timestep,loss) = LoadData(Ass_folder, nbrch, RR_enddate, RR_startdate)

    # Adjust observed data to overlap with simulation period
    RR_skip = Startdate - RR_startdate
    if RR_skip > 0:
        RR = RR[RR_skip:RR_skip+days,:]

    #Fitting the RR to the timestep
    Inputs = numpy.zeros([days*(1/timestep),nbrch_add])
    for i in range(0,days):
        for k in range (0,int(1/timestep)):
            Inputs[1/timestep*i+k,:] = RR[i]

    simlength = len(Inputs)

    modeltime = numpy.zeros([simlength,1])
    for i in range(0,len(modeltime)):
        modeltime[i] = Startdate+timestep*i

    IniScov = identity(3*nbrch_add)

    (F,G1,G2) = MuskSetupFlows(Ass_folder, nbrch, RR_enddate, RR_startdate)

    Ga = G1
    Gb = G2

    # Base Run
    xtemp = numpy.zeros([nbrch_add])
    x = numpy.zeros([nbrch_add,simlength])
    x[:,0] = xtemp

    for i in range(1,simlength):
        x[:,i] = dot(F,xtemp)+dot(Ga,Inputs[i-1,:].T)+dot(Gb,Inputs[i,:].T)
        xtemp = x[:,i]

    #Prepare matrices and correlation structure

    #Spatial correlation of inflows

    RHO = corrcoef(RR,rowvar=0)

    #Keep correlation only in same reaches
    SP = numpy.zeros([nbrch_add,nbrch_add])

    a = numpy.where(drainsTo==0)
    outlets = a[0]+1
    nb_outlets = len(outlets)

    drainsTo_max = {}
    for j in range(1,nbrch+1):
        drainsTo_max[j]=[]

    drainsTo_add_max = {}
    for j in range(nbrch,nbrch_add+1):
        drainsTo_max[j]=[]

    for k in range(0,nbrch_add):
        p = int(drainsTo[k])
        TempIndex_add = []
        TempIndex = []
        if p>0:
            while p>0:
                    if p<=nbrch:
                        TempIndex.append(p)
                        p = int(drainsTo[p-1])
                    else:
                        TempIndex_add.append(p)
                        p = int(drainsTo[p-1])

            for i in outlets:
                for j in TempIndex:
                    if i==j:
                        drainsTo_max[k+1] = j
                if len(TempIndex_add)>0:
                    for j in TempIndex_add:
                        if i==j:
                            drainsTo_add_max[k+1] = j

    Reaches = {}
    for i in range(0,nb_outlets):
        Reaches[outlets[i]]= []

    for m in range(0,nb_outlets):
        for n in drainsTo_max:
            if drainsTo_max[n]==outlets[m]:
                Reaches[outlets[m]].append(n)
            else:
                pass
        for n in drainsTo_add_max:
            if drainsTo_add_max[n]==outlets[m]:
                Reaches[outlets[m]].append(n)
            else:
                pass

    for i in range(0,nb_outlets):
        for j in range(0,len(Reaches[outlets[i]])):
            for k in range(0,len((Reaches[outlets[i]]))):
                SP[Reaches[outlets[i]][j]-1,Reaches[outlets[i]][k]-1] = 1

    RHO = RHO*SP

    #Define F1: model for both process and AR model
    F1 = numpy.zeros([3*nbrch_add,3*nbrch_add])

    for i in range(0,nbrch_add):
        for j in range(0,nbrch_add):
            F1[i,j] = F[i,j]

    for i in range(nbrch_add,2*nbrch_add):
        F1[i,i] = alphaerr[i-nbrch_add]

    for i in range(2*nbrch_add,3*nbrch_add):
        F1[i,i] = alphaerr[i-2*nbrch_add]

    G1 = numpy.zeros([3*nbrch_add,2*nbrch_add])

    for i in range(0,nbrch_add):
        for j in range(0,nbrch_add):
            G1[i,j] = Ga[i,j]
        for j in range(nbrch_add,2*nbrch_add):
            G1[i,j]= Gb[i,j-nbrch_add]

    Q2 = dot(RHO,(q**2))
    Q = numpy.zeros([3*nbrch_add,3*nbrch_add])

    for t in range(nbrch_add,2*nbrch_add):
        for v in range(nbrch_add,2*nbrch_add):
            Q[t,v] = Q2[t-nbrch_add,v-nbrch_add]

    for t in range(2*nbrch_add,3*nbrch_add):
        for v in range(2*nbrch_add,3*nbrch_add):
            Q[t,v] = Q2[t-2*nbrch_add,v-2*nbrch_add]

    #Run x2 - Run with no assimilation - with state augmentation

    xinit = numpy.zeros(3*nbrch_add)
    P = IniScov
    xtemp = xinit
    P1all = empty([nbrch_add,simlength])
    P1all[:] = NAN
    x2 = numpy.zeros([3*nbrch_add,simlength])

    x2[:,0] = xinit
    for i in range(1,simlength):

        for c in range(0,nbrch_add):
            for j in range(nbrch_add,2*nbrch_add):
                F1[c,j] = Ga[c,j-nbrch_add]*Inputs[i-1,j-nbrch_add]

            for j in range(2*nbrch_add,3*nbrch_add):
                F1[c,j] = Gb[c,j-2*nbrch_add]*Inputs[i,j-2*nbrch_add]

        x2[:,i] = dot(F1,xtemp) + dot(G1,concatenate((Inputs[i-1,:].T,Inputs[i,:].T), axis=0))

        xtemp = x2[:,i]

        P = dot(dot(F1,P),F1.T) + Q

        for b in range(0,nbrch_add):
            P1all[b,i]=sqrt(P[b,b])

    #Assimilation Run
    P = IniScov
    xtemp = xinit
    Innov = empty([simlength])
    Innov[:] = NAN
    PredStd = empty([simlength])
    PredStd[:] = NAN
    Loc = empty([simlength])
    Loc[:] = NAN
    Pall = empty([nbrch_add,simlength])
    Pall[:,:] = NAN
    x3 = numpy.zeros([3*nbrch_add,simlength])
    x4 = numpy.zeros([3*nbrch_add,simlength])
    x_ahead_temp = numpy.zeros([3*nbrch_add,simlength])
    Pall_ahead = Pall
    P_4 = Pall

    for i in range(1,simlength):
        for c in range(0,nbrch_add):
            for j in range(nbrch_add,2*nbrch_add):
                F1[c,j] = Ga[c,j-nbrch_add]*Inputs[i-1,j-nbrch_add]

            for j in range(2*nbrch_add,3*nbrch_add):
                F1[c,j] = Gb[c,j-2*nbrch_add]*Inputs[i,j-2*nbrch_add]

        x3[:,i] = dot(F1,xtemp)+dot(G1,concatenate((Inputs[i-1,:].T,Inputs[i,:].T), axis=0))
        P = dot(dot(F1,P),F1.T) + Q

        if os.path.isfile(obs_file):
            a = numpy.where(Q_obs[:,0]==modeltime[i])        #look for measurement on day i
            a = a[0].T
        else:
            a = numpy.array([])

        if a.size > 0:
            for mn in range(0,len(a)):
                pt = Q_obs[a[mn],3]            #Reach where measurement is taken
                r = Q_obs[a[mn],2]             #Measurement std [m3/s]

                z1 = x3[pt-1,i]                #Modelled flow
                if isnan(Q_obs[a[mn],1])==False:
                #Measurement operator at the state measurement
                    H1 = numpy.zeros([1,nbrch_add*3])
                    H1[0,pt-1] = 1
                    H = H1
                    #Kalman gain
                    R = r**2
                    K = dot(dot(P,H.T),(dot(dot(H,P),H.T)+R)**(-1))
                    Innov[i] = Q_obs[a[mn],1]-z1
                    PredStd[i] = math.sqrt(dot(dot(H,P),H.T)+R)
                    Loc[i] = pt
                    x3[:,i] = x3[:,i]+K.squeeze()*(Q_obs[a[mn],1]-z1)
                    P = P - dot(dot(K,H),P)

        for v in range(0,nbrch_add):
            Pall[v,i] = math.sqrt(P[v,v])

        xtemp = x3[:,i]

    P_2 = P1all
    P_3 = Pall

    (a,index)=numpy.where([numpy.isnan(Innov)==False])

    Innov1 = Innov
    PredStd1 = PredStd

    count = 0
    for i in range(0,len(index)):
        if Innov1[index[i]]>2*PredStd1[index[i]] or Innov1[index[i]]<-2*PredStd1[index[i]]:
            count = count+1

    #Adjust to one flow per day
    q2 = numpy.zeros([3*nbrch_add,days])
    for i in range(0,days):
        q_temp = 0
        for j in range(0,int(1/timestep)):
            q_temp = q_temp + x2[:,i*(1/timestep)+j]
        q2[:,i] = q_temp/(1/timestep)

    q3 = numpy.zeros([3*nbrch_add,days])
    for i in range(0,days):
        q_temp = 0
        for j in range(0,int(1/timestep)):
            q_temp = q_temp + x3[:,i*(1/timestep)+j]
        q3[:,i] = q_temp/(1/timestep)

    P2 = numpy.zeros([nbrch_add,days])
    for i in range(0,days):
        q_temp = 0
        for j in range(0,int(1/timestep)):
            q_temp = q_temp + P_2[:,i*(1/timestep)+j]
        P2[:,i] = q_temp/(1/timestep)

    P3 = numpy.zeros([nbrch_add,days])
    for i in range(0,days):
        q_temp = 0
        for j in range(0,int(1/timestep)):
            q_temp = q_temp + P_3[:,i*(1/timestep)+j]
        P3[:,i] = q_temp/(1/timestep)

    #Creating output files for plotting function
    with open(Ass_folder + os.sep + 'Deterministic_Output.csv', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',')
        for i in range(0,len(q2)):
            file_writer.writerow(q2[i])
    csvfile.close

    with open(Ass_folder + os.sep + 'Deterministic_Cov.csv', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',')
        for i in range(0,len(P2)):
            file_writer.writerow(P2[i])
    csvfile.close

    with open(Ass_folder + os.sep + 'Assimilation_Output.csv', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',')
        for i in range(0,len(q3)):
            file_writer.writerow((q3[i]))
    csvfile.close

    with open(Ass_folder + os.sep + 'Assimilation_Cov.csv', 'wb') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',')
        for i in range(0,len(P3)):
            file_writer.writerow(P3[i])
    csvfile.close


    #Creating output files for users
    out_header = []
    out_header.append('Dates')
    for i in range (0,nbrch):
        out_header.append('Reach '+str(i+1)+' flow')
        out_header.append('Reach '+str(i+1)+' std')

    simdates = arange(Startdate,Enddate+1,1)
    simdates = simdates - OUTSPECS.PYEX_DATE_OFFSET

    output = zeros([days,nbrch*2+1])
    for i in range(0,nbrch):
        output[:,i*2+1] = q3[i,:]
        output[:,i*2+2] = P2[i,:]

    output[:,0] = simdates

    with open(Ass_folder + os.sep + 'Assimilation_Final_Output.csv', 'wb') as csvfile:
        file_writer = csv.writer(csvfile,delimiter=',')
        file_writer.writerow(out_header)
        for i in range(0,len(output)):
            file_writer.writerow(output[i])

    return x,x2,x3,P_2,P_3,Innov,PredStd,Loc

