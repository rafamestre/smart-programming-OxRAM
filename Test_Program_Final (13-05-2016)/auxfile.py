#import variables_testParams_v3 as var
import numpy as np
import math
import variables_testParams_v3 as var
import csv
import re
import final_oxram_prog_v3_6 as final
import datetime as dt
import os
import sys
import matplotlib.pyplot as plt
from shutil import copyfile
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import SingleOperation

def dictionary(word):
    
    strategies = {'V': increase_voltage, 'SR': setReset }
    strategy = strategies[word]
    return strategy

def increase_voltage(plan):
    import numpy as np
    import math
    import variables_testParams_v3 as var
    import csv
    import re
    import final_oxram_prog_v3_6 as final
    import datetime as dt
    import os
    import sys
    import matplotlib.pyplot as plt
    from shutil import copyfile
    from madClassesAndFunctions_v3 import ReadOperation
    from madClassesAndFunctions_v3 import SingleOperation
    ###It only increases components 0 and 1 because they are the rising and final voltages
    ###the third component is the falling, which will always be zero
    if plan.name == "Set":
        plan.vTop[0] += stepSet
        plan.vTop[1] += stepSet
        print 'Increasing set voltage to ', plan.vTop[0]
    elif plan.name == "Reset":
        plan.vBot[0] += stepReset
        plan.vBot[1] += stepReset
        print 'Increasing reset voltage to ', plan.vBot[0]
    elif plan.name == "Forming":
        plan.vTop[0] += stepForm
        plan.vTop[1] += stepForm
        print 'Increasing forming voltage to ', plan.vTop[0]
    

def restart_voltage(initVset, initVreset):   ###This function resets the initial set and reset voltage to its initial conditions in order to start a new section
    import numpy as np
    import math
    import variables_testParams_v3 as var
    import csv
    import re
    import final_oxram_prog_v3_6 as final
    import datetime as dt
    import os
    import sys
    import matplotlib.pyplot as plt
    from shutil import copyfile
    from madClassesAndFunctions_v3 import ReadOperation
    from madClassesAndFunctions_v3 import SingleOperation
    var.set1.vTop[0] = initVset
    var.set1.vTop[1] = initVset

    var.reset1.vBot[0] = initVreset
    var.reset1.vBot[1] = initVreset

    
def setReset(plan):
    import numpy as np
    import math
    import variables_testParams_v3 as var
    import csv
    import re
    import final_oxram_prog_v3_6 as final
    import datetime as dt
    import os
    import sys
    import matplotlib.pyplot as plt
    from shutil import copyfile
    from madClassesAndFunctions_v3 import ReadOperation
    from madClassesAndFunctions_v3 import SingleOperation
    ###If the test is a reset, do this programming algorithm
    ###But if it is a Set, just do the increase voltage
    if plan[-2].name == "Reset":
        newPlan = [var.setSmart, var.reset1,plan[-1]]
    elif plan[-2].name == "Set":
        increase_voltage(plan[-2])
        newPlan = None

    return newPlan
        

    
