# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import time
import numpy as np

def simulate( start, end, symbols, allocations):
    #calculate daily returns of portfolio
    timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start, end, timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    #print("test")
    d_data = dict(zip(ls_keys, ldf_data))
    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0, :]
    na_portfolio_price = (allocations * na_normalized_price).sum(1)
    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_portfolio_price.copy()
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)
    # Plotting the plot of daily returns
    dev = na_rets.std()
    #if dev==0:
    #  print na_rets[:5]
    avg = na_rets.mean()
    cum_ret=(na_portfolio_price[-1])
    sharpe = avg/dev*(252**0.5)
    return dev, avg, sharpe, cum_ret

def bruteforce(start, end, symbols,d):
    max=0
    allocation=[0,0,0,0]
    for a in np.arange(0,1+d,d):
      for b in np.arange(0,1+d-a,d):
        for c in np.arange(0,1+d-a-b, d):
          if a+b+c>1:
            continue
          alloc=[a, b, c, 1-a-b-c]
          val=simulate(start, end, symbols, alloc)[2]
          if val>max:
              max=val
              allocation=alloc
    print("Best allocation is ", allocation, " and it returns a sharpe: ", max)

def gradual(start, end, symbols, d):
    allocation=np.array([0.25, 0.25, 0.25, 0.25])
    var=np.array([[d,-d,0,0],
         [d,0,-d,0],
         [d,0,0,-d],
         [0,d,-d,0],
         [0,d,0,-d],
         [0,0,d,-d],
         [-d,0,d,0],
         [-d,0,0,d],
         [0,-d,d,0],
         [0,-d,0,d],
         [0,0,-d,d],
         [-d,d,0,0]])
    values={}
    max=-10
    delta=1
    r=1
    while ((delta>0) or (r<4)):
      allocations=(allocation+var)
      #print allocations
      curVal=np.array([])
      for alloc in allocations:
          if not ((alloc<=1).all() and (alloc>=0).all()):
             continue
          if str(alloc) not in values:
              val=simulate(start, end, symbols, alloc)[2]
              values[str(alloc)]=val
          else:
              val=values[str(alloc)]
          curVal=np.append(curVal, val)
          if val > max:
            delta=val-max
            r=0
            max=val
            allocation=alloc
          elif val==max:
            r+=1
            delta=0
            allocation=alloc
      if not ((allocation<=1).all() and (allocation>=0).all()):
         break
      if (curVal<max).all():
         #print (curVal, max)
         break
    #print values
    print (allocation, max)

if __name__ == '__main__':
    symbols = ["LTC-BTC", "ETH-BTC", "DASH-BTC", "DASH-BTC"]

    # Start and End date of the charts
    start = dt.datetime(2017, 1, 1)
    end = dt.datetime(2017, 12, 31)
    beg = time.time()
    bruteforce(start, end, symbols, 0.125)
    print("Time spent: ", time.time()-beg)
    beg = time.time()
    gradual(start, end, symbols, 0.015625)
    print("Time spent on gradual: ", time.time()-beg)
