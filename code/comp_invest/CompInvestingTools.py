# -*- coding: utf-8 -*-
import sys
sys.path.append("C:\\Users\\Ben\Documents\\code\\python\\mjn_modules\\gen_mod")
import gen_tools as gen
import pandas as pd
import numpy as np
import datetime as dt
import math
import copy
import itertools
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

def readCSVToDF(filePath,fileName):
    """
    Read CSV file to Pandas dataframe.
    
    CSV file format:  Year,Month,Day,Symbol,Buy/Sell,Shares
    
    Returns: dfOrders 
    """
    #read CSV file to data frame
    print "Reading orders CSV file to data frame..."
    #ordersFl = "orders2.csv"
    #workPth = "C:\\Users\\Ben\Documents\\ci\\hw\\MarketSim\\quiz"
    dfOrders = pd.read_csv(filePath + '\\' + fileName, sep=',', index_col=None, header=None, usecols=range(6))
    dfOrders.columns = ['year','month','day','symbol','type','shares']
    #generate list of symbols
    
    #generate order dates and time series boundaries
    rawDates = []
    for r in dfOrders.iterrows():
        rawDate = dt.datetime(r[1]['year'],r[1]['month'],r[1]['day'],16,0,0)
        rawDates.append(rawDate)
    orderTSIdx = pd.to_datetime(rawDates)
    dfOrders = (dfOrders.set_index(orderTSIdx)).sort(axis=0)
    return dfOrders

