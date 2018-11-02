# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/5/22 9:28
"""
import pandas as pd
import datetime as dt
from Calf.data import BaseModel
from Calf.exception import MongoIOError, ExceptionInfo


class TickData(object):
    """
    tick数据IO
    """
    location = None
    dbname = None

    def __init__(self, location=None, dbname=None):
        TickData.location = location
        TickData.dbname = dbname
        pass

    @classmethod
    def merge_time(cls, data):
        """
        merge the date and time to datetime
        :param data: must have columns of date and time
        :return:
        """
        try:
            # deltas = pd.DataFrame([cls.timedelta(x) for x in data['time']], columns=['timedelta'])
            # data['date'] = pd.eval("data['date'] + deltas['timedelta']")
            dts = pd.DataFrame()
            dts['date'] = data.date.astype('str')
            dts['time'] = data.time.astype('str')
            dts['time'] = '000' + dts.time
            dts['time'] = dts.time.map(lambda t: t[-4:])
            dts['date'] = dts.date + " " + dts.time
            data['date'] = pd.to_datetime(dts.date, format='%Y-%m-%d %H%M')
            return data
        except Exception:
            raise Exception

    @classmethod
    def read_data(cls, code, start_date, end_date, field=None, timemerge=False, **kw):
        """

        :param code:
        :param start_date:
        :param end_date:
        :param timemerge:
        :return:
        """
        try:
            sql = dict(stock_code=code, date={'$gte': start_date, '$lte': end_date})
            sql = dict(sql, **kw)
            cursor = BaseModel('kline_tick', cls.location, cls.dbname).query(sql, field)
            if cursor.count():
                data = pd.DataFrame(list(cursor))
                data = cls.merge_time(data) if timemerge else data
                cursor.close()
                return data
            else:
                cursor.close()
                return pd.DataFrame()
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def lasted_ticker(cls, code, date, table_name='ticker'):
        try:
            if isinstance(code, str):
                sc = code
            elif isinstance(code, list):
                sc = {'$in': code}
            else:
                raise TypeError("'code' must be str or list of str")
            if isinstance(date, dt.datetime):
                d = dt.datetime(date.year, date.month, date.day)
                t = {'$gte': date - dt.timedelta(minutes=1), '$lte': date}
                pass
            else:
                raise TypeError("this 'date' must be datetime")
            cursor = BaseModel(table_name, cls.location, cls.dbname).aggregate([
                {'$match': {'stock_code': sc, 'date': d}},
                {'$match': {'datetime': t}}
            ])
            data = pd.DataFrame(list(cursor))
            if len(data):
                data = data.sort_values(['stock_code', 'datetime'], ascending=False)
                data = data.drop_duplicates(['stock_code'], keep='first')
                data = data.reset_index(drop=True)
            cursor.close()
            return data
            pass
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()
