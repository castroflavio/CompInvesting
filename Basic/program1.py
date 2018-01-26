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
import argparse

def datetimeNumpy(array):
    return dt.datetime(int(float(array[0])), int(float(array[1])), int(float(array[2])), 16)

if __name__ == '__main__':
    inputFile =  'values.csv' #sys.argv[1]
    symbol = '$SPX' #sys.argv[2]
    # Year, month, Symbol, Order, amount
    value = np.loadtxt(inputFile, delimiter=',', dtype='str' )
    dates = np.apply_along_axis( datetimeNumpy, axis=1, arr=value )
    start, end = min(dates), max(dates)
    ldt=du.getNYSEdays(start, end, dt.timedelta(hours=16))
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt, [symbol], ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    na_price = d_data['close']
    na_price['Custom'] = value[:,3]
    na_price=na_price.values.astype(float)
    na_normalized_price = na_price / na_price[0, :]

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt, na_normalized_price)
    plt.legend([symbol, 'Custom'])
    plt.ylabel('Normalized Close')
    plt.xlabel('Date')
    plt.savefig('normalized.pdf', format='pdf')

    na_rets = na_normalized_price.copy()
    tsu.returnize0(na_rets)
    # Plotting the plot of daily returns
    dev = na_rets.std(axis=0)
    #if dev==0:
    #  print na_rets[:5]
    avg = na_rets.mean(axis=0)
    cum_ret=(na_normalized_price[-1])
    sharpe = avg/dev*(252**0.5)
    print  "Sharpe ratio of Symbol:", sharpe[0]
    print  "Sharpe ratio of Fund:", sharpe[1]
    print  "\nTotal returns of Symbol: ", cum_ret[0]
    print  "Total returns of Fund: ", cum_ret[1]
    print "\nStandard deviation of Symbol:", dev[0]
    print "Standard deviation of Fund:", dev[1]
    print  "\nDaily returns of Symbol:", avg[0]
    print  "Daily returns of Fundl:", avg[1]
