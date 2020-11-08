    # -*-coding:Latin-1 -*

from madClassesAndFunctions_v3 import AddressingTrigger
from madClassesAndFunctions_v3 import SingleOperation
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import Arduino

######################################
# MISC. INFOS

testName = 'Test4kbit'		# Test name
waferLot = 'D15S1058'		# Lot
waferNo = '23'			# Wafer number
dutName = 'A_D18'		# DUT
resultsOutput = r'C://Users//cc228997//Desktop//FINAL MAD PROGRAMS//testResults'

######################################
# GLOBAL PARAMETERS

proberActiv = False          	# Prober connected or not
mtxSize = '4K'                	# Matrix Size: '256', '4K', '64K', '1M' 
#set the channels
chGate = 202
chTop = 101
chBot = 102
chTrig = 202
chVdd = 201
Vddvalue=5.6

######################################
# ADDRESSING PARAMETERS

adrsMode = 'S'   		# addressing mode: single address 'A' or scan 'S'
scanMode = 'All' 		# scanning mode: 'All', 'Range', 'CKBD' or 'ICKBC'

# If mode "S" together with "Range"
startBL = 0       		# scan range mode: BL start address
startWL = 14    		        # scan range mode: WL start address
startSL = 0     		# scan range mode: SL start address
stopBL = 255       	        # scan range mode: BL stop address
stopWL = 14      		# scan range mode: WL stop address
stopSL = 0      		# scan range mode: SL stop address

# If mode "L" (list of single addresses SL;WL;BL written in *.csv file with max=1365 addresses)
addressList = r'C:\Users\cc228997\Desktop\FINAL MAD PROGRAMS\Rafa//address_list.txt'

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
                       [3.5,3.5,0.0],            # top pulse bias
                       [0.0,0.0,0.0],            # bottom pulse bias
                       [1.2,1.2,0.0],            # gate pulse bias
                       [1e-7,1e-5,1e-7],        # top pulse timing 1e-5
                       [1e-7,1e-5,1e-7],        # bottom pulse timing 1e-5
                       [1e-7,1e-5,1e-7])        # gate pulse timing 1e-5

formrev = SingleOperation("Forming",              # operation name
                       [0.0,0.0,0.0],            # top pulse bias
                       [4.0,4.0,0.0],            # bottom pulse bias
                       [2.0,2.0,0.0],           # gate pulse bias
                       [1e-7,1e-5,1e-7],        # top pulse timing
                       [1e-7,1e-5,1e-7],        # bottom pulse timing
                       [1e-7,1e-5,1e-7])        # gate pulse timing

set1 = SingleOperation("Set",                   # operation name
                       [2.5,2.5,0.],            # top pulse bias 2.0
                       [0.0,0.0,0.],            # bottom pulse bias
                       [1.2,1.2,0.],            # gate pulse bias
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

reset1 = SingleOperation("Reset",               # operation name
                       [0,0,0.0],            # top pulse bias
                       [3.0,3.0,0.0],            # bottom pulse bias 2.5
                       [4.8,4.8,0.],            # gate pulse bias
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

setSmart = SingleOperation("Set",               # operation name
                       [2.5,2.5,0.],            # top pulse bias 
                       [0.0,0.0,0.],            # bottom pulse bias
                       [1.2,1.2,0.0],               # gate pulse bias
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

resetSmart = SingleOperation("Reset",           # operation name
                       [0,0,0.0],               # top pulse bias
                       [3.0,3.0,0.0],           # bottom pulse bias 2.5
                       [4.8,4.8,0.],            # gate pulse bias
                       [1e-7,1e-6,1e-7],        # top pulse timing
                       [1e-7,1e-6,1e-7],        # bottom pulse timing
                       [1e-7,1e-6,1e-7])        # gate pulse timing

#Thresholds

Ron = 10000
Roff = 40000
Rform = 100000

# Dictionnary containing the different objects
dico={'rd1':rd1,'rd10':rd10,'rd100':rd100,'rd1000':rd1000,'rd1m':rd1m,'form':form1,'formrev':formrev,'set':set1,'reset':reset1}

# List os specific patterns running on half of the memory
patterns=['CKBD','ICKBD','RS','IRS','CS','ICS']
# Dictionnary containing the patterns to be executed by ARDUINO 
dico_patterns={'A':'A','S':'S','L':'L','R':'R','CKBD':'C','ICKBD':'D','RS':'E','IRS':'F','CS':'G','ICS':'H'}


# main test plan to be run sequentially on the selected addresses
# (testPlan[0] on selected addresses, then testPlan[1]... etc...)
#testPlan = [formrev,rd100,set1,rd100,reset1,rd100,set1,rd100,reset1,rd100];



#testPlan = [rd10,form1,rd10,reset1,set1,reset1,set1,reset1,rd10,set1,rd10];

#testPlan = [reset1,rd1000,rd100,set1,rd1000rd100,reset1,set1,reset1,set1,reset1,rd1000,rd100,set1,rd1000,rd100];

#testPlan = [form1];
#testPlan = [rd100,form1,rd100,rd1m];

#####################################################
#testPlan = [1,rd100,2,[reset1,set1]]
####################################################
testPlan = [reset1,rd100,set1,rd100,set1,rd100]

#testPlan = [set1,rd1000,reset1,rd1000,set1,rd1000,reset1,rd1000];
#rd1, form1, rd1];
#, reset1, rd1, set1, rd1, reset1, rd1


######################################
# LOW-LEVEL VARIABLES, DO NOT MODIFY

B1530_GPIB = r'GPIB::17::INSTR'         # B1530 GPIB address
prober_GPIB = r'GPIB0::28::INSTR'       # Prober GPIB address
#trig = AddressingTrigger(chTrig, 2e-6, 350e-6)   # trigger configuration
trig = AddressingTrigger(chTrig, 2e-6, 250e-6)   # trigger configuration

