from SWAT_parameter_specs import SWAT_parameter_specs

parspecs = SWAT_parameter_specs()

class SWAT_SENSAN_specs():

    def __init__(self):
        # Modify this class to change settings for SWAT-PEST interaction

        # Folder where PEST executables are stored. Adjust depending on installation
        self.PESTexeFolder = 'c:\\Program Files (x86)\\PEST'

        # SENSAN control file defaults

        self.CFfirstline = 'scf'

        self.SCREENDISP = 'verbose'

        self.NPARGP = len(parspecs.PARAMETERS)

        self.PRECIS = 'single'

        self.DPOINT = 'point'

        self.VARFLE = 'parvar.dat'

        self.ABSFLE = 'out1.dat'

        self.RELFLE = 'out2.dat'

        self.SENSFLE = 'out3.dat'

        self.RESULT_TYPES = ['RELFLE - relative differences between observation values']

