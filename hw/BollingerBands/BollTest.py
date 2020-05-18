# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 11:10:11 2013

@author: Ben
"""

dataDF = pricesDF
ky = 'close'
sym = 'MSFT'
window = 20
windowMin = 20
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
bollBndsDF['stdLow2'] = rollMean.values - (rollStd.values * 2)   
bollBndsDF['stdHigh2'] = rollMean.values + (rollStd.values * 2)
aboveIdx = find(bollBndsDF[symLb] > bollBndsDF['stdHigh2'])
belowIdx = find(bollBndsDF[symLb] < bollBndsDF['stdLow2'])
bollBndsDF['bbVal'] = (bollBndsDF[symLb].values - rollMean.values) / rollStd.values  
bollBndsDF['bbIdx'][aboveIdx] = 1
bollBndsDF['bbIdx'][belowIdx] = -1