"""Class for interaction with model file"""
import os
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

class ModelFile(GeoAlgorithmExecutionException):

    def __init__(self, model_file):
        if os.path.isfile(model_file):
            # Model folder
            self.Path = os.path.split(model_file)[0]
            # Model file
            self.ModelFile = model_file

            # Reading model file
            self.desc = {}
            # Getting variables from model file
            f=open(model_file,'r').readlines()
            if not f[0].find('Model description file') == -1:
                for line in range(1,len(f)):
                    try:
                        (key, val) = f[line].split()
                        self.desc[key] = val
                    except:
                        pass
            else:
                raise GeoAlgorithmExecutionException('Not a model descibtion file: \"' + model_file + '\" ')
        else:
            raise GeoAlgorithmExecutionException('No such file: \"' + model_file + '\" ')
