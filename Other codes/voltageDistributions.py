import xlrd
import datetime as dt
import os
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
import sys
import fnmatch
from matplotlib import cm
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import LogFormatterMathtext
import matplotlib.ticker as ticker
import matplotlib.backends.backend_pdf


def getDay(date):

    date = date.split(';')
    day = date[0]
    month = date[1]
    year = date[2]

    theDate = day+'-'+month+'-'+year

    return theDate

def getDie(die):

    die = die.split(';')
    die1 = die[0]
    die2 = die[1]

    return die1,die2


def readTestFlow(path,together):

    print('here')
    workbookPath = path+'\\mixedForming.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

    #Extract the information of the test plan
    if together:
        testflow = workbook.sheet_by_name('Together')
    else:
        testflow = workbook.sheet_by_name('Separate')
        
    tests = testflow.col(0)
    strategies = testflow.col(1)
    plan = testflow.col(2)
    die = testflow.col(3)
    Vs = testflow.col(4)
    Vr = testflow.col(5)
    stepVs = testflow.col(6)
    stepVr = testflow.col(7)
    repSet = testflow.col(8)
    repReset = testflow.col(9)
    date = testflow.col(10)
    time = testflow.col(11)
    size = testflow.col(12)


    return tests, strategies, plan, die, Vs, stepVs, repSet, date, size




def readR(mypath,operationFolder):


    ###Initialization
    headerNb = 6
    results=[]
    header=[]
    SL=[]
    WL=[]
    BL=[]
    Rmeas=[]
    addressNotWorking=[]

    mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'

    if os.path.isdir(mypath2) == False:
        mypath2 = mypath+'\\'+operationFolder+'\\'
    
    with open(mypath2+'results.csv','rt') as f:
        reader = csv.reader(f)
        j = 0
        for row in reader:
            if j<headerNb:
                header.append(row)
            else:
                SL.append(row[0])
                WL.append(row[1])
                BL.append(row[2])
                Rmeas.append(row[3])
            j+=1

    return Rmeas, SL, WL, BL
    
