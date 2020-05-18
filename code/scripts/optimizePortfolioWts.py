import sys
sys.path.append("C:\\Users\\Ben\\Documents\\ci\\code\\comp_invest")
import CompInvestingTools as ci
##Optimize portfolio weights based on historic performance.
##For each time interval, determines the optimal allocation for
##mix of equities.
#Note:  Leave off SPY when reading hist prices becasue it gets appended

##Equity list and historic data.
symLst = ['QQQ','DIA','SPY']
dataLst = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
##Allocation step for optimiztion (percent).
allocationStep = 1
##Generat time intervals and subset for desired period.
dtBnds = ci.generateQuarterlyDT(1999,2013);
dtBnds = dtBnds[3:59]
#dtBnds = [[datetime.datetime(2013, 7, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)],
#[datetime.datetime(2013, 4, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)],
#[datetime.datetime(2012, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)],
#[datetime.datetime(2011, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)],
#[datetime.datetime(2008, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)], 
#[datetime.datetime(2006, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)], 
#[datetime.datetime(2003, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)],
#[datetime.datetime(1999, 10, 1, 0, 0), datetime.datetime(2013, 9, 30, 0, 0)]]
##Empty allocation matrix to populate with best allocation mix.
bestAllocs = np.zeros((len(dtBnds),3))
##Valid allocations, all combinations.
validAllocs = ci.generateValidAllocations(allocationStep,len(symLst))
##Loop through all time intervals.
for i in range(0,len(dtBnds)):
    tI = dtBnds[i]
    ##Grab historic data.  SPY is appended by this function.
    histPricesDF = ci.readHistDataToDF(tI[0],tI[1],['QQQ','DIA'],dataLst)
    ##Determine metrics for valid allocations.
    optPortAllsDF = ci.optimizePortAlloc(histPricesDF,validAllocs)
    ##Find maximum cumulative return, and populate bestAllocs matrix with values.
    rIdx = find(optPortAllsDF['cumTotRet'] == optPortAllsDF['cumTotRet'].max())
    bestAllocs[i,0] = optPortAllsDF.ix[rIdx[0]][0]
    bestAllocs[i,1] = optPortAllsDF.ix[rIdx[0]][1]
    bestAllocs[i,2] = optPortAllsDF.ix[rIdx[0]][2]
##Divide bestAllocs matrix into 4 intervals.  Weight intervals such that more
##recent history has a larger weight.
div = floor(bestAllocs.shape[0] / 4)
mn01 = bestAllocs[0:div].mean(axis=0)
mn02 = bestAllocs[div:(div * 2)].mean(axis=0)
mn03 = bestAllocs[(div * 2):(div * 3)].mean(axis=0)
mn04 = bestAllocs[(div * 3):bestAllocs.shape[0]].mean(axis=0)
wt01 = mn01 * 0.10
wt02 = mn02 * 0.15
wt03 = mn03 * 0.20
wt04 = mn04 * 0.55
finalWt = wt01 + wt02 + wt03 + wt04   
print "Optimal portfolio weights:"
for i in range(0,len(symLst)):
    print symLst[i] + ": " + str(finalWt[i])