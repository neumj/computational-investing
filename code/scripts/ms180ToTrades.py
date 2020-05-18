import sys
import datetime as dt
import math
import numpy as np
sys.path.append("C:\\Users\\Ben\\Documents\\ci\\code\\comp_invest")
import CompInvestingTools as ci
sys.path.append("C:\\Users\\Ben\Documents\\code\\python\\mjn_modules\\gen_mod")
import gen_tools as gen

#define functions
def log180Buys(futDtRng,cash,eqWts):


logFile = "C:\\Users\\Ben\\Documents\\ci\\hw\\MarketTest\\Test180_01.txt"
##Market simulation.
beginDT = dt.datetime(2000,1,1)
endDT = dt.datetime(2012,12,31)
#SPY not listed becasue it gets appended
secSyms = ['QQQ','DIA']
#'close' is adjusted close
dataLst = ['close']
priceDF = ci.readHistDataToDF(beginDT,endDT,secSyms,dataLst)
wtOpt = [[0.55,0.30,0.15],[0.333,0.333,0.333],[0,0,1.0]]
initCash = [100000]
secRets = np.zeros((1,len(wtOpt[0])))
maxRets = np.zeros((1,len(wtOpt[0])))
sampleDates = ci.generateAnnualDT(2000,2013)
allRets = np.zeros((len(sampleDates),5))
prvWts = -1
for j in range(0,(len(sampleDates)-1)):
    dtRng = sampleDates[j]
    drPlus = sampleDates[j + 1]
    #calculate SPY return past 180 days
    past180 = dtRng[1] - dt.timedelta(days=180)
    begin180 = priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))][0]
    lastIdx = len(priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))]) - 1
    end180 = priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))][lastIdx]
    return180 = ((end180 - begin180) / begin180) * 100
    #calculate SPY return past 45 days
    past60 = dtRng[1] - dt.timedelta(days=60)
    begin60 = priceDF['close']['SPY'][past60:(dtRng[1] + dt.timedelta(days=1))][0]
    lastIdx = len(priceDF['close']['SPY'][past60:(dtRng[1] + dt.timedelta(days=1))]) - 1
    end60 = priceDF['close']['SPY'][past60:(dtRng[1] + dt.timedelta(days=1))][lastIdx]
    return60 = ((end60 - begin60) / begin60) * 100
    #Select Wt Opt
    if return180 >= 0 and return60 >= -2.0:
        secWts = wtOpt[0]
        allRets[j+1,4] = 0
        curWts = 0
    elif return180 <= 0 and return60 >= 7.5:
        secWts = wtOpt[0]
        allRets[j+1,4] = 0
        curWts = 0
    elif return180 < 0 and return60 < 0:
        secWts = wtOpt[2]
        allRets[j+1,4] = 2
        curWts = 2
    else:
        secWts = wtOpt[2]
        allRets[j+1,4] = 2
        curWts = 2
    #Handle buys
    print curWts
    print prvWts
    if prvWts == -1 or (prvWts == curWts) == False:
        for i in range(0,len(priceDF['close'].keys())):
            sym = priceDF['close'].keys()[i]
            beginPrice = priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))][0]
            numShares = math.floor((secWts[i] * initCash[0]) / beginPrice)
            buyDtStr = str(priceDF['close'][sym][drPlus[0]:drPlus[1]].index[0])
            yearInt = int(buyDtStr.split(' ')[0].split('-')[0])
            monInt = int(buyDtStr.split(' ')[0].split('-')[1])
            dayInt = int(buyDtStr.split(' ')[0].split('-')[2])
            logStr =  str(yearInt) + "," + str(monInt) + "," + str(dayInt) + "," + sym + "," + "Buy" + "," + str(numShares)  + "\n"
            if numShares > 0:
                print logStr
                gen.write_log(logFile,logStr) 
                lastIdx = len(priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))]) - 1
                sellDtStr = str(priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))].index[lastIdx])
                yearInt = int(sellDtStr.split(' ')[0].split('-')[0])
                monInt = int(sellDtStr.split(' ')[0].split('-')[1])
                dayInt = int(sellDtStr.split(' ')[0].split('-')[2])
                logStr =  str(yearInt) + "," + str(monInt) + "," + str(dayInt) + "," + sym + "," + "Sell" + "," + str(numShares)  + "\n"
                print logStr
                gen.write_log(logFile,logStr)
    prvWts = curWts