import sys
import copy
import numpy as np
import datetime as dt
import QSTK.qstkstudy.EventProfiler as ep
sys.path.append("C:\\Users\\Ben\\Documents\\ci\\code\\comp_invest")
import CompInvestingTools as ci
##Market simulation based on bollinger band events.    
pricesDF = ci.readHistIndexToDF(dt.datetime(2008,1,1),dt.datetime(2009,12,31),'SP5002012',['close','actual_close'])
bbandsDF = copy.deepcopy(pricesDF['close'])
bbandsDF = bbandsDF * np.NAN
for sym in bbandsDF.keys():
    calcBB = ci.calcBollingerBands(pricesDF,'close',sym,20,20,1)
    bbandsDF[sym] = calcBB['bbVal']
bbEventsDF = ci.findBBEvents(bbandsDF,-2.0,-2.0,1.4)
ep.eventprofiler(bbEventsDF, pricesDF, i_lookback=20, i_lookforward=20,
                s_filename='bbEvents02.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
ci.eventStudyToTrades(bbEventsDF,6,'bbEventTrades.txt','C:\\Users\\Ben\\Documents\\ci\\hw\\BackTestSim')
ordersDF = ci.readCSVToDF('C:\\Users\\Ben\\Documents\\ci\\hw\\MarketTest','MarketTrades.txt')
portPricesDF = ci.readHistCloseToDFOrders(ordersDF)
portVal = ci.simulatePortfolio(ordersDF,portPricesDF,100000.0)
dfScalarMetrics, dfVectorMetrics = ci.calcBasicMetrics(portVal)