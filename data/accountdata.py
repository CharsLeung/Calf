# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/4/19 14:57
"""
import pandas as pd

from Calf.data import MODEL_TABLE
from Calf.exception import ExceptionInfo, MongoIOError


class AccountData(object):
    """
    交易账户数据，包括真实账户与模拟账户
    """
    location = None
    dbname = None

    def __init__(self, location=None, dbname=None):
        AccountData.location = location
        AccountData.dbname = dbname
        pass

    @classmethod
    def read_account_info(cls, **kw):
        """
        读取账户-订阅
        :return:
        """
        try:
            cursor = MODEL_TABLE(cls.location, cls.dbname, 'accounts').query(kw)
            if cursor.count():
                data = pd.DataFrame(list(cursor))
                return data
            else:
                return pd.DataFrame()
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()
        pass

    @classmethod
    def insert_account_info(cls, acts):
        """
        添加账户-订阅
        :return:
        """
        try:
            col = ['account', 'initial_balance', 'balance', 'date', 'subscription', 'model_scale', 'role']
            if set(col) <= set(acts.columns):
                d = acts.to_dict(orient='records')
                MODEL_TABLE(cls.location, cls.dbname, 'accounts').insert_batch(d)
            else:
                raise Exception('lost must field')

        except Exception:
            raise MongoIOError('Failed with insert data by DB')
        pass

    @classmethod
    def update_account_info(cls):
        pass