def plotter(path,together):

    f1 = plt.figure()
    f2 = plt.figure()

    dic = {'4k':4096,'64k':65536}

    Rforming = 100000


    [tests, strategies, plan, die, Vs, stepVs, repSet, date, size] = readTestFlow(path,together)
        
    count = 0
    print(stepVs)
    
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count

    for test in range(1,nbTests+1):

        print(test)

        voltage = [6]*dic.get(size[test].value)
        flag = [True]*dic.get(size[test].value)

        testPlan = plan[test].value

        if testPlan != 'form':
            raise NameError('Form needed')
        if strategies[test].value != 'V':
            raise NameError('Strategy has to be V')

        theDate = getDay(date[test].value)
        [die1,die2] = getDie(die[test].value)

        mypath = r'%s' % (path+'\\'+size[test].value+'bit\\'+theDate+'\\')
        dirFiles = os.listdir(mypath)
        filesAux = [fnmatch.fnmatchcase(dirFiles[f],'Test_*') for f in range(len(dirFiles))]
        files = [t for t,k in zip(dirFiles,filesAux) if k]
        filename = []
        y=[]
        
        if len(files) == 0:
            raise NameError('No files in directory')
        else:
            for i in range(len(files)):
                y.append(int(files[i][-3:]))   #return a list of the last 3 digits in folders as integers
            y.sort()
            
        index = [t for t,x in enumerate(y) if x == tests[test].value]
        theFile = files[index[0]]

        mypath = mypath + theFile + '\\'

        filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read_rep*') if os.path.isdir(mypath+f)]
        opNb = filesAux[0][:3]

        for repe in range(0,int(repSet[test].value)+1):
        
            if repe == 0:

                operationFolder = opNb + '__Read'

            else:

                operationFolder = opNb + '__Read_rep'+str(repe)


            mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'

            Rmeas, SL, WL, BL = readR(mypath,operationFolder)

            RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
            RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]

            for res in range(len(RmeasFloat)):

                if RmeasFloat[res] < Rforming and flag[res]:

                    voltage[res] = Vs[test].value+stepVs[test].value*repe
                    flag[res] = False
            
            if size[test].value == '4k':
                colorForPlot = 'b'
            else:
                colorForPlot = 'r'

            if repe == 0:
                if size[test].value == '4k':
                    legendLabel = '4 kb'
                elif size[test].value == '64k':
                    legendLabel = '64 kb'
            else:
                legendLabel = '_nolegend_'
                
            plt.figure(f1.number)
            (quantiles, values), (slope, intercept, r) = stats.probplot(RmeasLog, dist='norm')
            plt.plot(values, quantiles,colorForPlot+'.',label=legendLabel)
            ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
            ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
            plt.yticks(ticks_quan,ticks_perc)
            plt.grid(True)
            plt.axis([2.5, 8,-5,5])

        if size[test].value == '4k':
            legendLabel = '4 kb'
        elif size[test].value == '64k':
            legendLabel = '64 kb'
            
        plt.title('Normal probability plot for Forming')
        plt.xlabel('Log of resistance [log(Ohm)]')
        plt.legend(loc='lower right')
        plt.ylabel('Probability (%)')
        if together:
            fig_title = 'together_normalPlotForming'
            pdf = matplotlib.backends.backend_pdf.PdfPages(r'%s' % (path+'\\Mixed\\Forming\\Pdf\\'+fig_title+".pdf"))
            pdf.savefig(f1.number)
            pdf.close()
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\',fig_title+'.png'))
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\Pdf\\',fig_title+'.svg'))
        elif not together:
            fig_title = 'normalPlotForming_'+size[test].value+'_'+die1+'-'+die2
            #pdf = matplotlib.backends.backend_pdf.PdfPages(r'%s' % (path+'\\Mixed\\Forming\\Pdf\\'+fig_title+".pdf"))
            #pdf.savefig(f1.number)
            #pdf.close()
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\',fig_title+'.png'))
            plt.clf()

        plt.figure(f2.number)
        (quantiles, values), (slope, intercept, r) = stats.probplot(voltage, dist='norm')
        plt.plot(values, quantiles,colorForPlot+'-',label=legendLabel)
        plt.legend(loc='lower right')
        ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
        ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
        plt.yticks(ticks_quan,ticks_perc)
        plt.grid(True)
        plt.axis([2, 7,-5,5])
        plt.title('Forming voltage distribution')
        plt.xlabel('Forming voltage (V)')
        plt.ylabel('Probability (%)')
        if together:
            fig_title = 'together_voltageForming'
            pdf = matplotlib.backends.backend_pdf.PdfPages(r'%s' % (path+'\\Mixed\\Forming\\Pdf\\'+fig_title+".pdf"))
            pdf.savefig(f2.number)
            pdf.close()
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\',fig_title+'.png'))
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\Pdf\\',fig_title+'.svg'))
        elif not together:
            fig_title = 'voltageForming_'+size[test].value+'_'+die1+'-'+die2
            #pdf = matplotlib.backends.backend_pdf.PdfPages(r'%s' % (path+'\\Mixed\\Forming\\Pdf\\'+fig_title+".pdf"))
            #pdf.savefig(f2.number)
            #pdf.close()
            plt.savefig(r'%s/%s' % (path+'\\Mixed\\Forming\\',fig_title+'.png'))
            plt.clf()
        #plt.show()



if '__main__'==__name__:

    stop = False

    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23'

    while not stop:
        try:
            together = raw_input('Do you want to plot the files together? "Y" or "N"')
        except:
            together = input('Do you want to plot the files together? "Y" or "N"')

        if together == 'Y' or together == 'y':
            together = True
            stop = True
        elif together == 'n' or together == 'N':
            together = False
            stop = True
        else:
            print('\nNot correct. Please insert "y" or "n"')
    
    plotter(path,together)

