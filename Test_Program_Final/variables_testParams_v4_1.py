# -*-coding:Latin-1 -*
#######################################################################################
# Taken from variables_testParams_v4_0.py
# 
# A.A   V4.1    21/04/2016  transfert of some parameters to testflow.xls
#
#######################################################################################

from madClassesAndFunctions_v2 import AddressingTrigger
from madClassesAndFunctions_v2 import SingleOperation
from madClassesAndFunctions_v2 import ReadOperation
from madClassesAndFunctions_v2 import Arduino

######################################
# MISC. INFOS

resultsOutput = r'C://Users//cc228997//Desktop//FINAL MAD PROGRAMS//testResults'
X_pos=0
Y_pos=0

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
                       [1e-7,1e-5,1e-7],        # top pulse timing
                       [1e-7,1e-5,1e-7],        # bottom pulse timing
                       [1e-7,1e-5,1e-7])        # gate pulse timing

reset1 = SingleOperation("Reset",               # operation name
                       [0,0,0.0],            # top pulse bias
                       [2.5,2.5,0.],            # bottom pulse bias 2.5
                       [5.0,5.0,0.],            # gate pulse bias
                       [1e-7,10e-6,1e-7],        # top pulse timing
                       [1e-7,10e-6,1e-7],        # bottom pulse timing
                       [1e-7,10e-6,1e-7])        # gate pulse timing

# Dictionnary containing the different objects
dico={'rd1':rd1,'rd10':rd10,'rd100':rd100,'rd1000':rd1000,'rd1m':rd1m,'form1':form1,'formrev':formrev,'set1':set1,'reset1':reset1}

# List os specific patterns running on half of the memory
patterns=['CKBD','ICKBD','RS','IRS','CS','ICS']
# Dictionnary containing the patterns to be executed by ARDUINO 
dico_patterns={'A':'A','S':'S','L':'L','R':'R','CKBD':'C','ICKBD':'D','RS':'E','IRS':'F','CS':'G','ICS':'H'}

# main test plan to be run sequentially on the selected addresses
# (testPlan[0] on selected addresses, then testPlan[1]... etc...)
#testPlan = [formrev,rd100,set1,rd100,reset1,rd100,set1,rd100,reset1,rd100];


#testPlan = [rd10,form1,rd10,reset1,set1,reset1,set1,reset1,rd10,set1,rd10];

#testPlan = [reset1,rd1000,rd100,set1,rd1000,rd100,reset1,set1,reset1,set1,reset1,rd1000,rd100,set1,rd1000,rd100];

#testPlan = [form1];
#testPlan = [rd100,form1,rd100];

#####################################################
#testPlan = [1,rd100,2,[reset1,set1]]
####################################################
#testPlan = [1,rd100]

#testPlan = [set1,rd1000,reset1,rd1000,set1,rd1000,reset1,rd1000];



######################################
# LOW-LEVEL VARIABLES, DO NOT MODIFY

B1530_GPIB = r'GPIB::17::INSTR'         # B1530 GPIB address
prober_GPIB = r'GPIB0::28::INSTR'       # Prober GPIB address
#trig = AddressingTrigger(chTrig, 2e-6, 350e-6)   # trigger configuration
trig = AddressingTrigger(chTrig, 2e-6, 250e-6)   # trigger configuration