def readHistAdjCloseToDFOrders(dfOrders):      
    """
    """
    ##read historical data        
    print "Reading historical data to data frame..."
    dtStart = (dfOrders.index.min()).to_pydatetime()
    dtEnd = (dfOrders.index.max()).to_pydatetime()
    ldt_timestamps = du.getNYSEdays(dtStart, dtEnd, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['close']
    symbols = list(set(dfOrders['symbol']))
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    #create historical prices data frame
    dfPrices = d_data['close']
    return dfPrices

def readHistActCloseToDFOrders(dfOrders):      
    """
    """
    ##read historical data        
    print "Reading historical data to data frame..."
    dtStart = (dfOrders.index.min()).to_pydatetime()
    dtEnd = (dfOrders.index.max()).to_pydatetime()
    ldt_timestamps = du.getNYSEdays(dtStart, dtEnd, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['actual_close']
    symbols = list(set(dfOrders['symbol']))
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    #create historical prices data frame
    dfPrices = d_data['actual_close']
    return dfPrices

def readHistIndexToDF(startDT,endDT,indexName,dataLst):
    dt_start = startDT
    dt_end = endDT
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(indexName)
    ls_symbols.append('SPY')

    ls_keys = dataLst 
    #['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    return d_data

def readHistDataToDF(startDT,endDT,symbolsLst,dataLst):
    dt_start = startDT
    dt_end = endDT
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = symbolsLst
    ls_symbols.append('SPY')

    ls_keys = dataLst
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
        
    return d_data

def simulatePortfolio(dfOrders,dfPrices,initCash):
    ##create equities data frame
    print "Creating equities data frame..."
    symbols = list(set(dfOrders['symbol']))
    dfEquities = pd.DataFrame(np.zeros((dfPrices.index.size,len(symbols))),index=dfPrices.index,columns=symbols)
    ##create cash data frame
    print "Creating cash data frame..."
    clabel = ['cash']
    dfCash = pd.DataFrame(np.zeros((dfPrices.index.size,1)),index=dfPrices.index,columns=clabel)
    dfCash['cash'][0] = initCash
    #create value data frame
    print "Creating equities value data frame..."
    clabel = ['value']
    dfValue = pd.DataFrame(np.zeros((dfPrices.index.size,1)),index=dfPrices.index,columns=clabel)

    #loop through orders and determine portfolio composition and cash
    print "Calculating daily portfolio positions and values..." 
    for t in dfOrders.index.unique():
        tOrder = dfOrders[t:t]
        #print tOrder
        for i in range(0,(tOrder.shape[0])):
            if tOrder['type'][i] == "Buy":
                print tOrder['type'][i] + " " + str(tOrder['shares'][i]) + " " + tOrder['symbol'][i] + " @ " + str(dfPrices[tOrder['symbol'][i]][tOrder.index[i]])
                numHold = dfEquities[tOrder['symbol'][i]][tOrder.index[i]]
                newTot = numHold + tOrder['shares'][i]
                dfEquities[tOrder['symbol'][i]][tOrder.index[i]:dfEquities.index.max()] = newTot
                totCost = (dfPrices[tOrder['symbol'][i]][tOrder.index[i]] * tOrder['shares'][i]) * -1
                curCash = dfCash['cash'][tOrder.index[i]]
                newCash = curCash + totCost
                dfCash['cash'][tOrder.index[i]:dfCash.index.max()] = newCash
                #print newCash
            elif tOrder['type'][i] == "Sell":
                print tOrder['type'][i] + " " + str(tOrder['shares'][i]) + " " + tOrder['symbol'][i] + " @ " + str(dfPrices[tOrder['symbol'][i]][tOrder.index[i]])
                numHold = dfEquities[tOrder['symbol'][i]][tOrder.index[i]]
                newTot = numHold - tOrder['shares'][i]
                dfEquities[tOrder['symbol'][i]][tOrder.index[i]:dfEquities.index.max()] = newTot                 
                totCost = dfPrices[tOrder['symbol'][i]][tOrder.index[i]] * tOrder['shares'][i]
                curCash = dfCash['cash'][tOrder.index[i]]
                newCash = curCash + totCost
                dfCash['cash'][tOrder.index[i]:dfCash.index.max()] = newCash
                #print newCash
    
    #determine equity portfolio value
    valueArray = dfPrices.values * dfEquities.values
    dfValue['value'] = valueArray.sum(axis=1)
    #determine total portfolio value
    clabel = ['totValue']
    dfTotalVal = pd.DataFrame(np.zeros((dfPrices.index.size,1)),index=dfPrices.index,columns=clabel)
    dfTotalVal['totValue'] = dfValue['value'].values + dfCash['cash'].values
    #combine for final date frame
    clabel = ['cashValue','equityValue','totalValue']
    dfPortVal = pd.DataFrame(np.zeros((dfPrices.index.size,3)),index=dfPrices.index,columns=clabel)
    dfPortVal['cashValue'] = dfCash['cash']
    dfPortVal['equityValue'] = dfValue['value']
    dfPortVal['totalValue'] = dfTotalVal['totValue']
    return dfPortVal

def calcBasicMetrics(dfPortfolio):
    #calculate metrics
    totRet = dfPortfolio['totalValue'][dfPortfolio['totalValue'].size - 1] / dfPortfolio['totalValue'][0]
    normalizedPrice = dfPortfolio['totalValue'] / dfPortfolio['totalValue'][0]
    dailyReturn = tsu.returnize0(normalizedPrice)
    portVolatility = dailyReturn.std()
    portAveDalRet = dailyReturn.mean()
    sharpeRatio = math.sqrt(dfPortfolio.index.size) * (portAveDalRet / portVolatility).tolist() 
    sharpeRatio252 = math.sqrt(252) * (portAveDalRet / portVolatility).tolist() 
    clabel = ['totReturn','volatility','aveDailyReturn','sharpeRatio','sharpeRatio252']
    dfScalarMetrics = pd.DataFrame(np.zeros((1,5)),columns=clabel)
    dfScalarMetrics['totReturn'] = totRet
    dfScalarMetrics['volatility'] = portVolatility
    dfScalarMetrics['aveDailyReturn'] = portAveDalRet
    dfScalarMetrics['sharpeRatio'] = sharpeRatio
    dfScalarMetrics['sharpeRatio252'] = sharpeRatio252
    clabel = ['normalizedValue','dailyReturn']
    dfVectorMetrics = pd.DataFrame(np.zeros((dfPortfolio.index.size,2)),index=dfPortfolio.index,columns=clabel)
    dfVectorMetrics['normalizedValue'] = normalizedPrice
    dfVectorMetrics['dailyReturn'] = dailyReturn
    return dfScalarMetrics, dfVectorMetrics
    
def eventStudyToTrades(dfEventStudy,holdDays,fileName,filePath):
    logFile = filePath + "\\" + fileName
    lgCnt = 0
    for ky in dfEventStudy.keys():
        if len(dfEventStudy[ky][dfEventStudy[ky] == 1]) > 0:
            print ky
            eventsIdx = find(dfEventStudy[ky] == 1)
            for i in range(0,(eventsIdx.size)):
                shares = 100
                buyDtStr = str(dfEventStudy[ky].index[eventsIdx[i]])
                print buyDtStr
                yearInt = int(buyDtStr.split(' ')[0].split('-')[0])
                monInt = int(buyDtStr.split(' ')[0].split('-')[1])
                dayInt = int(buyDtStr.split(' ')[0].split('-')[2])
                logStr =  str(yearInt) + "," + str(monInt) + "," + str(dayInt) + "," + ky + "," + "Buy" + "," + str(shares)  + "\n"
                gen.write_log(logFile,logStr)
                buyTS = dfEventStudy[ky].index[eventsIdx[i]]
                sellIdx = (find(dfEventStudy.index == buyTS) + holdDays) - 1
                print sellIdx
                if sellIdx >= len(dfEventStudy.index):
                    print "Need Last Day"
                    sellIdx = (len(dfEventStudy.index)) - 1
                print "Not last day"
                sellDtStr = str(dfEventStudy[ky].index[int(sellIdx)])
                print sellDtStr
                yearInt = int(sellDtStr.split(' ')[0].split('-')[0])
                monInt = int(sellDtStr.split(' ')[0].split('-')[1])
                dayInt = int(sellDtStr.split(' ')[0].split('-')[2])
                logStr =  str(yearInt) + "," + str(monInt) + "," + str(dayInt) + "," + ky + "," + "Sell" + "," + str(shares)  + "\n"
                gen.write_log(logFile,logStr)
                lgCnt = lgCnt + 2
                print lgCnt

def calcBollingerBands(dataDF,ky,sym,window,windowMin,stdFact):
    rollMean = pd.rolling_mean(dataDF[ky][sym],window,windowMin)
    rollStd = pd.rolling_std(dataDF[ky][sym],window,windowMin)
    symLb = sym + ky
    kyLb = 'mean' + str(window)
    labels = [symLb,kyLb,'stdLow1','stdHigh1','stdLow2','stdHigh2','bbIdx','bbVal']
    bollBndsDF = pd.DataFrame(np.zeros((dataDF[ky].index.size,8)),index=dataDF[ky].index,columns=labels)
    bollBndsDF[symLb] = dataDF[ky][sym].values 
    bollBndsDF[kyLb] = rollMean.values
    bollBndsDF['stdLow1'] = rollMean.values - rollStd.values   
    bollBndsDF['stdHigh1'] = rollMean.values + rollStd.values
    bollBndsDF['stdLow2'] = rollMean.values - (rollStd.values * stdFact)   
    bollBndsDF['stdHigh2'] = rollMean.values + (rollStd.values * stdFact)
    aboveIdx = find(bollBndsDF[symLb] > bollBndsDF['stdHigh2'])
    belowIdx = find(bollBndsDF[symLb] < bollBndsDF['stdLow2'])
    bollBndsDF['bbVal'] = (bollBndsDF[symLb].values - rollMean.values) / rollStd.values  
    bollBndsDF['bbIdx'][aboveIdx] = 1
    bollBndsDF['bbIdx'][belowIdx] = -1
    return bollBndsDF

def findBBEvents(bolBandsDF,bValTod,bValYest,bValMarTod):
    print "Finding Events..."
    ts_market = bolBandsDF['SPY']
    # Creating an empty dataframe
    df_events = copy.deepcopy(bolBandsDF)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = bolBandsDF.index

    for sym in bolBandsDF.keys():
        for i in range(1, len(ldt_timestamps)):
            bbValToday = bolBandsDF[sym].ix[ldt_timestamps[i]]
            bbValYest = bolBandsDF[sym].ix[ldt_timestamps[i - 1]]
            marketbbValToday = ts_market.ix[ldt_timestamps[i]]
            #marketbbValYest = ts_market.ix[ldt_timestamps[i - 1]]

            if bbValToday < bValTod and bbValYest >= bValYest and marketbbValToday >= bValMarTod:
                df_events[sym].ix[ldt_timestamps[i]] = 1
    print "Done."
    return df_events
    
def optimizePortAlloc(histDataDF,validAllocs):
    symLab =[]
    metLab = ['portVolatility', 'portAveDalRet', 'sharpeRatio', 'cumTotRet']
    dfLab = []
    for ky in histDataDF['close'].keys():
        symLab.append(ky)
        dfLab.append(ky)
    for mL in metLab: 
        dfLab.append(mL) 
    portAllocsDF = pd.DataFrame(np.zeros((len(validAllocs),len(dfLab))),columns=dfLab)
    for i in range(0,len(validAllocs)):
        for j in range(0,len(symLab)):
            portAllocsDF[symLab[j]][i] = validAllocs[i][j]     
        #turn allocation wt list into array
        assetAlloc = validAllocs[i]
        arrAlloc = np.array(assetAlloc)
        allocIdx = arrAlloc != 0
        na_price = histDataDF['close'].values
        normalizedPrice = na_price / na_price[0, :]
        wtPrice = normalizedPrice[:,allocIdx] * arrAlloc[allocIdx]
        wtPriceSum = wtPrice.sum(axis = 1)
        cumTotRet = wtPriceSum[wtPriceSum.size - 1] / wtPriceSum[0]
        dailyReturn = tsu.returnize0(wtPriceSum)
        portVolatility = dailyReturn.std()
        portAveDalRet = dailyReturn.mean()
        sharpeRatio = math.sqrt(252) * (portAveDalRet / portVolatility).tolist()     
        portAllocsDF['portVolatility'][i] = float(portVolatility)
        portAllocsDF['portAveDalRet'][i] = float(portAveDalRet)    
        portAllocsDF['sharpeRatio'][i] = float(sharpeRatio)
        portAllocsDF['cumTotRet'][i] = float(cumTotRet)
    return portAllocsDF    
    
def generateValidAllocations(percentStep,numSymbols):
    validAllocs = []
    stepVal = int(100 / percentStep)
    for i in itertools.product(range(stepVal + 1), repeat=numSymbols):
        if sum(i) == stepVal:
            alloc = map(lambda x: float(x) / stepVal, i)
            validAllocs.append(alloc)  
    return validAllocs    

def generateAnnualDT(beginYr,endYr):
    yrs = range(beginYr,endYr,1)
    dtBnds = []
    for yr in yrs:
        bgMn = [dt.datetime(yr,1,1),dt.datetime(yr,12,31)]
        dtBnds.append(bgMn)
    return dtBnds

def generateSemiAnnualDT(beginYr,endYr):
    yrs = range(beginYr,endYr,1)
    dtBnds = []
    for yr in yrs:
        bgMn = [dt.datetime(yr,1,1),dt.datetime(yr,6,30)]
        enMn = [dt.datetime(yr,7,1),dt.datetime(yr,12,31)]
        dtBnds.append(bgMn)
        dtBnds.append(enMn)
    return dtBnds

def generateQuarterlyDT(beginYr,endYr):
    yrs = range(beginYr,endYr,1)
    dtBnds = []
    for yr in yrs:
        q1 = [dt.datetime(yr,1,1),dt.datetime(yr,3,31)]
        q2 = [dt.datetime(yr,4,1),dt.datetime(yr,6,30)]
        q3 = [dt.datetime(yr,7,1),dt.datetime(yr,9,30)]
        q4 = [dt.datetime(yr,10,1),dt.datetime(yr,12,31)]
        dtBnds.append(q1)
        dtBnds.append(q2)
        dtBnds.append(q3)
        dtBnds.append(q4)
    return dtBnds

    


