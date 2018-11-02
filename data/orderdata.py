# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/1/4 14:09
"""
from Calf.data import MODEL_TABLE
from Calf.exception import MongoIOError, ExceptionInfo
import pandas as pd
import datetime


class OrderData(object):
    """
    关于交易订单的数据交互,只能用于真实的交易
    """
    location = None
    dbname = None

    def __init__(self, location=None, dbname=None):
        OrderData.location = location
        OrderData.dbname = dbname
        pass

    @classmethod
    def timedelta(cls, x):
        return pd.Timedelta(hours=x // 100, minutes=x % 100)

    @classmethod
    def merge_time(cls, data, date='date', time='time'):
        """
        merge the date and time to datetime
        :param time:
        :param date:
        :param data: must have columns of date and time
        :return:
        """
        # try:
        deltas = pd.DataFrame([cls.timedelta(x) for x in data[time]], columns=['timedelta'])
        data[date] = data[date] + deltas['timedelta']
        return data
        # except Exception:
        #     ExceptionInfo()
        #     return data

    @classmethod
    def read_account_info(cls, model_from, field=None, **kw):
        """
        读取现有的账户信息
        :return:
        """
        try:
            sql = {'model_from': model_from}
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'asset').query(sql, field)
            if cursor.count():
                ai = pd.DataFrame(list(cursor))
                ai.drop(['classtype'], axis=1, inplace=True)
                ai = ai.sort_values(['date'], ascending=False)
                ai = ai.drop_duplicates(['client_no'], keep='first')
                cursor.close()
                return ai
            cursor.close()
            return pd.DataFrame()
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def insert_client_info(cls, client):
        """
        插入订阅账户信息
        :param client:
        :return:
        """
        try:
            if len(client):
                # 客户信息表必须包含的字段，缺省的填0
                col = ['client_no', 'model_from', 'update', 'status', 'Rr']
                if set(col) <= set(client.columns):
                    d = client.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                'clients').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def read_client_info(cls, model_from, field=None, **kw):
        """

        :param model_from:
        :return:
        """
        try:
            sql = {'model_from': model_from}
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'clients').query(sql, field)
            if cursor.count():
                clis = pd.DataFrame(list(cursor))
                cursor.close()
                return clis
            cursor.close()
            return pd.DataFrame()
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def update_client_info(cls, condition, **kw):
        """
        按condition条件更新K订单数据
        :param table_name:
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            MODEL_TABLE(cls.location, cls.dbname,
                        'clients').update_batch(condition, kw)
        except Exception:
            raise MongoIOError('Failed with update by MongoDB')

    @classmethod
    def open(cls, orders):
        """
        插入开仓数据
        :param orders:
        :return:
        """
        try:
            if len(orders):
                # 订单表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                col = ['open_date', 'open_price', 'type', 'model_from', 'Rr',
                       'exp_open_vol', 'client_no', 'status']
                if set(col) <= set(orders.columns):
                    d = orders.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                'orders').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def order_send(cls, orders):
        """
        插入需要购买的数据
        :param orders: a DataFrame
        :return:
        """
        try:
            if len(orders):
                # 订单表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                # 'open_date', 'open_price', 'confidence', 'type', 'version', 'model_from'
                col = []
                if set(col) <= set(orders.columns):
                    d = orders.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname, 'orders').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def insert_orders(cls, orders, table_name='orders'):
        """
        插入订单数据，默认插入到orders表中，这个表可能会参与实际交易。
        也可以插入到orders_simulated表中，这只是用于模拟交易的
        :param orders:
        :param table_name:
        :return:
        """
        try:
            if len(orders):
                # 订单表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                col = ['open_date', 'open_price', 'confidence', 'type',
                       'version', 'model_from', 'status']
                if set(col) <= set(orders.columns):
                    d = orders.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                table_name).insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def read_orders_(cls, model_from=None, **kw):
        """
        读取持仓的数据,一个特殊的实现
        :param model_from:
        :param kw:
        :return:
        """
        try:
            sql = dict()
            if model_from is not None:
                sql = {'model_from': model_from}
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'orders').query(sql)
            if cursor.count():
                ods = pd.DataFrame(list(cursor))
                ods = cls.merge_time(ods, 'date', 'time')
                ods = cls.merge_time(ods, 'max_pst_date', 'pst_time')
                ods.drop(['_id', 'classtype'], axis=1, inplace=True)
                return ods
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query orders data from db raise a error')

    @classmethod
    def read_orders(cls, table_name='orders', field=None, **kw):
        """
        读取持仓信息，可以读取包括orders,orders_simulated,orders_his三个表的数据
        :param table_name:
        :param field:
        :param kw:
        :return:
        """
        try:
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 table_name).query(kw, field)
            if cursor.count():
                ods = pd.DataFrame(list(cursor))
                return ods
            return pd.DataFrame()

        except Exception:
            raise MongoIOError('query orders data from db raise a error')

    @classmethod
    def remove_orders(cls, table_name='orders', **kw):
        """
        移除订单
        :param table_name:
        :param kw:
        :return:
        """
        try:
            r = MODEL_TABLE(cls.location, cls.dbname,
                            table_name).remove(kw)
            return r
        except Exception:
            raise MongoIOError('Failed with removing data ')

    @classmethod
    def update_orders(cls, condition, table_name='orders', **kw):
        """
        按condition条件更新K订单数据
        :param table_name:
        :param condition: 形如{‘date':datetime.datetime(2018,1,1)}的一个字典
        :param kw:形如close=0这样的参数组
        :return:
        """
        try:
            MODEL_TABLE(cls.location, cls.dbname,
                        table_name).update_batch(condition, kw)
        except Exception:
            raise MongoIOError('Failed with update by MongoDB')

    @classmethod
    def insert_his_orders(cls, orders):
        """
        插入交易历史数据
        :param orders:
        :return:
        """
        try:
            if len(orders):
                # 订单历史表必须包含的字段，缺省的填0
                # 证券代码的字段名可以不一样，不做统一规范
                col = ['open_date', 'open_price', 'close_date',
                       'close_price', 'type', 'reason', 'profit', 'model_from']
                if set(col) <= set(orders.columns):
                    d = orders.to_dict(orient='records')
                    MODEL_TABLE(cls.location, cls.dbname,
                                'orders_his').insert_batch(d)
                else:
                    raise Exception('lost must field')
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

    @classmethod
    def read_his_orders(cls, model_from, start_date=None,
                        end_date=None, field=None, **kw):
        """
        读取持仓的数据
        :param end_date:
        :param start_date:
        :param model_from:
        :param kw:
        :return:
        """
        try:
            sql = {'model_from': model_from}

            if start_date is None and end_date is None:
                pass
            else:
                if start_date is not None and end_date is None:
                    date = {'close_date': {'$gte': start_date}}
                elif end_date is not None and start_date is None:
                    date = {'close_date': {'$lte': end_date}}
                else:
                    date = {'close_date': {'$gte': start_date, '$lte': end_date}}
                sql = dict(sql, **date)
            sql = dict(sql, **kw)
            cursor = MODEL_TABLE(cls.location, cls.dbname,
                                 'orders_his').query(sql, field)
            if cursor.count():
                ods = pd.DataFrame(list(cursor))
                # ods.drop(['_id', 'classtype'], axis=1, inplace=True)
                return ods
            return pd.DataFrame()
        except Exception:
            raise MongoIOError('query orders data from db raise a error')

    @classmethod
    def insert_his_rmds(cls, rmds):
        """
        插入为账户推荐的历史
        :param rmds:
        :return:
        """
        try:
            if len(rmds):
                dit = []
                for i, row in rmds.iterrows():
                    r = dict(row)
                    dit.append(r)
                # print(dit[0])
                MODEL_TABLE(cls.location, cls.dbname,
                            'rmds_his').insert_batch(dit)
        except Exception:
            raise MongoIOError('Failed with insert data by MongoDB')

