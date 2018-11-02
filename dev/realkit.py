# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/3/2 11:08
"""
import datetime as dt
import pandas as pd
from Calf.data import RealData as rd
from Calf.data import KlineData as kd
from Calf.exception import ExceptionInfo
from Calf.utils import trading


class RealKit:
    """
    实时任务中的一些工具
    """

    @classmethod
    def real_profit(cls, data, market='ZH'):
        """
        计算实时收益
        :param data:信号片集，来自于signals,orders...表
        :return:
        """
        try:
            if market == 'ZH':
                real_data = rd.get_stocks_data(list(data.stock_code.unique()))
            elif market == 'US':
                real_data = rd.usa_stock_data(list(data.stock_code.unique()))
            elif market == 'HK':
                real_data = rd.hk_stock_data(list(data.stock_code.unique()))
            else:
                raise ValueError('Calf current only support (ZH, US, HK)')
            if real_data is None:
                return pd.DataFrame()
            data = pd.merge(data, real_data, on='stock_code')
            data['price'] = data.price.astype('float')  # 实时价格
            data['profit'] = (data.price - data.open_price) / data.open_price
            data.fillna(0, inplace=True)
            data = data[data.price > 0] # 避免数据没读到，而返回0
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
                data.rename(columns={'price': 'open_price'}, inplace=True)
            if method == 'local':
                # 注意使用的是open_date
                data['open_price'] = data.apply(
                    lambda r: kd.read_one(r['stock_code'], r['open_date'], 'kline_day')['close'], axis=1)
            return data
        except Exception as e:
            ExceptionInfo(e)
            return pd.DataFrame()
    @classmethod
    def finally_datetime(cls, date, max_pst_days=1, max_pst_hour=14,
                         max_pst_min=55, bsi=False, market=None):
        """
        根据开仓时间和最长持有时间计算买出时间，默认适用于中国A股股票
        :param bsi: False表示按自然日计算持有的时间， True表示按交易日计算
        :param date:
        :param max_pst_days:
        :param market: 作用的市场
        :return:
        """
        try:
            tra = trading(market)
            time = dt.timedelta(hours=max_pst_hour, minutes=max_pst_min)
            start = dt.datetime(date.year, date.month, date.day)
            if bsi:
                end = tra.trade_period(start, max_pst_days)
                return end + time
            else:
                end = start + dt.timedelta(days=max_pst_days)
                if tra.is_trade_day(end):
                    return end + time
                else:  # end 不是交易日
                    if tra.trade_days(start, end) > 0:  # 向前推算
                        # for i in range(1, max_pst_days, 1):
                        #     end = end - dt.timedelta(days=1)
                        #     if tra.is_trade_day(end):
                        #         return end + time
                        end = tra.trade_period(end, -1)
                    else:  # 向后推算
                        # for i in range(1, 11, 1):
                        #     end = start + dt.timedelta(days=i)
                        #     if tra.is_trade_day(end):
                        #         return end + time
                        end = tra.trade_period(end, 1)
                    return end + time
                return date
        except Exception as e:
            ExceptionInfo(e)
            return date

pass
# a = RealKit.finally_datetime(date=dt.datetime(2018, 7, 13), max_pst_days=1,
#                              max_pst_hour=10, market='Forex')
# print(a)