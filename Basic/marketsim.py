# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import time, sys
import numpy as np

def datetimeNumpy(year, month, day):
    return dt.datetime(int(year), int(month), int(day), 16)

inputFile =  sys.argv[2]
outputFile = sys.argv[3]
cash = int(sys.argv[1])
# Year, month, Symbol, Order, amount
orders = pd.read_csv(inputFile, delimiter=',',
                     usecols = range(6),
                     names = ['year', 'month', 'day', 'equity', 'order', 'shares'],
                     header = None,
                     skipinitialspace = True,
                     parse_dates = {'date' : ['year', 'month', 'day']},
                     date_parser=datetimeNumpy)

orders.sort(['date'], ascending = [1], inplace = True)
orders.index = range(len(orders))

symbols = orders['equity'].unique()
symbols = np.append(symbols,['cash'])
start, end = orders['date'][0], orders['date'][len(orders)-1]
ldt=du.getNYSEdays(start, end, dt.timedelta(hours=16))
c_dataobj = da.DataAccess('Yahoo')
ldf_data = c_dataobj.get_data(ldt, symbols, ['close'])
d_data = dict(zip(['close'], ldf_data))
d_data['close'] = d_data['close'].fillna(method='ffill')
d_data['close'] = d_data['close'].fillna(method='bfill')
d_data['close'] = d_data['close'].fillna(1.0)
na_prices = d_data['close'] #
own = na_prices.copy()*0 #
def addOrder(matrix, symbol, operation, shares, date):
    curr = matrix[symbol][date]
    global cash
    if operation == 'Buy':
        matrix[symbol][date:]= (curr + float(shares))
        cash -= float(shares)*float(na_prices[symbol][start])
    if operation == 'Sell':
        matrix[symbol][date:]= (curr - float(shares))
        cash += float(shares)*float(na_prices[symbol][start])
    matrix['cash'][date:]=cash
for i,order in enumerate(orders.values):
    start = order[0]
    addOrder(own, order[1], order[2], order[3], start)
fval = pd.DataFrame( (own.values*na_prices.values).sum(axis=1), index=own.index )
#print fval
dailyVal=[]
for i,row in enumerate(fval.values):
    date=ldt[i]
    dailyVal.append([int(date.year), int(date.month), int(date.day),row])
np.savetxt(outputFile, dailyVal, delimiter=',', fmt='%s')
