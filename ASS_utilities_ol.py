from matplotlib.pylab import *
import numpy
import os
import read_SWAT_out
from SWAT_output_format_specs import SWAT_output_format_specs
RES_OUTSPECS = SWAT_output_format_specs()

def ReadNoSubs(MOD_DESC):
    if os.path.isfile(MOD_DESC):
        MOD_DESC_file = open(MOD_DESC,'r')
        model_data = MOD_DESC_file.readlines()
        MOD_DESC_file.close
        nbrch=int(model_data[-1][12:])
    else:
        raise GeoAlgorithmExecutionException('File ' + MOD_DESC + ' does not exist')
    return nbrch

def ReadObsFlowsAss(obs_file):
    """Read the observed flows for the assimilation (time, obs, measurement error, reachID)"""
    if os.path.isfile(obs_file):
        filename = (obs_file)
        f = [0,1,2,3]
        Q_obs = numpy.genfromtxt(filename, delimiter=',', usecols=f)
    else:
        raise GeoAlgorithmExecutionException('File ' + obs_file + ' does not exist')
    return(Q_obs)

def LoadData(Ass_folder, nbrch, Enddate, Startdate):
    """Load data from Assimilation file and runoff files"""
    filename = Ass_folder + os.sep + 'Assimilationfile.txt'
    for f in (1,2,3,5,6):
        data = numpy.genfromtxt(filename, delimiter=' ', skip_header=1, usecols=f)
        if f==1:
            X = data
        if f==2:
            K = data
        if f==3:
            drainsTo = data
        if f==5:
            alphaerr = data
        if f==6:
            loss = data

    filename = Ass_folder + os.sep + 'Assimilationfile_q.txt'
    q = numpy.zeros([nbrch,nbrch])
    for i in range(0,nbrch):
        data = numpy.genfromtxt(filename, delimiter=' ', skip_header=1, usecols=i)
        q[:,i] = data

    #Getting the runoff from runoff text files
    days = int(Enddate-Startdate)+1
    RR = numpy.zeros([days,nbrch])

    for i in range(0,nbrch):
        filename = Ass_folder + os.sep + 'runoff'+ str(i+1) + '.txt'
        RR[:,i] = numpy.genfromtxt(filename, delimiter = ' ', skip_header = 1, usecols=1)

    # Check numerical stability
    deltaTmax = 2.0*K*(1.0-X)
    deltaTmin = 2*K*X

    # If all K require timestep larger than 1, the timestep will be set to one and the reaches sub-divided accordingly
    if max(deltaTmin)>1.0:
        timestep = 1.0
    # If a K requires a timestep smaller than 1, the timestep will be decreased and the reaches sub-divided accordingly
    if min(deltaTmax)<1.0:
        timestep = 1.0/numpy.ceil(1.0/min(deltaTmax))
        if timestep<0.1:
            timestep = 0.1
    else:
        timestep = 1.0

    max_K = timestep/(2*X)
    maxK = max(max_K)

    #Checking for large K values
    a = numpy.where(K>maxK)

    #In cases with large differences in the K values, the reaches in question will be subdivided into new reaches
    if len(a[0])>0:
        new_reaches = []
        new_K = []
        K_temp = K
        for i in range(0,len(a[0])):
            if K[a[0][i]]<2*max_K[0]:
                K_temp[a[0][i]] = K[a[0][i]]/2
                for j in range(0,1):
                    new_K.append(K_temp[a[0][i]])
                    new_reaches.append(a[0][i]+1)
            elif K[a[0][i]]<3*max_K[0]:
                K_temp[a[0][i]] = K[a[0][i]]/3
                for j in range(0,2):
                    new_K.append(K_temp[a[0][i]])
                    new_reaches.append(a[0][i]+1)
            elif K[a[0][i]]<4*max_K[0]:
                K_temp[a[0][i]] = K[a[0][i]]/4
                for j in range(0,3):
                    new_K.append(K_temp[a[0][i]])
                    new_reaches.append(a[0][i]+1)
            else:
                K_temp[a[0][i]] = K[a[0][i]]/5
                for j in range(0,4):
                    new_K.append(K_temp[a[0][i]])
                    new_reaches.append(a[0][i]+1)

        add_reaches = numpy.zeros([len(new_reaches)])
        add_reach_nr = numpy.zeros([len(add_reaches)])
        for i in range(0,len(add_reaches)):
            add_reaches[i] = new_reaches[i]
            add_reach_nr[i] = (nbrch+1+i)

        # Enlarging the inputs to fit to the new number of reaches
        K_add = numpy.zeros([nbrch+len(new_reaches)])
        X_add = numpy.zeros([nbrch+len(new_reaches)])
        drainsTo_add = numpy.zeros([nbrch+len(new_reaches)])
        loss_add = numpy.zeros([nbrch+len(new_reaches)])
        RR_add = numpy.zeros([days,nbrch+len(new_reaches)])
        alphaerr_add = numpy.zeros([nbrch+len(new_reaches)])
        q_add = numpy.zeros([nbrch+len(new_reaches),nbrch+len(new_reaches)])


        for i in range(0,nbrch):
            alphaerr_add[i] = alphaerr[i]
            q_add[i,i] = q[i,i]
            K_add[i] = K_temp[i]
            X_add[i] = X[i]
            RR_add[:,i] = RR[:,i]
            drainsTo_add[i] = drainsTo[i]
            loss_add[i] = loss[i]

        for i in range (0,len(new_reaches)):
            alphaerr_add[i+nbrch] = alphaerr[add_reaches[i]-1]
            X_add[i+nbrch] = X[add_reaches[i]-1]
            q_add[i+nbrch,i+nbrch] = q[add_reaches[i]-1,add_reaches[i]-1]

        for j in range(0,len(new_K)):
            K_add[nbrch+j] = new_K[j]

        #Creating the new drains to array (drainsTo_add) and splitting the runoff input and losses among the new subreaches
        for i in range(1,nbrch+1):
            fr = where(add_reaches==i)
            if len(fr[0])>0:
                #Divide the losses and runoff to fit the new reahces
                loss_add[i-1] = loss[i-1]/(len(fr[0])+1)
                RR_add[:,i-1] = RR[:,i-1]/(len(fr[0])+1)
                for k in range(0,len(fr[0])):
                    loss_add[add_reach_nr[fr[0][k]]-1] = loss_add[i-1]
                    RR_add[:,add_reach_nr[fr[0][k]]-1] = RR_add[:,i-1]
                #Find  reaches that drain to reach
                fdt = where(drainsTo==i)
                if len(fdt[0])==0:
                    drainsTo_add[add_reach_nr[fr[0][0]]-1] = i
                    if len(fr[0])>1:
                        for k in range(0,len(fr[0])-1):
                            drainsTo_add[add_reach_nr[fr[0][k]]-1] = add_reach_nr[fr[0][k+1]]
                        drainsTo_add[add_reach_nr[fr[0][k+1]]-1] = i
                    else:
                        drainsTo_add[add_reach_nr[fr[0][0]]-1] = i
                else:
                    drainsTo_add[fdt[0]] = add_reach_nr[fr[0][0]]
                    #The rainfall runoff input will now enter at the most upstream sub-reach of the old reach
                    if len(fr[0])>1:
                        for k in range(0,len(fr[0])-1):
                            drainsTo_add[add_reach_nr[fr[0][k]]-1] = add_reach_nr[fr[0][k+1]]
                        drainsTo_add[add_reach_nr[fr[0][k+1]]-1] = i
                    else:
                        drainsTo_add[add_reach_nr[fr[0][0]]-1] = i

            #Implementing the new reaches
            K = K_add
            X = X_add
            drainsTo = drainsTo_add
            RR = RR_add
            alphaerr = alphaerr_add
            q = q_add
            nbrch_add = len(K)
            loss = loss_add
    else:
        nbrch_add = nbrch

    return X,K,drainsTo,alphaerr,q,RR,nbrch_add,timestep,loss

