from qgis.core import *
import os, sys
import inspect
from processing.core.Processing import Processing
from processing_SWAT.WG9HMAlgorithmProvider import WG9HMAlgorithmProvider


cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class ProcessingWG9HMPlugin:

    def __init__(self):
        self.provider = WG9HMAlgorithmProvider()
    def initGui(self):
        Processing.addProvider(self.provider, True)

    def unload(self):
        Processing.removeProvider(self.provider)
