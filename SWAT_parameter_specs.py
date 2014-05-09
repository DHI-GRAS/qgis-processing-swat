class SWAT_parameter_specs():

    def __init__(self):
        # Modify this class if format of SWAT input files changes or additional calibration parameters are requested
        self.PARAMETERS = ['ALPHA_BF','ALPHA_BNK','CANMX','CH_K(1)','CH_K(2)','CH_L(1)','CH_L(2)','CH_N(1)','CH_N(2)','CH_S(1)','CH_S(2)','CH_W(1)','CH_W(2)','CN2','CNCOEF','EPCO','EPCO_B','ESCO','ESCO_B','EVRCH','GW_DELAY','GW_REVAP','GWQMN','MSK_CO1','MSK_CO2','MSK_X','OV_N','RCHRG_DP','REVAPMN','RFINC(1)','RFINC(10)','RFINC(11)','RFINC(12)','RFINC(2)','RFINC(3)','RFINC(4)','RFINC(5)','RFINC(6)','RFINC(7)','RFINC(8)','RFINC(9)','SOL_AWC(1)','SOL_AWC(2)','SOL_AWC(3)','SOL_K(1)','SOL_K(2)','SOL_K(3)','SOL_Z(1)','SOL_Z(2)','SOL_Z(3)','SURLAG','TMPINC(1)','TMPINC(10)','TMPINC(11)','TMPINC(12)','TMPINC(2)','TMPINC(3)','TMPINC(4)','TMPINC(5)','TMPINC(6)','TMPINC(7)','TMPINC(8)','TMPINC(9)','TRNSRCH']

        self.PARLEVELS = ['hru','sub','hru','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','hru','bsn','hru','bsn','hru','bsn','bsn','hru','hru','hru','bsn','bsn','bsn','hru','hru','hru','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','hru','hru','hru','hru','hru','hru','hru','hru','hru','bsn','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','bsn']

        self.PARFILES = ['gw','rte','hru','sub','rte','sub','rte','sub','rte','sub','rte','sub','rte','mgt','bsn','hru','bsn','hru','bsn','bsn','gw','gw','gw','bsn','bsn','bsn','hru','gw','gw','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sol','sol','sol','sol','sol','sol','sol','sol','sol','bsn','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','sub','bsn']

        self.PARLINES = [5,11,9,28,7,25,5,29,6,26,4,27,2,11,69,11,14,10,13,66,4,7,6,59,60,61,5,9,8,37,39,39,39,37,37,37,37,37,39,39,39,10,10,10,11,11,11,8,8,8,20,41,43,43,43,41,41,41,41,41,43,43,43,65]

        self.PARSTARTCOL = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,25,33,41,9,17,25,33,41,1,9,17,28,40,52,28,40,52,28,40,52,1,1,25,33,41,9,17,25,33,41,1,9,17,1]

        self.PARENDCOL = [16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,8,32,40,48,16,24,32,40,48,8,16,24,39,51,63,39,51,63,39,51,63,16,8,32,40,48,16,24,32,40,48,8,16,24,16]



        # PEST parameter defaults
        self.PARTRANS = ['none','none','none','log','log','none','none','none','none','none','none','none','none','none','log','none','none','none','none','none','none','log','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','log','log','log','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none','none']

        self.PARCHGLIM = ['factor','factor','relative','factor','factor','factor','factor','relative','relative','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','relative','factor','factor','factor','factor','factor','relative','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor','factor']

        self.SCALE = ['1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0','1.0']

        self.OFFSET = ['0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0','0.0']

        self.DERCOM = ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']

        self.INCTYP = ['relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative','relative']

        self.DERINC = [0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01]

        self.DERINCLB = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

        self.FORCEN = ['switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch','switch']

        self.DERINCMUL = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,]

        self.DERMTHD = ['parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic','parabolic']

