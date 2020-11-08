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
from itertools import compress
from adjustText import adjust_text




path = 'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\Mixed\\efficiencies\\'

colors = {'SR':'b','V':'r','TB':'g'}
markers = {'4k':'o','64k':'s','1M':'D'}
        
fileNameSet ='mean_set.txt'
fileNameReset ='mean_reset.txt'


if os.path.isfile(path+fileNameSet) and os.path.isfile(path+fileNameReset):
    
    txt = open(path+fileNameSet)

    g=[]

    for line in txt:
        g.append(line)

    allDataSet = []

    txt = open(path+fileNameReset)

    g2=[]

    for line in txt:
        g2.append(line)

    allDataReset = []


    for i in range(1,len(g)):
        allDataSet.append(g[i].split('\t'))
        allDataReset.append(g2[i].split('\t'))
        
    tests = [int(allDataSet[k][7]) for k in range(len(allDataSet))]
    allMeansReset = [float(allDataReset[k][12]) for k in range(len(allDataReset))]
    allMeansSet = [float(allDataSet[k][12]) for k in range(len(allDataSet))]
    allSdvsReset = [float(allDataReset[k][13]) for k in range(len(allDataReset))]
    allSdvsSet = [float(allDataSet[k][13]) for k in range(len(allDataSet))]
    allVset = [float(allDataSet[k][3]) for k in range(len(allDataSet))]
    allVreset = [float(allDataReset[k][3]) for k in range(len(allDataReset))]
    allTimes = [float(allDataReset[k][9]) for k in range(len(allDataReset))]

    uniqueTests = list(set(tests))
    print(uniqueTests)

    for nb in range(len(uniqueTests)):

        meansSet = [allMeansSet[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]
        sdvsSet = [allSdvsSet[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]
        meansReset = [allMeansReset[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]
        sdvsReset = [allSdvsReset[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]

        Vset = [allVset[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]
        Vreset = [allVreset[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]
        times = [allTimes[i] for i, j in enumerate(tests) if j == uniqueTests[nb]]

        
        f = plt.figure(1)
        plt.plot(meansSet,'r.-')
        plt.plot(meansReset,'b.-')
        f2 = plt.figure(2)
        plt.plot(sdvsSet,'r.-')
        plt.plot(sdvsReset,'b.-')
                

        plt.figure(1)
        plt.title('Resistance mean in cycling (Vs = '+str(Vset[0])+', Vr = '+str(Vreset[0])+', t = '+str(times[0]))
        plt.xlabel('Cycles []')
        plt.ylabel('Resistance (Ohm)')
        plt.grid()
##      plt.legend(loc='lower right')
##      plt.plot([0,1],[0,1],'r-.',label='_nolegend_')
        axes = plt.gca()
        axes.set_ylim([1e3, 1e7])
        axes.set_yscale('log')
                  
        fig_title = 'mean_test'+str(int(uniqueTests[nb]))
        plt.savefig(path+'cycling\\'+fig_title+'.png')
        plt.close()

                  

        plt.figure(2)
        plt.title('Resistance stdev in cycling (Vs = '+str(Vset[0])+', Vr = '+str(Vreset[0])+', t = '+str(times[0]))
        plt.xlabel('Cycles []')
        plt.ylabel('Standard deviation (Ohm)')
        plt.grid()
##      plt.legend(loc='lower right')
##      plt.plot([0,1],[0,1],'r-.',label='_nolegend_')
        axes = plt.gca()
        axes.set_ylim([1e2, 1e6])
        axes.set_yscale('log')

        fig_title = 'sdv_test'+str(int(uniqueTests[nb]))
        plt.savefig(path+'cycling\\'+fig_title+'.png')
        plt.close()





