# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/1/29 10:52
"""
import datetime as dt
# import numba
import pandas as pd
import re
import numpy as np
from Calf.data import KLINE_MODEL_TABLE
from Calf.exception import MongoIOError, ExceptionInfo


class KlineData(object):
    """
    所有以K线描述的时间序列行数据的读取，插入，删除均通过这个类实现
    """
    location = None  # klinedata对象的目标数据库服务器位置，
    dbname = None  # klinedata对象的目标数据库名称

    # 关于数据库服务器的路径配置在 __init__.py中有说明

    def __init__(self, location=None, dbname=None):
        KlineData.location = location
        KlineData.dbname = dbname
        pass

    @classmethod
    def codes(cls, *code):
        return {'$in': list(code)}

    @classmethod
    def field(cls, table_name, field_name, filter=None):
        """
        Query the value of a field in the database
        :param filter: dict
        :param table_name: the database's table name
        :param field_name: the table's field name
        :return: all values in database
        """
        try:
            return KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                     table_name).distinct(field_name, filter)
        except Exception:
            raise MongoIOError('query the field raise a error')

    @classmethod
    def timedelta(cls, x):
        # 将min线的time转化成时间截以便合并时间
        return pd.Timedelta(hours=x // 100, minutes=x % 100)

    @classmethod
    def merge_time(cls, data):
        """
        merge the date and time to datetime
        :param data: must have columns of date and time
        :return:
        """
        # try:
        # deltas = pd.DataFrame([cls.timedelta(x) for x in data['time']],
        #  columns=['timedelta'])
        # data['date'] = pd.eval("data['date'] + deltas['timedelta']")
        dts = pd.DataFrame()
        dts['date'] = data.date.astype('str')
        dts['time'] = data.time.astype('str')
        dts['time'] = '000' + dts.time
        dts['time'] = dts.time.map(lambda t: t[-4:])
        dts['date'] = dts.date + " " + dts.time
        data['datetime'] = pd.to_datetime(dts.date, format='%Y-%m-%d %H%M')
        data['date'] = data.datetime.dt.normalize()
        return data
        # except Exception:
        #     raise Exception

    @classmethod
    def read_one(cls, code, date, kline, **kw):
        """
        读取某只代码的某个时间点的K线数据，这个功能在read_data中也可以完成，
        但是这里单独实现是为了更好的性能.
        :param code:
        :param date:
        :param kline:
        :return:返回的是一个字典{}
        """
        try:
            sql = dict(stock_code=code, date=date)
            sql = dict(sql, **kw)
            cursor = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                       kline).query_one(sql)
            return cursor
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def read_one_min(cls, code, date, kline, **kw):
        """
        读取某只代码的某个时间点的K线数据(限于日内)
        :param code:
        :param date:
        :param kline:
        :return:
        """
        try:
            d = dt.datetime(date.year, date.month, date.day)
            t = date.hour * 100 + date.minute
            sql = dict(stock_code=code, date=d, time=t)
            sql = dict(sql, **kw)
            cursor = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                       kline).query_one(sql)
            return cursor
        except Exception as e:
            ExceptionInfo(e)
            return None

    @classmethod
    def read_data(cls, code=None, start_date=None, end_date=None, kline=None,
                  axis=1, timemerge=False, field=None, **kw):
        """读取K线数据.
        读取所有以K线描述的数据，可能包括但不限于股票，外汇，期权期货等
        根据时间范围、代码、表名从数据库中读到某K线的数据
        读取出来的数据是按时间降序排列好的，这意味着时间越大，位置越靠前
        axis=1表示纵向读取数据，=0表示横向读取数据
        这里所谓的纵向是指以时间序列为主线，横向是以代码为主线.
        to query from BD and package to Pandas' DataFrame
        :param field:
        :param timemerge: merge data and time
        :param axis:
        :param code: query of code or codes
        :param start_date: the datetime of start
        :param end_date: the datetime of end
        :param kline: the category of kline, this kline must in models
        list on models' init.py
        :return: DataFrame of data, or a null df.
        """
        try:
            sql = dict()
            if axis == 1:
                # 纵向读取必须说明code、start_date、end_date
                if code is None or start_date is None or end_date is None:
                    raise MongoIOError('If you want to longitudinally read '
                                       'data, so you must get stock code'
                                       ' and start date and end data')
                else:
                    # 如需同时读取多个品种的数据时，传递code={'$in':[c1,c2,]}或者使用codes方法
                    # 某些证券的代码不叫stock_code,需要注意
                    if isinstance(code, str):
                        sql['stock_code'] = code
                    elif isinstance(code, list):
                        sql['stock_code'] = {'$in': code}
                    else:
                        raise TypeError("'code' must be str or list of str")
                    sql['date'] = {'$gte': start_date, '$lte': end_date}
            if axis == 0:
                # 横向读取数据必须说明start_date与end_date之一
                if start_date is None and end_date is None:
                    raise MongoIOError('If you want to laterally read data, '
                                       'so you must get start date or end date')
                else:
                    date = dict()
                    if start_date is not None and end_date is None:
                        date['date'] = {'$gte': start_date}
                    elif end_date is not None and start_date is None:
                        date['date'] = {'$lte': end_date}
                    else:
                        date['date'] = {'$gte': start_date, '$lte': end_date}
                    sql = dict(sql, **date)

            sql = dict(sql, **kw)
            if re.search('min', kline, re.I) is not None:
                # 在一些场景中日内通常会把date与time分开存储，这可能会涉及到合并操作
                # 默认是不会合并的，如果需要合并，需要显示传递timemerg=True
                cursor = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                           kline).query(sql, field)
                if cursor.count() > 0:
                    data = pd.DataFrame(list(cursor))
                    data = cls.merge_time(data) if timemerge else data
                    if axis == 1:
                        if 'datetime' in data.columns:
                            data = data.sort_values('datetime', ascending=False)
                        else:
                            data = data.sort_values('date', ascending=False)
                        data = data.reset_index(drop=True)
                    cursor.close()
                    return data
            else:
                cursor = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                           kline).query(sql, field)
                if cursor.count() > 0:
                    data = pd.DataFrame(list(cursor))
                    if axis == 1:
                        data = data.sort_values(['date'], ascending=False)
                        data = data.reset_index(drop=True)
                    cursor.close()
                    return data
            return pd.DataFrame()
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def insert_data(cls, kline, data):
        """
        插入K线数据
        :param kline:
        :param data: insert data
        :return:
        """
        try:
            if len(data):
                d = data.to_dict(orient='records')
                KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                  kline).insert_batch(d)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def update_data(cls, kline, condition, **kw):
        """
        按condition条件更新K线数据
        :param kline:
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            r = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                  kline).update_batch(condition, kw)
            return r
        except Exception:
            raise MongoIOError('Failed with update by MongoDB')

    @classmethod
    def remove_data(cls, kline, **kw):
        """
        删除K线数据
        :param kline:
        :param kw:
        :return:
        """
        try:
            KLINE_MODEL_TABLE(cls.location, cls.dbname, kline).remove(kw)
        except Exception:
            raise MongoIOError('Failed with delete data by MongoDB')

    @classmethod
    def insert_update_log(cls, kline, status, **kw):
        """
        插入基本K线数据更新的日志， 这个更新不同于修改，是指插入了某个周期的某个
        时点的Bar数据
        :param status:
        :param kline:
        :param kw:
        :return:
        """
        try:
            log = dict(kline=kline, status=status, date=dt.datetime.now())
            log = dict(log, **kw)
            KLINE_MODEL_TABLE(cls.location, cls.dbname,
                              'data_logs').insert(log)
        except Exception:
            raise MongoIOError('insert kline data update log to db raise a error')

    @classmethod
    def read_log(cls, kline=None, start_date=None, end_date=None, **kw):
        """
        读取基本K线数据更新日志
        :param end_date:
        :param start_date:
        :param kline:
        :param kw:
        :return:
        """
        try:
            sql = dict()
            if kline is not None:
                sql['kline'] = kline
            if start_date is None and end_date is None:
                pass
            else:
                if start_date is not None and end_date is None:
                    date = {'date': {'$gte': start_date}}
                elif end_date is not None and start_date is None:
                    date = {'date': {'$lte': end_date}}
                else:
                    date = {'date': {'$gte': start_date, '$lte': end_date}}
                sql = dict(sql, **date)
            sql = dict(sql, **kw)
            cursor = KLINE_MODEL_TABLE(cls.location, cls.dbname,
                                       'data_logs').query(sql)
            if cursor.count():
                lgs = pd.DataFrame(list(cursor))
                # lgs.drop('classtype', axis=1, inplace=True)
                lgs = lgs.sort_values(['date'], ascending=False)
                lgs = lgs.drop_duplicates(['kline'], keep='first')  # 保留最新的一条记录
                return lgs
            return pd.DataFrame()

        except Exception:
            raise MongoIOError('read kline data update log from db raise a error')