def EstimateLosses(src_folder,Startdate,Enddate,nbrch):
    LOSS = numpy.zeros([nbrch])

    return LOSS

def MuskSetupFlows(Ass_folder, nbrch, Enddate, Startdate):
    """Set up of the Muskingum propagation"""
#-------------------------------------------------------------------------------
# set up of the Muskingum propagation for a Kalman Filtering application
# X(k+1)=F*X(k)+G1*M(k)+G2*M(k+1)
#-------------------------------------------------------------------------------

    (X,K,drainsTo, alphaerr,q,RR,nbrch_add, timestep, loss) = LoadData(Ass_folder, nbrch, Enddate, Startdate)

    F=numpy.zeros(shape=(nbrch_add,nbrch_add))
    G1=numpy.zeros(shape=(nbrch_add,nbrch_add))
    G2=numpy.zeros(shape=(nbrch_add,nbrch_add))
    C1=numpy.zeros(shape=(nbrch_add,1))
    C2=numpy.zeros(shape=(nbrch_add,1))
    C3=numpy.zeros(shape=(nbrch_add,1))

    deltaT = timestep #time step (same unit as K)

    for i in range(0,nbrch_add):
        C1[i] = (deltaT-2*K[i]*X[i])/(2*K[i]*(1-X[i])+deltaT)
        C2[i] = (deltaT+2*K[i]*X[i])/(2*K[i]*(1-X[i])+deltaT)
        C3[i] = (2*K[i]*(1-X[i])-deltaT)/(2*K[i]*(1-X[i])+deltaT)

    for i in range(0,nbrch_add):
        F[i,i] = C3[i]
        G1[i,i] = C1[i]
        G2[i,i] = C2[i]

    for j in range(0,nbrch_add):
        p = int(drainsTo[j])
        TempIndex = []                           #TempIndex will be a list of all reaches getting input from reach no j
        if p>0:
            while p>0:
                TempIndex.append(p)
                p = int(drainsTo[p-1])

            for k in range(0,len(TempIndex)):
                i = TempIndex[k]
                PC = (C1[TempIndex[0]-1]*C3[j]+C2[TempIndex[0]-1])*(1-loss[j])
                for q in range (0,k):
                    PC = PC*(1-loss[TempIndex[q]-1])
                if k>0:
                    for r in range(0,k):
                        PC = PC*C1[TempIndex[r+1]-1]

                F[i-1,j] = PC

                PC2 = 1
                PC2 = PC2*C1[TempIndex[0]-1]*(1-loss[j])
                if k>0:
                    for r in range(0,k):
                        PC2 = PC2*C1[TempIndex[r+1]-1]*(1-loss[TempIndex[r]-1])

                G1[i-1,j] = PC2*C2[j]
                G2[i-1,j] = PC2*C1[j]

    return F,G1,G2
