# -*- coding: utf-8 -*-
"""
Created on Wed Oct 02 13:41:14 2013

@author: Ben
"""
import pandas as pd
import numpy as np
import datetime as dt
import math
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

def readCSVToDF(filePath,fileName):
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

def readHistoricalCloseToDF(dfOrders):      
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

dfOrders = readCSVToDF("C:\\Users\\Ben\Documents\\ci\\hw\\EventsToTrades","orders2012_72.txt")
dfPrices = readHistoricalCloseToDF(dfOrders)
dfPortfolio = simulatePortfolio(dfOrders,dfPrices,50000.0)
dfScalarMetrics, dfVectorMetrics = calcBasicMetrics(dfPortfolio)