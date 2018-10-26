# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/1/31 11:02
"""
from Calf.data import MongoIOError, MODEL_TABLE
import pandas as pd


class BaseData(object):
    """关于上市体系基本面的所有信息IO"""
    location = None
    dbname = None

    def __init__(self, location=None, dbname=None):
        BaseData.location = location
        BaseData.dbname = dbname
        pass

    @classmethod
    def read_RRADS(cls, **kwargs):
        """
        Regularly report the appointment disclosure schedule
        定期报告预约披露时间表
        :return:
        """
        try:
            sql = kwargs
            cursor = MODEL_TABLE(cls.location, cls.dbname, 'RRADS').query(sql)
            rds = list(cursor)
            if len(rds):
                rds = pd.DataFrame(rds)
                rds.drop('classtype', axis=1, inplace=True)
                # rds = rds.sort_values(['date'], ascending=False)
                return rds
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query orders data from db raise a error')

    @classmethod
    def update_date(cls, symbol, condition, **kw):
        """
        按condition条件更新数据
        :param symbol:
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            MODEL_TABLE(cls.location, cls.dbname, symbol).update_batch(condition, kw)
        except Exception:
            raise MongoIOError('Failed with update by MongoDB')


            # data = basedata.read_RRADS(stock_code={"$in": ["000001", "000002"]})
            # print(data)
