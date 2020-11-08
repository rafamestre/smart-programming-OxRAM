# -*-coding:Latin-1 -*
##################################################################################################################
#   A.A     V4.2    18/04/2016      Add of WL_refresh parameter
#                                           on -> WL refresh is done before each operation
#                                           off -> WL refresh is done only before the whole testflow
#   A.A     V4.3    20/04/2016      Add of SmartForm parameter
#                                           on -> a smartforming is done before the xls testflow
#                                           off -> no initialization is done before the xls testflow
#
##################################################################################################################
from madClassesAndFunctions_v3 import AddressingTrigger
from madClassesAndFunctions_v3 import SingleOperation
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import Arduino

######################################
# MISC. INFOS

testflow= 'Endurance_flow.xls'
X_pos = 0
Y_pos = 0

resultsOutput = r'C://Users//cc228997//Desktop//FINAL MAD PROGRAMS//testResults'

######################################
# GLOBAL PARAMETERS

proberActiv = False          	# Prober connected or not
#set the channels
chGate = 202
chTop = 101
chBot = 102
chTrig = 202
chVdd = 201

######################################
# DEFINE DEVICE OPERATIONS

rd1 = ReadOperation("Read",     # operation name
                    "1uA",      # current range on bottom electrode 
                    "5V",       # voltage meas. range on top/gate electrodes
                    0.1,        # top read voltage  
                    0.0,        # bottom read voltage
                    5.0,        # gate read voltage
                    40e-6)      # read duration (averaging time)

rd10 = ReadOperation("Read",     # operation name
                    "10uA",      # current range on bottom electrode 
                    "5V",       # voltage meas. range on top/gate electrodes
                    0.1,        # top read voltage  0.1
                    0.0,        # bottom read voltage
                    5.0,        # gate read voltage
                    20e-6)      # read duration (averaging time)

rd100 = ReadOperation("Read",     # operation name
                    "100uA",      # current range on bottom electrode 
                    "5V",       # voltage meas. range on top/gate electrodes
                    0.1,        # top read voltage  0.2
                    0.0,        # bottom read voltage
                    5.0,        # gate read voltage
                    20e-6)      # read duration (averaging time) 10

rd1000 = ReadOperation("Read",     # operation name
                    "10mA",      # current range on bottom electrode 
                    "5V",       # voltage meas. range on top/gate electrodes
                    0.1,        # top read voltage  
                    0.0,        # bottom read voltage
                    5.0,        # gate read voltage
                    40e-6)      # read duration (averaging time)

rd1m = ReadOperation("Read",     # operation name
                    "1mA",      # current range on bottom electrode 
                    "5V",       # voltage meas. range on top/gate electrodes
                    0.1,        # top read voltage  
                    0.0,        # bottom read voltage
                    5.0,        # gate read voltage
                    40e-6)      # read duration (averaging time)


form1 = SingleOperation("Forming",              # operation name
                       [4.0,4.0,0.],            # top pulse bias
                       [0.0,0.0,0.],            # bottom pulse bias
                       [2,2,0.0],            # gate pulse bias
                       [1e-7,1e-5,1e-7],        # top pulse timing 1e-5
                       [1e-7,1e-5,1e-7],        # bottom pulse timing 1e-5
                       [1e-7,1e-5,1e-7])        # gate pulse timing 1e-5

formrev = SingleOperation("Forming",              # operation name
                       [4.0,4.0,0.0],            # top pulse bias
                       [0.0,0.0,0.0],            # bottom pulse bias
                       [2.0,2.0,0.0],           # gate pulse bias
                       [1e-7,1e-5,1e-7],        # top pulse timing
                       [1e-7,1e-5,1e-7],        # bottom pulse timing
                       [1e-7,1e-5,1e-7])        # gate pulse timing

set1 = SingleOperation("Set",                   # operation name
                       [2.0,2.0,0.],            # top pulse bias 2.0
                       [0.0,0.0,0.],            # bottom pulse bias
                       [2.0,2.0,0.],            # gate pulse bias 2.0
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

reset1 = SingleOperation("Reset",               # operation name
                       [0,0,0.0],            # top pulse bias
                       [2.5,2.5,0.],            # bottom pulse bias 2.5
                       [5.0,5.0,0.],            # gate pulse bias
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

# Dictionnary containing the different objects
dico={'rd1':rd1,'rd10':rd10,'rd100':rd100,'rd1000':rd1000,'rd1m':rd1m,'form1':form1,'formrev':formrev,'set1':set1,'reset1':reset1}

# List os specific patterns running on half of the memory
patterns=['CKBD','ICKBD','RS','IRS','CS','ICS']
# Dictionnary containing the patterns to be executed by ARDUINO 
dico_patterns={'A':'A','S':'S','L':'L','R':'R','CKBD':'C','ICKBD':'D','RS':'E','IRS':'F','CS':'G','ICS':'H'}

######################################
# LOW-LEVEL VARIABLES, DO NOT MODIFY

B1530_GPIB = r'GPIB::17::INSTR'         # B1530 GPIB address
prober_GPIB = r'GPIB0::28::INSTR'       # Prober GPIB address
#trig = AddressingTrigger(chTrig, 2e-6, 350e-6)   # trigger configuration

