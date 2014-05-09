"""Class for interaction with model file"""
import os
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from numpy import size

class ParVarFile(GeoAlgorithmExecutionException):

    def __init__(self, parvar_file,NPAR):
        if os.path.isfile(parvar_file):
            # Model folder
            self.Path = os.path.split(parvar_file)[0]
            # Model file
            self.ParVarFile = parvar_file

            # Reading model file
            self.desc = {}
            # Getting variables from model file
            f=open(parvar_file,'r').readlines()
            if f[0].split() == NPAR:
                pass
            else:
                if size(f[1:]) < NPAR+1:
                    raise GeoAlgorithmExecutionException('Too few parameter sets in the parameter variation file: \"' + parvar_file + '\" ')
                elif size(f[1:]) > NPAR+1:
                    raise GeoAlgorithmExecutionException('Too many parameter sets in the parameter variation file: \"' + parvar_file + '\" ')
        else:
            raise GeoAlgorithmExecutionException('No such file: \"' + parvar_file + '\" ')
