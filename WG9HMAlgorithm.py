import os
from PyQt4.QtGui import *
from processing.script.ScriptAlgorithm import ScriptAlgorithm
from processing.core.WrongHelpFileException import WrongHelpFileException

class WG9HMAlgorithm(ScriptAlgorithm):

    def helpFile(self):
        [folder, filename] = os.path.split(self.descriptionFile)
        [filename, _] = os.path.splitext(filename)
        folder = os.path.dirname(folder)
        helpfile = str(folder) + os.sep + "doc" + os.sep + filename + ".html"
        if os.path.exists(helpfile):
            return helpfile
        else:
            raise WrongHelpFileException("Sorry, no help is available for this algorithm.")
    
    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + "/images/tigerNET.png")
    
    def getCopy(self):
        newone = WG9HMAlgorithm(self.descriptionFile)
        newone.provider = self.provider
        return newone
    
