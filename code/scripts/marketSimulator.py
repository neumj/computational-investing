import sys
sys.path.append("C:\\Users\\Ben\\Documents\\ci\\code\\comp_invest")
import CompInvestingTools as ci
##Market simulation.
ordersDF = ci.readCSVToDF('C:\\Users\\Ben\\Documents\\ci\\hw\\MarketTest','Test180_01.txt')
portPricesDF = ci.readHistAdjCloseToDFOrders(ordersDF)
portVal = ci.simulatePortfolio(ordersDF,portPricesDF,100000.0)
dfScalarMetrics, dfVectorMetrics = ci.calcBasicMetrics(portVal)