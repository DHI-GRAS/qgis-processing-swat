from SWAT_parameter_specs import SWAT_parameter_specs
from SWAT_PEST_specs import SWAT_PEST_specs
from SWAT_output_format_specs import SWAT_output_format_specs
import numpy
import os
import datetime
from dateutil.relativedelta import *
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from read_SWAT_out import read_SWAT_time
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

def create_PEST_template(src_folder, SWATparameter, parameter_name, subid, hruid, PARVAL1, PARLBND, PARUBND):
    if (SWATparameter[0:5]=='RFINC') | (SWATparameter[0:6]=='TMPINC'):
        if len(parameter_name)>6:
            raise GeoAlgorithmExecutionException('Parameter name for '+SWATparameter+' should have maximum 6 characters.')
    if len(parameter_name)>12:
        raise GeoAlgorithmExecutionException('Parameter name for '+SWATparameter+' should have maximum 12 characters.')

    specs = SWAT_parameter_specs()
    pestspecs = SWAT_PEST_specs()
    pars = numpy.array(specs.PARAMETERS)
    index = int(numpy.where(pars == SWATparameter)[0])
    if specs.PARLEVELS[index] == 'bsn':
        SWAT_filename = 'basins.bsn'
        TEMPLATE_filename = 'basins_bsn.tpl'
    elif specs.PARLEVELS[index] == 'sub':
        SWAT_filename = "%05d" % subid + '0000.' + specs.PARFILES[index]
        TEMPLATE_filename = "%05d" % subid + '0000_' + specs.PARFILES[index] + '.tpl'
    elif specs.PARLEVELS[index] =='hru':
        SWAT_filename = "%05d" % subid + "%04d" % hruid + '.' + specs.PARFILES[index]
        TEMPLATE_filename = "%05d" % subid + "%04d" % hruid + '_' + specs.PARFILES[index] + '.tpl'

    SWAT_filename = src_folder + os.sep + SWAT_filename
    TEMPLATE_filename = src_folder + os.sep + TEMPLATE_filename
    if os.path.isfile(SWAT_filename):
        if os.path.isfile(TEMPLATE_filename):
            lines = open(TEMPLATE_filename,'r').readlines()
            changeline = lines[specs.PARLINES[index]]
            if (SWATparameter[0:5]=='RFINC') | (SWATparameter[0:6]=='TMPINC') | (SWATparameter[0:5]=='SOL_Z') | (SWATparameter[0:7]=='SOL_AWC') | (SWATparameter[0:5]=='SOL_K'):
                lines[specs.PARLINES[index]] = changeline[:specs.PARSTARTCOL[index]-1] + pestspecs.ptf + parameter_name.rjust(specs.PARENDCOL[index]-specs.PARSTARTCOL[index]-1) + pestspecs.ptf + changeline[specs.PARENDCOL[index]:len(changeline)]
            else:
                lines[specs.PARLINES[index]] = pestspecs.ptf + parameter_name.rjust(specs.PARENDCOL[index]-specs.PARSTARTCOL[index]) + pestspecs.ptf + changeline[specs.PARENDCOL[index]+1:len(changeline)]
            ntfile = open(TEMPLATE_filename,'w')
            ntfile.writelines(lines)
            ntfile.close()
        else:
            line1 = 'ptf ' + pestspecs.ptf + '\r\n'
            lines = open(SWAT_filename).readlines()
            changeline = lines[specs.PARLINES[index]-1]
            if (SWATparameter[0:5]=='RFINC') | (SWATparameter[0:6]=='TMPINC') | (SWATparameter[0:5]=='SOL_Z') | (SWATparameter[0:7]=='SOL_AWC') | (SWATparameter[0:5]=='SOL_K'):
                lines[specs.PARLINES[index]-1] = changeline[:specs.PARSTARTCOL[index]-1] + pestspecs.ptf + parameter_name.rjust(specs.PARENDCOL[index]-specs.PARSTARTCOL[index]-1) + pestspecs.ptf + changeline[specs.PARENDCOL[index]:len(changeline)]
            else:
                lines[specs.PARLINES[index]-1] = pestspecs.ptf + parameter_name.rjust(specs.PARENDCOL[index]-specs.PARSTARTCOL[index]) + pestspecs.ptf + changeline[specs.PARENDCOL[index]+1:len(changeline)]
            ntfile = open(TEMPLATE_filename,'w')
            ntfile.writelines(line1)
            ntfile.writelines(lines)
            ntfile.close()
        parblockname = src_folder + os.sep + parameter_name + '.pbf'
        parblockfile = open(parblockname,'w')
        parblockfile.writelines(parameter_name.ljust(13) + specs.PARTRANS[index].ljust(6) + specs.PARCHGLIM[index].ljust(9) + str(PARVAL1).ljust(9)  + str(PARLBND).ljust(9) + str(PARUBND).ljust(9) + SWATparameter.ljust(13) + specs.SCALE[index].ljust(5) + specs.OFFSET[index].ljust(5) + specs.DERCOM[index])
        parblockfile.close()
    else:
        raise GeoAlgorithmExecutionException('SWAT input file ' + SWAT_filename + ' not found in source directory')
    return TEMPLATE_filename, SWAT_filename

