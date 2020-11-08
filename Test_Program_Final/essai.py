from final_oxram_prog_v4_8 import test_die
import linecache
i=2
die=linecache.getline('DUT.txt', i)
x = str(int(die[0:2]))
y = str(int(die[3:]))

mon_fichier_info = open("Informations.txt", "r")
lotname=linecache.getline('Informations.txt', 2)
lotname=lotname.replace("lot name=","")
lotname=lotname.replace("\n","")
print lotname
size_of_memory=linecache.getline('Informations.txt', 1)
size_of_memory=size_of_memory.replace("size of memory=","")
size_of_memory=size_of_memory.replace("\n","")
print size_of_memory
wafernumber=linecache.getline('Informations.txt', 3)
wafernumber=wafernumber.replace('wafer name = ',"")
wafernumber=wafernumber.replace("\n","")
print wafernumber
test_die( lotname , wafernumber , x , y ,'4K',1 )
