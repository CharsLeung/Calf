# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/4/24 16:51
"""
import time
import datetime as dt
import pytz
from pytz import utc

from Calf.utils import trading


class CalfDateTime:

    @classmethod
    def now(cls, tz=None, offset=None):

        if tz == 'China/Shanghai':
            tz_sh = pytz.timezone('Asia/Shanghai')
            now = dt.datetime.now(tz=tz_sh) if offset is None else dt.datetime.now(tz=tz_sh) + offset
            return now.replace(tzinfo=None)
        if tz == 'China/HongKong':
            tz_hk = pytz.timezone('Asia/Hong_Kong')
            now = dt.datetime.now(tz=tz_hk) if offset is None else dt.datetime.now(tz=tz_hk) + offset
            return now.replace(tzinfo=None)
        if tz == 'US/Eastern':
            tz_us = pytz.timezone('US/Eastern')
            now = dt.datetime.now(tz=tz_us) if offset is None else dt.datetime.now(tz=tz_us) + offset
            return now.replace(tzinfo=None)
        if tz is None:
            return dt.datetime.now() if offset is None else dt.datetime.now() + offset

    @classmethod
    def trade_date(cls, datetime, market='China/Stock'):
        if market == 'China/Stock':
            tdy = dt.datetime(datetime.year, datetime.month, datetime.day)
            if trading.is_trade_day(tdy):
                open_am = dt.datetime(datetime.year, datetime.month, datetime.day, 9, 30)
                close_am = dt.datetime(datetime.year, datetime.month, datetime.day, 11, 30)
                open_pm = dt.datetime(datetime.year, datetime.month, datetime.day, 13)
                close_pm = dt.datetime(datetime.year, datetime.month, datetime.day, 15)
                if open_am <= datetime <= close_am or open_pm <= datetime < close_pm:
                    return True
                else:
                    return False
            else:
                return False
        if market == 'China/HongKong':
            pass

    @classmethod
    def open_date(cls, market='China/Stock'):
        if market == 'China/Stock':
            return dict(am=dt.timedelta(hours=9, minutes=30), pm=dt.timedelta(hours=13))
        if market == 'China/HongKong':
            return
        if market == 'US/Stock':
            n = CalfDateTime.now(tz='US/Eastern')
            n = n.strftime('%Y-%m-%d %H:%M:%S')
            n = time.strptime(n, "%Y-%m-%d %H:%M:%S")
            if bool(n.tm_isdst):
                # 夏令时
                return dict()


# print(CalfDateTime.now(tz='China/Shanghai'))
# print(dt.datetime.now() + dt.timedelta(minutes=-20))