import sys
import datetime as dt
import numpy as np
sys.path.append("C:\\Users\\Ben\\Documents\\ci\\code\\comp_invest")
import CompInvestingTools as ci
##Market simulation.
beginDT = dt.datetime(2000,1,1)
endDT = dt.datetime(2012,12,31)
#SPY not listed becasue it gets appended
secSyms = ['QQQ','DIA']
#'close' is adjusted close
dataLst = ['close']
priceDF = ci.readHistDataToDF(beginDT,endDT,secSyms,dataLst)
secWts = np.array([0.55,0.30,0.15])
secRets = np.zeros((1,secWts.size))
sampleDates = ci.generateAnnualDT(2000,2013)
allRets = np.zeros((len(sampleDates),5))
for j in range(0,(len(sampleDates)-1)):
    dtRng = sampleDates[j]
    drPlus = sampleDates[j + 1]
    #calculate SPY return past 180 days
    past180 = dtRng[1] - dt.timedelta(days=180)
    begin180 = priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))][0]
    lastIdx = len(priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))]) - 1
    end180 = priceDF['close']['SPY'][past180:(dtRng[1] + dt.timedelta(days=1))][lastIdx]
    return180 = ((end180 - begin180) / begin180) * 100
    #Calc SPY return for drPlus
    spyBegin = priceDF['close']['SPY'][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))][0]
    lastIdx = len(priceDF['close']['SPY'][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))]) - 1
    spyEnd = priceDF['close']['SPY'][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))][lastIdx]
    spyReturn = ((spyEnd - spyBegin) / spyBegin) * 100
    allRets[j+1,1] = spyReturn
    #Calc Port return for drPlus     
    for i in range(0,len(priceDF['close'].keys())):
        sym = priceDF['close'].keys()[i]
        beginPrice = priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))][0]
        lastIdx = len(priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))]) - 1
        endPrice = priceDF['close'][sym][drPlus[0]:(drPlus[1] + dt.timedelta(days=1))][lastIdx]
        iReturn = (((endPrice - beginPrice) / beginPrice) * 100) * secWts[i]
        secRets[0,i] = iReturn
    allRets[j+1,2] = secRets.sum()
    #Flag choices
    if return180 <= 0:
        allRets[j+1,0] = spyReturn
        allRets[j+1,3] = 1
        allRets[j+1,4] = 0
    else:
        allRets[j+1,0] = secRets.sum()
        if secRets.sum() >= spyReturn:
            allRets[j+1,3] = 1
        allRets[j+1,4] = 1
            
print allRets
print allRets.sum(axis=0)