##Writes the log file        
def write_log(logDirectory, originalPlan, firstTime, testNb, strategy, section, repetition, notWorking, stepSet, stepReset, Ron, Roff):

    import numpy as np
    import math
    import variables_testParams_v3 as var
    import csv
    import re
    import final_oxram_prog_v3_6 as final
    import datetime as dt
    import os
    import sys
    import matplotlib.pyplot as plt
    from shutil import copyfile
    from madClassesAndFunctions_v3 import ReadOperation
    from madClassesAndFunctions_v3 import SingleOperation
    initVset = var.set1.vTop[1]
    initVreset = var.reset1.vBot[1]
    smartSetV = var.setSmart.vTop[1]
    smartResetV = var.resetSmart.vBot[1]
    if firstTime:
        wr = open(logDirectory+'\\log.txt','w')
        wr.write('Test:\t'+str(testNb)+'\n')
        wr.write('Plan:\t ')
        for i in range(len(originalPlan)):
            wr.write(originalPlan[i].name+'\t')
        wr.write('\nRon (Ohm)\t'+str(Ron)+'\tRoff (Ohm)\t'+str(Roff)+'\n')
        wr.write('Strategy:\t'+strategy+'\n')
        if strategy == 'V':
            wr.write('Init Vset:\t'+str(initVset)+'\tInit Vreset:\t'+str(initVreset)+'\tStep Vset:\t'+str(stepSet)+'\tStep Vreset:\t'+str(stepReset)+'\n')
        elif strategy == 'SR':
            wr.write('Init Vset:\t'+str(initVset)+'\tInit Vreset:\t'+str(initVreset)+'\tSmart Vset:\t'+str(smartSetV)+'\tSmart Vreset:\t'+str(smartResetV)+'\n')
        else:
            wr.write('\n')
        wr.write('Section \t Repetition \t Bad cells \n')
    else:
        wr = open(logDirectory+'\\log.txt','a')

    wr.write(str(section)+'\t'+str(repetition-1)+'\t'+str(notWorking)+'\n')
    wr.close()

##Writes the number of cells that didn't switch after smart forming with addresslist
def write_log_forming(logDirectory, addressNotWorking):

    wr = open(logDirectory+'\\nonSwitched.txt','w')
    wr.write('Cells not formed \n')
    wr.write('Wln,WL,BL,\n')
    for j in range(0,len(addressNotWorking)/3):
        wr.write(addressNotWorking[j*3]+','+addressNotWorking[j*3+1]+','+addressNotWorking[j*3+2]+','+'\n')
    wr.close()




def plotDistributions(data,logDirectory,operationFolder):

    plt.clf()
    floatdata = [np.log10(float(data[i])) for i in range(0,len(data))]
    bins = np.linspace(2.5,7,75)
    plt.hist(floatdata, bins)
    ##plt.show()
    plt.savefig(logDirectory+'\\distribution_'+operationFolder+'.png')
    print('   OK\n')

             
