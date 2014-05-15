from SWAT_parameter_specs import SWAT_parameter_specs

parspecs = SWAT_parameter_specs()

class SWAT_PEST_specs():

    def __init__(self):
        # Modify this class to change settings for SWAT-PEST interaction

        # Folder where PEST executables are stored. Adjust depending on installation
        self.PESTexeFolder = 'c:\\Program Files(x86)\\MapWindow\\Plugins\\MWSWAT2009\\PEST' ##'c:\\Program Files (x86)\\PEST_13'

        # Parameter identifier used in PEST template files
        self.ptf = '$'

        # Observation identifies used in PEST instruction files
        self.pif = '$'

        # Location of simulated discharge in reach output file
        self.flowoutinicol = 50

        self.flowoutendcol = 61

        # PEST control file defaults

        self.CFfirstline = 'pcf'

        self.RSTFLE = 'restart'

        self.PESTMODE = 'estimation'

        self.NPARGP = len(parspecs.PARAMETERS)

        self.NPRIOR = 0

        self.NOBSGP = 1

        self.PRECIS = 'single'

        self.DPOINT = 'point'

        self.NUMCOM = 1

        self.JACFILE = 0

        self.MESSFILE = 0

        self.RLAMBDA1 = 10.0

        self.RLAMFAC = 2.0

        self.PHIRATSUF= 0.3

        self.PHIREDLAM = 0.01

        self.NUMLAM = 10

        self.RELPARMAX = 5.0

        self.FACPARMAX = 5.0

        self.FACORIG = 0.001

        self.PHIREDSWH = 0.1

        self.NOPTMAX = 30

        self.PHIREDSTP = 0.005

        self.NPHISTP = 4

        self.NPHINORED = 4

        self.RELPARSTP = 0.01

        self.NRELPAR = 4

        self.ICOV = 1

        self.ICOR = 1

        self.IEIG = 1