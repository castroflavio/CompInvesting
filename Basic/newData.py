import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

end = dt.datetime(2017, 8, 30)
start = dt.datetime(2017, 7, 30)
timeofday = dt.timedelta(hours=16)
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
c_dataobj = da.DataAccess('Yahoo')
ldt_timestamps = du.getNYSEdays(start, end, timeofday)
ldf_data = c_dataobj.get_data(ldt_timestamps, ['ETH','BTC'], ls_keys, verbose=True)
print ldf_data