def oneCell_perBit(stepSet,stepReset,maxSet,maxReset,maxGroup,Ron,Roff,strategy,initVset,initVreset):

    ###I CHECK HOW MANY TESTS WERE DONE
    nbTests = len(var.testPlan)
    originalPlan = var.testPlan
    lastOperation = 0
    section = 0
    firstTime = True
    for test in range(0,nbTests):

        if originalPlan[test].__class__ is ReadOperation:

            ###It repeats only the last section of the original plan
            var.testPlan = originalPlan[lastOperation:test+1]
            ###Right now it assumes that the only thing I want to repeat is the test right before the reading
            ###At some point, I have to improve this to repeat all the tests from read to read


            ###I start the execution of this part of the test plan the first time
            section += 1

            if section == 1:
                sys.argv = ["","",0,0,0]
            elif section > 0:
                sys.argv = ["Smart",section,0,lastOperation,0] ###By doing this, it will create the folder for the test only the firs time
                if strategy == 'V':
                    restart_voltage(initVset,initVreset)   ###We need to put the voltage in the original value in every section
                    print 'First execution of the section number ',section, ' of the test plan ... \n \n \n'
            final.main()
            lastOperation = test+1

            ###Necessary initialization: do not touch
            times = 1
            stop = False
            
            ###I repeat the execution of the test plan until: 1) it reaches the maximum number of times allowed,
            ###2) all the cells are switched
            while not stop:

                now = dt.datetime.now()
                mypath = r'%s\%s\%s' % (var.resultsOutput,
                                                var.waferLot + 'w' + var.waferNo,
                                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="
                                                +var.dutName)
                folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

                y=[]
                for i in range(len(folders)):
                    y.append(int(folders[i][-3:]))
                    y.sort()
                    
                ###I ONLY NEED THE LAST TEST DONE
                lastTest = y[-1]
                testname = 'Test_%s' % ((3 - len(str(lastTest)))*"0" + str(lastTest))
                mypath+='\\'+testname
                folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

                ###Initialization
                results=[]
                header=[]
                SL=[]
                WL=[]
                BL=[]
                Rmeas=[]
                addressNotWorking=[]
                ###NOT VALID FOR SEVERAL READS IN THE SAME TEST PLAN
                ###NEED TO ADD LATER (COUNT NUMBER OF READ FOLDERS TO INITIALIZE ARRAYS)

                ###I read the results of the test plan
                ###By the way is defined, the current test will always be a read
                if times == 1:
                    operationFolder = 'Op'+str(test+1)+'__Read'
                else:
                    operationFolder = 'Op'+str(test+1)+'__Read_rep'+str(times-1)

                ######
                ######RIGHT NOW IT ONLY TAKES THE FOLDER x0_y0
                ######NEEDS TO BE FIXED AT SOME POINT WHEN I ANALYZE SEVERAL DIES
                ######

                if var.adrsMode == 'S':
                    headerNb = 6
                elif var.adrsMode == 'A' or var.adrsMode == 'L':
                    headerNb = 3
                
                
                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                with open(mypath2+'results.csv','rt') as f:
                    reader = csv.reader(f)
                    j = 0
                    for row in reader:
                        if j<headerNb:
                            header.append(row)
                        else:
                            results.append(row)
                            SL.append(row[0])
                            WL.append(row[1])
                            BL.append(row[2])
                            Rmeas.append(row[3])
                        j+=1
                
                ###The operation before the reading is supposed to be the target state
                ###It will check if it's working depending if it's Set or Reset
                        
                working = np.zeros(len(Rmeas))
                
                if var.testPlan[-2].name is "Set":
                    for i in range(0,len(Rmeas)):
                        if float(Rmeas[i]) < Ron:
                            working[i] = 1
                elif var.testPlan[-2].name is "Reset":
                    for i in range(0,len(Rmeas)):
                        if float(Rmeas[i]) > Roff:
                            working[i] = 1
                elif var.testPlan[-2].name is "Forming":
                    for i in range(0,len(Rmeas)):
                        if float(Rmeas[i]) < Rform:
                            working[i] = 1

                ###Makes the distributions
                print('Creating histograms...  ')
                plotDistributions(Rmeas,mypath,operationFolder)

                ###Rewrites the address list with the number of cells that were not working

                for i in range(0,len(working)):
                    if working[i] == 0:
                        addressNotWorking.append(SL[i])
                        addressNotWorking.append(WL[i])
                        addressNotWorking.append(BL[i])
                notWorking = int(len(addressNotWorking)/3)
                        
                ###It checkes if it's necessary to stop
                if len(addressNotWorking) == 0:
                    stop = True
                    print('All cells were switched!')
                elif len(var.testPlan) > 2:
                    if times == maxGroup:
                        stop = True
                        print('The maximum number of repetitions of a group of operations has been achieved')
                elif var.testPlan[-2].name is "Set":
                    if times == maxSet:
                        stop = True
                        print('The maximum number of repetitions of Set has been achieved')
                elif var.testPlan[-2].name is "Reset":
                    if times == maxReset:
                        stop = True
                        print('The maximum number of repetitions of Reset has been achieved')
                elif var.testPlan[-2].name is "Forming":
                    if times == maxForm:
                        stop = True
                        print('The maximum number of repetitions of Forming has been achieved')                        
                 
                print notWorking,' cells were not switched \n'
                print "      Updating log file...  "
                ###It creates the log file
                if firstTime:
                    write_log(mypath, originalPlan, firstTime, lastTest, strategy, section, times, notWorking, stepSet, stepReset, Ron, Roff)
                    firstTime = False
                elif not firstTime:
                    write_log(mypath, originalPlan, firstTime, lastTest, strategy, section, times, notWorking, stepSet, stepReset, Ron, Roff)
                if var.testPlan[-2].name is "Forming":
                    if times == maxForm:
                        write_log_forming(mypath, addressNotWorking)
                    elif times < maxForm and stop == True:
                        write_log_forming(mypath, addressNotWorking)
                print "OK\n"

                if stop == False:
                    oldPlan = var.testPlan
                    ###CHOOSE SMART PROGRAMMING STRATEGY AND START THE EXECUTION
                    if strategy == 'V':
                        increase_voltage(originalPlan[test - 1])
                    elif strategy == 'SR':
                        if var.testPlan[-2].name is "Forming":
                            raise NameError('Forming is not compatible with SR strategy')
                        if setReset(var.testPlan) is not None:
                            var.testPlan = setReset(var.testPlan)
                    auxPlan = var.testPlan
                    print auxPlan
                    if len(addressNotWorking) > 274:
                        var.testPlan = auxPlan[:-1]  ###NEED TO GENERALIZE FOR GROUP OF OPERATIONS
                        for i in range(int(math.ceil((len(addressNotWorking)/3.0)/274))):
                            print 'Starting execution number ', times, ' with improved conditions. Part ', i+1
                            print ' (',int(math.ceil((len(addressNotWorking)/3.0)/274)),' parts) \n'
                            
                            wr = open('address_list.txt','w')
                            wr.write('Format must be like Wln,WL,BL,\n')
                            for j in range(i*274,(i+1)*274):
                                if j == len(addressNotWorking)/3:
                                    break
                                wr.write(addressNotWorking[j*3]+','+addressNotWorking[j*3+1]+','+addressNotWorking[j*3+2]+','+'\n')
                            wr.close()
                            copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part'+str(i+1)+'.txt')
                            
                            var.adrsMode = 'L'
                            sys.argv=["Smart","Parts",i+1,test-1,times]
                            final.main()
                            
                        ###Now only read the whole matrix in S mode    
                        var.adrsMode = 'S'
                        var.testPlan = oldPlan[-1:]  ###Before I separated Read from the rest, now I take only the read
                        sys.argv=["Smart",section,i+1,test,times]
                        print 'Starting repetition number ', times, ' with improved conditions. Last part (read)\n'
                        final.main()
                    else: 
                        print 'Starting repetition number ', times,' with improved conditions \n '

                        wr = open('address_list.txt','w')
                        wr.write('Format must be like Wln,WL,BL,\n')
                        for j in range(0,len(addressNotWorking)/3):
                            wr.write(addressNotWorking[j*3]+','+addressNotWorking[j*3+1]+','+addressNotWorking[j*3+2]+','+'\n')
                        wr.close()
                        copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part1.txt')

                        sys.argv=['Smart',section,0,test-1,times]
                        var.adrsMode = "L"
                        var.testPlan = auxPlan[:-1]  ###Do the previous plan first
                        final.main()
                        sys.argv=['Smart',section,0,test,times]
                        var.testPlan = oldPlan[-1:]  ###Then read in Scan mode
                        var.adrsMode = 'S'
                        final.main()

                     
                        
                    var.testPlan = oldPlan
                    
                times += 1

                #Here if stop is not True it will do again the loop until stop is finally set to False
                #After this it will continue to the next
                      









