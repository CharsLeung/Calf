# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2017/11/23 14:24
"""
import datetime
import pandas as pd
import numpy as np

from bson import ObjectId
from Calf.data import MODEL_TABLE, BaseModel
from Calf.base.query_str_analyzer import analyzer
from Calf.exception import MongoIOError, FileError, ExceptionInfo, \
    WarningMessage, SuccessMessage


class ModelData(object):
    """
    有关公共模型所有的IO（数据库、文件）将通过这个类实现.
    通用的IO方法
    """

    def __init__(self, location=None, dbname=None):
        self.location = location
        self.dbname = dbname
        pass

    # @classmethod
    def field(self, table_name, field_name, filter=None):
        """
        Query the value of a field in the database
        :param filter:
        :param table_name: the database's table name
        :param field_name: the table's field name
        :return: all values in database
        """
        try:
            return BaseModel(table_name, self.location,
                             self.dbname).distinct(field_name, filter)
        except Exception:
            raise MongoIOError('query the field raise a error')

    # @classmethod
    def max(self, table_name, field='_id', **kw):
        """
        找到满足kw条件的field列上的最大值
        :param table_name:
        :param field:
        :param kw:
        :return:
        """
        try:
            if not isinstance(field, str):
                raise TypeError('field must be an instance of str')
            cursor = BaseModel(table_name, self.location,
                               self.dbname).query(sql=kw, field={field: True})
            if cursor.count():
                d = pd.DataFrame(list(cursor))
                m = d.loc[:, [field]].max()[field]
            else:
                m = None
            cursor.close()
            return m
        except Exception as e:
            raise e

    # @classmethod
    def min(self, table_name, field='_id', **kw):
        """
        找到满足kw条件的field列上的最小值
        :param table_name:
        :param field:
        :param kw:
        :return:
        """
        try:
            if not isinstance(field, str):
                raise TypeError('field must be an instance of str')
            cursor = BaseModel(table_name, self.location,
                               self.dbname).query(sql=kw, field={field: True})
            if cursor.count():
                d = pd.DataFrame(list(cursor))
                m = d.loc[:, [field]].min()[field]
            else:
                m = None
            cursor.close()
            return m
        except Exception as e:
            raise e

    # @classmethod
    def insert_data(self, table_name, data, add_id=False):
        """
        一个简易的数据插入接口
        :param table_name:
        :param data:
        :param add_id:
        :return:
        """
        try:
            if add_id:
                data['_id'] = data.index.map(lambda x: ObjectId())
            if len(data):
                d = data.to_dict(orient='records')
                BaseModel(table_name, self.location,
                          self.dbname).insert_batch(d)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    def insert_one(self, table_name, data, add_id=False):
        """
        insert one record
        :param table_name:
        :param data: a dict
        :param add_id:
        :return:
        """
        try:
            if add_id:
                data['_id'] = ObjectId()
            BaseModel(table_name, self.location,
                      self.dbname).insert(data)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    def read_one(self, table_name, field=None, **kw):
        """
        有时候只需要读一条数据，没必要使用read_data，
        :param table_name:
        :param field:
        :param kw:
        :return: a dict or None
        """
        try:
            cursor = BaseModel(table_name, self.location,
                               self.dbname).query_one(kw, field)
        except Exception as e:
            ExceptionInfo(e)
        finally:
            return cursor

    # @classmethod
    def read_data(self, table_name, field=None, **kw):
        """
        一个简易的数据读取接口
        :param table_name:
        :param field:
        :param kw:
        :return:
        """
        try:
            cursor = BaseModel(table_name, self.location,
                               self.dbname).query(kw, field)
            data = pd.DataFrame()
            if cursor.count():
                data = pd.DataFrame(list(cursor))
        except Exception as e:
            ExceptionInfo(e)
        finally:
            cursor.close()
            return data

    def aggregate(self, table_name, pipeline):
        """
        
        :param table_name:
        :param pipeline:
        :return: 
        """
        try:
            cursor = BaseModel(table_name, self.location,
                               self.dbname).aggregate(pipeline)
            # data = pd.DataFrame()
            # if cursor.count():
            data = pd.DataFrame(list(cursor))

        except Exception as e:
            ExceptionInfo(e)

        finally:
            cursor.close()
            return data

    # @classmethod
    def update_data(self, table_name, condition, **kw):
        """
        按condition条件更新table_name表数据
        :param table_name:
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            r = BaseModel(table_name, self.location,
                          self.dbname).update_batch(condition, kw)
            return r
        except Exception as e:
            ExceptionInfo(e)
            raise MongoIOError('Failed with update by MongoDB')

    # @classmethod
    def remove_data(self, table_name, **kw):
        """
        删除数据
        :param table_name:
        :param kw:
        :return:
        """
        try:
            r = BaseModel(table_name, self.location,
                          self.dbname).remove(kw)
            return r
        except Exception:
            raise MongoIOError('Failed with delete data by MongoDB')

    # @classmethod
    def insert_trade_menu(self, menus):
        """
        记录日交易所获得的收益
        :param menus:
        :return:
        """
        try:
            if len(menus):
                d = menus.to_dict(orient='records')
                MODEL_TABLE(self.location, self.dbname,
                            'trademenu').insert_batch(d)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    # @classmethod
    # @deprecated()
    def read_trade_menu(self, model_from, start_date=None,
                        end_date=None, version=None, **kw):
        """
        读取模型收益数据，读取到的数据主要包括某种策略一个或一段时间所对应的收益
        :param model_from:
        :param start_date:
        :param end_date:
        :param version:
        :param kw:
        :return:
        """
        try:
            sql = {'model_from': model_from}
            if version is not None:
                sql['version'] = version
            if start_date is None and end_date is None:
                pass
            else:
                if start_date is not None and end_date is None:
                    date = analyzer("date >= {s}".format(s=start_date))
                elif end_date is not None and start_date is None:
                    date = analyzer("date <= {e}".format(e=end_date))
                else:
                    date = analyzer("date >= {s} and data <= {e}"
                                    .format(s=start_date, e=end_date))
                sql = dict(sql, **date)
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(self.location, self.dbname,
                                 'trademenu').query(sql)
            menus = list(cursor)
            if len(menus):
                menus = pd.DataFrame(menus)
                menus = menus.sort_values(['date'], ascending=True)
                menus = menus.reset_index(drop=True)
                menus.drop(['_id', 'classtype'], axis=1, inplace=True)
                return menus
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query trade menu from db raise a error')

    # @classmethod
    def insert_finance_index(self, fis):
        """
        保存模型回测过程中的一些财务指标
        :param fis:
        :return:
        """
        try:
            if len(fis):
                d = fis.to_dict(orient='records')
                MODEL_TABLE(self.location, self.dbname,
                            'financeindex').insert_batch(d)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    # @classmethod
    def read_finance_index(self, model_from, field=None, **kwargs):
        """
        读取模型回测的财务指标数据
        :return:
        """
        try:
            sql = {'model_from': model_from}
            sql = dict(sql, **kwargs)
            cursor = MODEL_TABLE(self.location, self.dbname,
                                 'financeindex').query(sql, field)
            if cursor.count():
                fis = pd.DataFrame(list(cursor))
                fis.drop(['_id', 'classtype'], axis=1, inplace=True)
                return fis
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query finance indicators from db raise a error')

    # @classmethod
    def insert_risk_pst(self, rps):
        """
        插入风险仓位数据
        :param rps: a DataFrame
        :return:
        """
        try:
            if len(rps):
                dit = []
                for i, row in rps.iterrows():
                    r = dict(row)
                    dit.append(r)
                # print(dit[0])
                MODEL_TABLE(self.location, self.dbname,
                            'risk_and_position').insert_batch(dit)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    # @classmethod
    def read_risk_pst(self, stock_code=None, date=None, **kw):
        """
        读取仓位数据
        :return:
        """
        try:
            sql = dict()
            if stock_code is not None:
                sql['stock_code'] = stock_code
            if date is not None:
                sql = dict(sql, **analyzer("date = {d}".format(d=date)))
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(self.location, self.dbname,
                                 'risk_and_position').query(sql)
            rps = list(cursor)
            if len(rps):
                rps = pd.DataFrame(rps)
                rps.drop(['_id', 'classtype'], axis=1, inplace=True)
                return rps
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query risk and position from db raise a error')

    # @classmethod
    def insert_risk(self, risks):
        """
        插入风险参数
        :param risks:
        :return:
        """
        try:
            if len(risks):
                dit = []
                for i, row in risks.iterrows():
                    r = dict(row)
                    dit.append(r)
                MODEL_TABLE(self.location, self.dbname,
                            'risk').insert_batch(dit)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    # @classmethod
    def read_risk(self, stock_code=None, date=None, **kw):
        """
        读取风险参数
        :param stock_code:
        :param date:
        :param kw:
        :return:
        """
        try:
            sql = dict()
            if stock_code is not None:
                sql['stock_code'] = stock_code
            if date is not None:
                sql = dict(sql, **analyzer("date = {d}".format(d=date)))
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(self.location, self.dbname,
                                 'risk').query(sql)
            rks = list(cursor)
            if len(rks):
                rks = pd.DataFrame(rks)
                rks.drop(['_id', 'classtype'], axis=1, inplace=True)
                return rks
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query risk from db raise a error')

    # @classmethod
    def insert_pst(self, pst):
        """
        插入仓位
        :param pst:
        :return:
        """
        try:
            if len(pst):
                dit = []
                for i, row in pst.iterrows():
                    r = dict(row)
                    dit.append(r)
                MODEL_TABLE(self.location, self.dbname,
                            'position').insert_batch(dit)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    # @classmethod
    def read_pst(self, stock_code=None, date=None, **kw):
        """
        读取仓位
        :param stock_code:
        :param date:
        :param kw:
        :return:
        """
        try:
            sql = dict()
            if stock_code is not None:
                sql['stock_code'] = stock_code
            if date is not None:
                sql = dict(sql, **analyzer("date = {d}".format(d=date)))
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(self.location, self.dbname,
                                 'position').query(sql)
            pst = list(cursor)
            if len(pst):
                pst = pd.DataFrame(pst)
                pst.drop(['_id', 'classtype'], axis=1, inplace=True)
                return pst
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query position from db raise a error')
