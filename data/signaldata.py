# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/12/25 13:39
"""
import pandas as pd

from Calf.data import MODEL_TABLE
from Calf.exception import ExceptionInfo, MongoIOError


class SignalData(object):
    """信号IO"""
    location = None
    dbname = None

    def __init__(self, location=None, dbname=None):
        SignalData.location = location
        SignalData.dbname = dbname
        pass

    # 将min线的time转化成时间截以便合并时间
    @classmethod
    def timedelta(cls, x):
        return pd.Timedelta(hours=x // 100, minutes=x % 100)

    @classmethod
    def merge_time(cls, data):
        """
        merge the date and time to datetime
        :param data: must have columns of date and time
        :return:
        """
        # try:
        deltas = pd.DataFrame([cls.timedelta(x) for x in data['time']],
                              columns=['timedelta'])
        data['date'] = data['date'] + deltas['timedelta']
        return data
        # except Exception:
        #     ExceptionInfo()
        #     return data

    @classmethod
    def insert_signals(cls, signals):
        """
        The signal points of buying insert to DB
        :param signals: a df of signal which come from someone models,
        and the df must have columns of
        stock_code,date,buy_price,model_from
        :return:
        """
        try:
            if len(signals):
                # 信号表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                col = ['open_date', 'open_price', 'confidence',
                       'type', 'version', 'model_from']
                if set(col) <= set(signals.columns):
                    d = signals.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                'signals').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by DB')

    @classmethod
    def read_signals(cls, model_from=None, field=None, **kw):
        """
        query signals from DB
        :param model_from:
        :param field:属性域
        :return:
        """
        try:
            sql = dict()
            if model_from is not None:
                sql = {"model_from": model_from}
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'signals').query(sql, field)
            if cursor.count():
                data = pd.DataFrame(list(cursor))
                # data['date'] = pd.to_datetime(data.date)
                # data = cls.merge_time(data)
                data = data.sort_values(['open_date'], ascending=False)
                data = data.reset_index(drop=True)
                # data.drop(['_id', 'classtype'], axis=1, inplace=True)
                # data = data.drop_duplicates(['stock_code', 'date', 'time'])
                # data.stock_code.astype('int')
                cursor.close()
                return data
            else:
                cursor.close()
                return pd.DataFrame([])
        except Exception:
            raise MongoIOError('query signals from db raise a error')

    @classmethod
    def update_signals(cls, condition, **kw):
        """
        按condition条件更新K线数据
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            r = MODEL_TABLE(cls.location, cls.dbname,
                            'signals').update_batch(condition, kw)
            return r.raw_result
        except Exception:
            raise MongoIOError('Failed with update by MongoDB')

    @classmethod
    def remove_signals(cls, model_from, **kw):
        """
        根据条件删除signals表当中的信号，其实只是将信号从signals转移到了信号历史
        表当中
        :param model_from:
        :param kw:
        :return:
        """
        try:
            sql = {'model_from': model_from}
            sql = dict(sql, **kw)
            r = MODEL_TABLE(cls.location, cls.dbname, 'signals').remove(sql)
            return r
        except Exception:
            raise MongoIOError('Failed with removing data ')

    @classmethod
    def insert_his_signals(cls, pst):
        """
        把通过模型收益计算方法得到的交易清单存入数据库
        :param pst:
        :return:
        """
        try:
            if len(pst):
                # 信号历史表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                col = ['open_date', 'open_price', 'close_date', 'close_price',
                       'type', 'reason', 'profit', 'model_from']
                if set(col) <= set(pst.columns):
                    d = pst.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                'signals_his').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def read_his_signals(cls, field=None, **kw):
        """
        读取持有过的股票数据，包括在回测中买入过的股票
        :param kw:
        :return:
        """
        try:
            sql = kw
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'signals_his').query(sql, field)
            if cursor.count():
                data = pd.DataFrame(list(cursor))
                return data
            else:
                return pd.DataFrame([])
        except Exception:
            raise MongoIOError('query positions from db raise a error')
