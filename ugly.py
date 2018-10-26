# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/1/31 11:28
"""
import datetime as dt
from Calf.exception import ExceptionInfo
from Calf.utils import trading, fontcolor
from Calf import BaseData
import pandas as pd


class ugly:
    """处理一些可以合理避免风险的意外情况， 这相当于是信号上线的最后
    一道关卡"""
    @classmethod
    def rrads(cls, date, n):
        """
        财务报表公布前或后n个交易日提请入市注意
        :param date:
        :return:
        """
        try:
            aim = trading.trade_period(date, n)
            lt = {'$gte': aim, '$lte': date} if n < 0 else {'$gte': date, '$lte': aim}
            rds = BaseData.read_RRADS(last_time=lt)
            return rds.loc[:, ['stock_code', 'stock_name', 'last_time']]
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def remove(cls, data, n):
        tdy = dt.date.today()
        tdy = dt.datetime(tdy.year, tdy.month, tdy.day)
        aim = trading.trade_period(tdy, n)
        # ugl = cls.rrads(tdy, n)
        ugl = BaseData.read_RRADS(stock_code={'$in': data.stock_code.tolist()})
        if len(ugl):
            ugl = ugl[(ugl.last_time >= tdy) & (ugl.last_time <= aim)]
        # data = pd.merge(data, ugl, on='stock_code', how='left')
        if len(ugl):
            print(fontcolor.F_RED + '-' * 80 + fontcolor.END)
            print(fontcolor.F_RED + '#重大风险提示#' + fontcolor.END)
            print(fontcolor.F_RED, ugl.loc[:, ['stock_code', 'stock_name', 'last_time']], fontcolor.END)
            print(fontcolor.F_RED, '时间：', dt.datetime.now(), '备注：近期将公布财务报表', fontcolor.END)
            print(fontcolor.F_RED + '-' * 80 + fontcolor.END)
            same = list(data[data.stock_code.isin(ugl.stock_code)].index)
            data.drop(same, axis=0, inplace=True)
        return data


# import datetime
# d = datetime.datetime(2018, 3, 15)
# ugly.rrads(d, 5)
# from Foxin.model_data_get.SingalData import signaldata
# data = signaldata.read_signals(model_from='macd_min30', date='2018-01-31')
#
# ugly.remove(data, 50)
# print('as\tdf\tas\n dssd')