def updateAddressList_twoCells(parity,addresses):

    wr = open('address_list.txt','w')
    wr.write('Format must be like Wln,WL,BL,\n')
    if parity == 'even':
        for j in range(0,len(addresses)/3):
            wr.write(addresses[j*3]+','+addresses[j*3+1]+','+addresses[j*3+2]+','+'\n')
    elif parity == 'odd':
        for j in range(0,len(addresses)/3):
            wr.write(addresses[j*3]+','+str(int(addresses[j*3+1])+1)+','+addresses[j*3+2]+','+'\n')                        
    wr.close()


def twoCells_perBit(stepSet,stepReset,maxSet,maxReset,maxGroup,Ron,Roff,strategy,initVset,initVreset):
                                     
    ###I CHECK HOW MANY TESTS WERE DONE
    nbTests = len(var.testPlan)
    originalPlan = var.testPlan

    lastOperation = 0
    section = 0
    firstTime = True
    for test in range(0,nbTests):

        print 'Test number  '+str(test)+'\n \n'

        if originalPlan[test].__class__ is ReadOperation:

            ###It repeats only the last section of the original plan
            var.testPlan = originalPlan[lastOperation:test+1]
            ###Right now it assumes that the only thing I want to repeat is the test right before the reading
            ###At some point, I have to improve this to repeat all the tests from read to read


            ###I start the execution of this part of the test plan the first time
            section += 1
            if section == 1:
                sys.argv = ["",section,0,lastOperation,0]
            elif section > 0:
                sys.argv = ["Smart",section,0,lastOperation,0] ###By doing this, it will create the folder for the test only the firs time
                if strategy == 'V':
                    restart_voltage(initVset,initVreset)   ###We need to put the voltage in the original value in every section            print 'First execution of the section number ',section, ' of the test plan ... \n \n \n \n \n'
            lastOperation = test+1
                                     
            savedPlan = var.testPlan
            print var.testPlan
            if var.testPlan[-2].name is "Set":
                var.testPlan = [var.set1]
                var.scanMode = 'RS'
                final.main()
                sys.argv[0] = "Smart" ###By doing this, it will create the folder for the test only the firs time
                var.testPlan = [var.reset1]
                var.scanMode = 'IRS'
                final.main()
            elif var.testPlan[-2].name is "Reset":
                var.testPlan = [var.reset1]
                var.scanMode = 'RS'
                final.main()
                sys.argv[0] = "Smart" ###By doing this, it will create the folder for the test only the firs time
                var.testPlan = [var.set1]
                var.scanMode = 'IRS'
                final.main()

            var.scanMode = 'All'
            var.adrsMode = 'S'
            var.testPlan = [var.rd100]
            sys.argv[3] = test
            final.main()
                           
            var.testPlan = savedPlan

            ###Necessary initialization: do not touch
            times = 1
            stop = False

            ###I repeat the execution of the test plan until: 1) it reaches the maximum number of times allowed,
            ###2) all the cells are switched
            while not stop:

                now = dt.datetime.now()
                mypath = r'%s\%s\%s' % (var.resultsOutput,
                                                var.waferLot + 'w' + var.waferNo,
                                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="
                                                +var.dutName)
                folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

                y=[]
                for i in range(len(folders)):
                    y.append(int(folders[i][-3:]))
                    y.sort()
                    
                ###I ONLY NEED THE LAST TEST DONE
                lastTest = y[-1]
                testname = 'Test_%s' % ((3 - len(str(lastTest)))*"0" + str(lastTest))
                mypath+='\\'+testname
                folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

                ###Initialization
                results=[]
                header=[]
                SL=[]
                WL=[]
                BL=[]
                Rmeas=[]
                addressNotWorking=[]
                working=[]
                           
                ###NOT VALID FOR SEVERAL READS IN THE SAME TEST PLAN
                ###NEED TO ADD LATER (COUNT NUMBER OF READ FOLDERS TO INITIALIZE ARRAYS)

                ###I read the results of the test plan
                ###By the way is defined, the current test will always be a read
                if times == 1:
                    operationFolder = 'Op'+str(test+1)+'__Read'
                else:
                    operationFolder = 'Op'+str(test+1)+'__Read_rep'+str(times-1)

                ######
                ######RIGHT NOW IT ONLY TAKES THE FOLDER x0_y0
                ######NEEDS TO BE FIXED AT SOME POINT WHEN I ANALYZE SEVERAL DIES
                ######

                if var.adrsMode == 'S':
                    headerNb = 6
                elif var.adrsMode == 'A' or var.adrsMode == 'L':
                    headerNb = 3
                
                
                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                with open(mypath2+'results.csv','rt') as f:
                    reader = csv.reader(f)
                    j = 0
                    for row in reader:
                        if j<headerNb:
                            header.append(row)
                        else:
                            results.append(row)
                            SL.append(row[0])
                            WL.append(row[1])
                            BL.append(row[2])
                            Rmeas.append(row[3])
                        j+=1
                
                ###The operation before the reading is supposed to be the target state
                ###It will check if it's working depending if it's Set or Reset

                working = np.zeros(len(Rmeas)/2)
                
                if var.testPlan[-2].name is "Set":
                    for i in range(0,len(Rmeas),2):
                        if float(Rmeas[i]) - float(Rmeas[i+1]) < 0:
                            working[i/2] = 1

                elif var.testPlan[-2].name is "Reset":
                    for i in range(0,len(Rmeas),2):
                        if float(Rmeas[i]) - float(Rmeas[i+1]) > 0:
                            working[i/2] = 1

                
                ###Makes the distributions
                print('Creating histograms...  ')
                plotDistributions(Rmeas,mypath,operationFolder)

                ###Rewrites the address list with the number of cells that were not working

                for i in range(0,len(working)):
                    if working[i] == 0:
                        addressNotWorking.append(SL[i*2])
                        addressNotWorking.append(WL[i*2])
                        addressNotWorking.append(BL[i*2])
                notWorking = int(len(addressNotWorking)/3)
                        
                ###It checkes if it's necessary to stop
                if len(addressNotWorking) == 0:
                    stop = True
                    print('All cells were switched!')
                elif len(var.testPlan) > 2:
                    if times == maxGroup:
                        stop = True
                        print('The maximum number of repetitions of a group of operations has been achieved')
                elif var.testPlan[-2].name is "Set":
                    if times == maxSet:
                        stop = True
                        print('The maximum number of repetitions of Set has been achieved')
                elif var.testPlan[-2].name is "Reset":
                    if times == maxReset:
                        stop = True
                        print('The maximum number of repetitions of Reset has been achieved')
                 
                print notWorking,' cells were not switched \n'
                print "      Updating log file...  "
                ###It creates the log file
                if firstTime:
                    write_log(mypath, originalPlan, firstTime, lastTest, strategy, section, times, notWorking, stepSet, stepReset, Ron, Roff)
                    firstTime = False
                elif not firstTime:
                    write_log(mypath, originalPlan, firstTime, lastTest, strategy, section, times, notWorking, stepSet, stepReset, Ron, Roff)
                print "OK\n"

                if stop == False:
                    ###CHOOSE SMART PROGRAMMING STRATEGY AND START THE EXECUTION
                    #dictionary(strategy)(originalPlan[test - 1])
                    oldPlan = var.testPlan
                
                    if len(addressNotWorking) > 274:
                        for i in range(int(math.ceil((len(addressNotWorking)/3.0)/274))):
                            print 'Starting execution number ', times, ' with improved conditions. Part ', i+1
                            print ' (',int(math.ceil((len(addressNotWorking)/3.0)/274)),' parts) \n'

                            if i == int(math.ceil((len(addressNotWorking)/3.0)/274))-1:
                                if oldPlan[-2].name == "Set":
                                    var.testPlan = [var.set1]
                                    updateAddressList_twoCells('even',addressNotWorking[i*274:])
                                elif oldPlan[-2].name == "Reset":
                                    var.testPlan = [var.reset1]
                                    updateAddressList_twoCells('even',addressNotWorking[i*274:])
                            else:
                                if oldPlan[-2].name == "Set":
                                    var.testPlan = [var.set1]
                                    updateAddressList_twoCells('even',addressNotWorking[i*274:(i+1)*274])
                                elif oldPlan[-2].name == "Reset":
                                    var.testPlan = [var.reset1]
                                    updateAddressList_twoCells('even',addressNotWorking[i*274:(i+1)*274])
                       
                            copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part'+str(i+1)+'_even.txt')

                            var.adrsMode = 'L'
                            sys.argv=["Smart","Parts",i+1,test-1,times]
                            final.main()

                            if i == int(math.ceil((len(addressNotWorking)/3.0)/274))-1:
                                if oldPlan[-2].name == "Set":
                                    var.testPlan = [var.reset1]
                                    updateAddressList_twoCells('odd',addressNotWorking[i*274:])
                                elif oldPlan[-2].name == "Reset":
                                    var.testPlan = [var.set1]
                                    updateAddressList_twoCells('odd',addressNotWorking[i*274:])
                            else:
                                if oldPlan[-2].name == "Set":
                                    var.testPlan = [var.reset1]
                                    updateAddressList_twoCells('odd',addressNotWorking[i*274:(i+1)*274])
                                elif oldPlan[-2].name == "Reset":
                                    var.testPlan = [var.set1]
                                    updateAddressList_twoCells('odd',addressNotWorking[i*274:(i+1)*274])

                            copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part'+str(i+1)+'_odd.txt')

                            var.adrsMode = 'L'
                            sys.argv=["Smart","Parts",i+1,test-1,times]
                            final.main()
                            
                        var.adrsMode = 'S'
                        var.testPlan = [originalPlan[test]]
                        sys.argv=["Smart","Parts",i+1,test,times]
                        print 'Starting execution number ', times, ' with improved conditions. Last part \n'
                        final.main()
                    else: 
                        print 'Starting execution number ',times,' with improved conditions \n '

                        if oldPlan[-2].name == "Set":
                            var.testPlan = [var.set1]
                            updateAddressList_twoCells('even',addressNotWorking)
                        elif oldPlan[-2].name == "Reset":
                            var.testPlan = [var.reset1]
                            updateAddressList_twoCells('even',addressNotWorking)

                        copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part1_even.txt')
                                
                        sys.argv=['Smart','',0,test-1,times]
                        var.adrsMode = "L"
                        final.main()
                                     
                        if oldPlan[-2].name == "Set":
                            var.testPlan = [var.reset1]
                            updateAddressList_twoCells('odd',addressNotWorking)
                        elif oldPlan[-2].name == "Reset":
                            var.testPlan = [var.set1]
                            updateAddressList_twoCells('odd',addressNotWorking)

                        copyfile('address_list.txt',mypath+'\\address_list_sect_'+str(section)+'_rep'+str(times)+'_part1_odd.txt')
                                 
                        sys.argv=['Smart','',0,test-1,times]
                        var.adrsMode = "L"
                        final.main()
                                     
                        sys.argv=['Smart','',0,test,times]
                        var.testPlan = [originalPlan[test]]  ###Then read in Scan mode
                        var.adrsMode = 'S'
                        final.main()

                     
                        
                    var.testPlan = oldPlan
                    
                times += 1

                #Here if stop is not True it will do again the loop until stop is finally set to False
                #After this it will continue to the next
                                     
            var.testPlan = originalPlan







def test_die():


    stepSet = 0.1
    stepReset = 0.1
    stepForm = 0.2
    maxSet = 6      ###Maximum amount of times I will do a Set operation (notice: the number of repetitions is maxSet - 1 !!)
    maxReset = 1    ###Maximum amount of times I will do a Reset operation (notice: the number of repetitions is maxReset - 1 !!)
    maxGroup = 3    ###Maximum amount of times I will do a group of operations (notice: the number of repetitions is maxGroup - 1 !!)
    maxForm = 7     ###Maximum amount of times I will do a group of operations (notice: the number of repetitions is maxGroup - 1 !!)
    Ron = 7e3
    Roff = 40e3
    Rform = 1e5
    strategy = 'V'
    initVset = var.set1.vTop[1]
    initVreset = var.reset1.vBot[1]

    if strategy == 'TB':
        twoCells_perBit(stepSet,stepReset,maxSet,maxReset,maxGroup,Ron,Roff,strategy,initVset,initVreset)
    else:
        oneCell_perBit(stepSet,stepReset,maxSet,maxReset,maxGroup,Ron,Roff,strategy,initVset,initVreset)





                                         
