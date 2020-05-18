# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/2 11:08
"""
import datetime as dt
import pandas as pd
from Calf import RealData as rd
from Calf import KlineData as kd
from Calf.exception import ExceptionInfo
from Calf.utils import trading


class RealKit:
    """
    实时任务中的一些工具
    """

    @classmethod
    def real_profit(cls, data):
        """
        计算实时收益
        :param data:信号片集，来自于signals表
        :return:
        """
        try:
            real_data = rd.get_stocks_data(list(data.stock_code))
            data = pd.merge(data, real_data, on='stock_code')
            data['price'] = data.price.astype('float')  # 实时价格
            data['profit'] = (data.price - data.open_price) / data.open_price
            data.fillna(0, inplace=True)
            return data
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()

    @classmethod
    def unreplenishment(cls, data, method='local'):
        """
        将XDXR_day复权后的价格更新至现价
        :param method:获取现价的方法：net表示从网络接口获取最新价作为现价
         local表示从本地数据库获取。
         目前反复权操作指针对中国A股XDXR_day 表,将其close-->现价
        :param data:
        :return:
        """
        try:
            if method == 'net':
                real_data = rd.get_stocks_data(list(data.stock_code))
                data.drop('close', axis=1, inplace=True)
                data = pd.merge(data, real_data.loc[:, ['stock_code', 'price']], on='stock_code')
                data.rename(columns={'price': 'close'}, inplace=True)
            if method == 'local':
                data['close'] = data.apply(
                    lambda r: kd.read_one(r['stock_code'], r['date'], 'kline_day')['close'], axis=1)
            return data
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()
    @classmethod
    def finally_datetime(cls, date, max_pst_days=1, bsi=False):
        """
        根据开仓时间和最长持有时间计算买出时间，适用于中国A股股票
        :param bsi: False表示按自然日计算持有的时间， True表示按交易日计算
        :param date:
        :param max_pst_days:
        :return:
        """
        try:
            time = dt.timedelta(hours=14, minutes=55)
            start = dt.datetime(date.year, date.month, date.day)
            if bsi:
                end = trading.trade_period(start, max_pst_days)
                return end + time
            else:
                end = start + dt.timedelta(days=max_pst_days)
                if trading.is_trade_day(end):
                    return end + time
                else:  # end 不是交易日
                    if trading.trade_days(start, end) > 0:  # 向前推算
                        for i in range(1, max_pst_days, 1):
                            end = end - dt.timedelta(days=1)
                            if trading.is_trade_day(end):
                                return end + time
                    else:  # 向后推算
                        for i in range(1, 11, 1):
                            end = start + dt.timedelta(days=i)
                            if trading.is_trade_day(end):
                                return end + time
                return date
        except Exception as e:
            ExceptionInfo(e)
            return date