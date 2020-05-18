'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import math
import itertools
import datetime as dt
import pandas as pd

print "Pandas Version", pd.__version__

def portfolioMetrics(startDate,endDate,symbolList,assetAlloc):
    #turn allocation wt list into array
    arrAlloc = array(assetAlloc)
    allocIdx = arrAlloc != 0
    #Set time of day to 16:00
    dt_timeofday = dt.timedelta(hours=16)
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(startDate, endDate, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbolList, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
        
    # Getting the numpy ndarray of close prices.
    #print d_data    
    na_price = d_data['close'].values
    normalizedPrice = na_price / na_price[0, :]
    wtPrice = normalizedPrice[:,allocIdx] * arrAlloc[allocIdx]
    wtPriceSum = wtPrice.sum(axis = 1)
    cumTotRet = wtPriceSum[wtPriceSum.size - 1] / wtPriceSum[0]
    dailyReturn = tsu.returnize0(wtPriceSum)
    portVolatility = dailyReturn.std()
    portAveDalRet = dailyReturn.mean()
    sharpeRatio = math.sqrt(len(ldt_timestamps)) * (portAveDalRet / portVolatility).tolist()     
    cumTotRet = [float(cumTotRet)]    
    portVolatility = [float(portVolatility)]
    portAveDalRet = [float(portAveDalRet)]
    sharpeRatio = [float(sharpeRatio)]
    return portVolatility, portAveDalRet, sharpeRatio, cumTotRet
    
def generateValidAllocations(percentStep,numSymbols):
    validAllocs = []
    stepVal = int(100 / percentStep)
    for i in itertools.product(range(stepVal + 1), repeat=numSymbols):
        if sum(i) == stepVal:
            alloc = map(lambda x: float(x) / stepVal, i)
            validAllocs.append(alloc)  
    return validAllocs
        
        
#Simulations Basics
dtStart = dt.datetime(2000, 1, 1)
dtEnd = dt.datetime(2000, 12, 31)
lstSym = ['QQQ','DIA','SPY']
#lstSym = ['LQD','SPY']
allocationStep = 30

#Generate valid allocations
print "Generating valid allocations..."
validAllocs = generateValidAllocations(allocationStep,len(lstSym))
print "Done."

#Optimizing
print "Generating performance metrics..."
bestAlloc = []
bestSharpe = []
bestCumRet = []
for vA in validAllocs:
    pVolatility, pAveDalRet, pSharpeRatio, pCumulativeTotRet = portfolioMetrics(dtStart,dtEnd,lstSym,vA)
    if len(bestCumRet) == 0:
        bestCumRet = pCumulativeTotRet
        bestAlloc = vA
        print "  Begining CumulativeTotRet: " + str(bestCumRet)
        print "  Begining Allocation: " + str(bestAlloc)
    else:
        if pCumulativeTotRet > bestCumRet:
            bestCumRet = pCumulativeTotRet
            bestAlloc = vA
#    if len(bestSharpe) == 0:
#        bestSharpe = pSharpeRatio
#        bestAlloc = vA
#        print "Begining Sharpe ratio: " + str(bestSharpe)
#        print "Begining Allocation: " + str(bestAlloc)
#    else:
#        if pSharpeRatio > bestSharpe:
#            bestSharpe = pSharpeRatio
#            bestAlloc = vA
print "Done."
#print "Best Sharpe ratio: " + str(bestSharpe)
#print "Best Allocation: " + str(bestAlloc)
print "Best CumRet: " + str(bestCumRet)
print "Best Allocation: " + str(bestAlloc)
           

#print "Portfolio volatility: " + str(pVolatility)
#print "Portfolio average daily return: " +  str(pAveDalRet)
#print "Sharpe ratio: " + str(pSharpeRatio)
#print "Portfolio cumulative total return: " + str(pCumulativeTotRet)