# -*- coding: utf-8 -*-
"""
Created on Tue Oct 08 11:23:06 2013

@author: Ben
"""
import sys
sys.path.append("C:\\Users\\Ben\Documents\\code\\pyhton\\mjn_modules\\gen_mod")
import gen_tools as gen


def EventStudyToTrades(dfEventStudy,holdDays,fileName,filePath):
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
                if sellIdx > len(dfEventStudy.index):
                    sellIdx = (len(dfEventStudy.index)) - 1
                sellDtStr = str(dfEventStudy[ky].index[int(sellIdx)])
                print sellDtStr
                yearInt = int(sellDtStr.split(' ')[0].split('-')[0])
                monInt = int(sellDtStr.split(' ')[0].split('-')[1])
                dayInt = int(sellDtStr.split(' ')[0].split('-')[2])
                logStr =  str(yearInt) + "," + str(monInt) + "," + str(dayInt) + "," + ky + "," + "Sell" + "," + str(shares)  + "\n"
                gen.write_log(logFile,logStr)
                lgCnt = lgCnt + 2
                print lgCnt
    
fileName = "orders2012_72.txt"
filePath = "C:\\Users\\Ben\\Documents\\ci\\hw\\EventsToTrades"
EventStudyToTrades(df_events,6,fileName,filePath)
#2011,1,10,AAPL,Buy,1500