##def create_PEST_instruction(src_folder, obsfile, obsgroup, reachid, nreaches, tmpres):
def create_PEST_instruction(src_folder, obsfile, obsgroup, nreaches, tmpres):
    specs = SWAT_output_format_specs()
    pestspecs = SWAT_PEST_specs()
    obsdata =  numpy.genfromtxt(obsfile, delimiter = ',', skiprows=0, missing_values = 'NaN')
    obsdata[:,0] = obsdata[:,0] + specs.PYEX_DATE_OFFSET
    SWAT_time_info = read_SWAT_time(src_folder)
    startyr = datetime.date(int(SWAT_time_info[1]),1,1)
    startdate = startyr + datetime.timedelta(days=int(SWAT_time_info[2])-1)
    if SWAT_time_info[4] > 0:
        startdate = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[4]),1,1)
    endyear = datetime.date(int(SWAT_time_info[1]+SWAT_time_info[0]-1),1,1)
    enddate = endyear + datetime.timedelta(days=int(SWAT_time_info[3])-1)
    insname = obsfile.split('.')[0] + '_' + obsfile.split('.')[1] + '.ins'
    insfile = open(insname,'w')
    insfile.writelines('pif ' + pestspecs.pif + '\n')
    insfile.writelines('l9\n')
    obsblockname = obsfile.split('.')[0] + '_' + obsfile.split('.')[1] + '_observation_block.obf'
    obsblockfile = open(obsblockname,'w')
    obsid = 1
    if tmpres == 0:
        tsteps = int((enddate-startdate).days) + 1
        for i in range(0,tsteps):
            currentdate = startdate + datetime.timedelta(i)
            currentdatenum = matplotlib.dates.date2num(currentdate)
            obs = obsdata[obsdata[:,0]==currentdatenum,1]
            obsw = obsdata[obsdata[:,0]==currentdatenum,2]
            obsw = 1./numpy.power(obsw,2)
            try:
                reachid = int(obsdata[obsdata[:,0]==currentdatenum,3][0])
            except:
                pass
            if ~numpy.isnan(obs):
                obsblockfile.writelines('reach_' + str(reachid) + '_' + str(obsid) + ' ' + str(obs[0]) + ' ' + str(obsw[0]) + ' ' + obsgroup + '\n')
                insfile.writelines('l' + str(reachid) + ' [' + 'reach_' + str(reachid) + '_' + str(obsid) + ']' + str(pestspecs.flowoutinicol) + ':' + str(pestspecs.flowoutendcol) + '\n')
                if reachid < nreaches:
                    insfile.writelines('l' + str(nreaches-reachid) + '\n')
                obsid = obsid + 1
            else:
                insfile.writelines('l' + str(nreaches) + '\n')
    elif tmpres == 1:
        tsteps = int((enddate-startdate).days) + 1
        currentyear = startdate
        while (currentyear <= endyear):
            if currentyear == endyear:
                for m in range(0,enddate.month):
                    currentdate = currentyear + relativedelta(months=+m)
                    currentdatenum = matplotlib.dates.date2num(currentdate)
                    obs = obsdata[obsdata[:,0]==currentdatenum,1]
                    obsw = obsdata[obsdata[:,0]==currentdatenum,2]
                    obsw = 1./numpy.power(obsw,2)
                    try:
                        reachid = int(obsdata[obsdata[:,0]==currentdatenum,3][0])
                    except:
                        pass
                    if ~numpy.isnan(obs):
                        obsblockfile.writelines('reach_' + str(reachid) + '_' + str(obsid) + ' ' + str(obs[0]) + ' ' + str(obsw[0]) + ' ' + obsgroup + '\n')
                        insfile.writelines('l' + str(reachid) + ' [' + 'reach_' + str(reachid) + '_' + str(obsid) + ']' + str(50) + ':' + str(61) + '\n')
                        if reachid < nreaches:
                            insfile.writelines('l' + str(nreaches-reachid) + '\n')
                        obsid = obsid + 1
                    else:
                        insfile.writelines('l' + str(nreaches) + '\n')
                insfile.writelines('l' + str(nreaches) + '\n')
                currentyear = currentyear + relativedelta(years=+1)
            else:
                for m in range(0,12):
                    currentdate = currentyear + relativedelta(months=+m)
                    currentdatenum = matplotlib.dates.date2num(currentdate)
                    obs = obsdata[obsdata[:,0]==currentdatenum,1]
                    obsw = obsdata[obsdata[:,0]==currentdatenum,2]
                    obsw = 1./numpy.power(obsw,2)
                    try:
                        reachid = int(obsdata[obsdata[:,0]==currentdatenum,3][0])
                    except:
                        pass
                    if ~numpy.isnan(obs):
                        obsblockfile.writelines('reach_' + str(reachid) + '_' + str(obsid) + ' ' + str(obs[0]) + ' ' + str(obsw[0]) + ' ' + obsgroup + '\n')
                        insfile.writelines('l' + str(reachid) + ' [' + 'reach_' + str(reachid) + '_' + str(obsid) + ']' + str(50) + ':' + str(61) + '\n')
                        if reachid < nreaches:
                            insfile.writelines('l' + str(nreaches-reachid) + '\n')
                        obsid = obsid + 1
                    else:
                        insfile.writelines('l' + str(nreaches) + '\n')
                insfile.writelines('l' + str(nreaches) + '\n')
                currentyear = currentyear + relativedelta(years=+1)

    return insname, obsblockname
