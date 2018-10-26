# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/11/24 9:27
"""
import datetime
import pandas as pd
import numpy as np
import re
from abc import ABCMeta, abstractmethod
from Calf.utils import trading as td
from Calf.exception import warning, ExceptionInfo
from Calf.modelfinance import FinanceIndex as fi
from Calf import KlineData


class VerifyError(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ModelValidator:
    """
    一个广泛适用的模型回测验证工具，
    适用于A股大部分的交易场景，支持多空对冲，
    对验证得到的交易清单进行量化评估，
    其他交易场景
    """
    __metaclass__ = ABCMeta
    model_name = ''
    kline = ''
    data = pd.DataFrame([])
    index_flag = False
    sd = datetime.datetime(2017, 1, 1)  # 默认回测的时间起点
    ed = datetime.datetime(2018, 1, 1)
    # 交易策略的相关参数
    model_param = {
        'INDEX_REFERENCE': '399303',
        'price': 10,  # 股票的单价（收盘）
        'amount': 20000000,  # 成交额
        'max_pst_vol': 10,  # 最大持仓量
        'stop_loss': 0.1,  # 止损点
        'stop_get': 0.1,  # 止赢点
        'fee': 0.005,  # 交易费用
        'max_pst_days': 1,  # 最大持仓天数
        'max_pst_mins': 0,  # 最大持有分钟数，最终的持有时间将是天数+分钟数
        'lever': 1,  # 杠杆率
    }
    # 日内支持验证的时间点(适用于A股)，其他市场的日内回测需要重置这些变量
    min60 = [1030, 1130, 1400, 1500]
    min30 = [1000, 1030, 1100, 1130, 1330, 1400, 1430, 1500]
    min15 = [945, 1000, 1015, 1030, 1045, 1100, 1115, 1130,
             1315,1330, 1345, 1400, 1415, 1430, 1445, 1500]
    min5 = [935, 940, 945, 950, 955, 1000, 1005, 1010, 1015,
            1020, 1025, 1030, 1035, 1040, 1045, 1050, 1055,
            1100, 1105, 1110, 1115, 1120, 1125, 1130, 1305,
            1310, 1315, 1320, 1325, 1330, 1335, 1340, 1345,
            1350,1355, 1400, 1405, 1410, 1415, 1420, 1425,
            1430, 1435, 1440, 1445, 1450, 1455, 1500]

    # 验证得到的最终结果最少包含但不限于cols描述的一个df
    cols = ['code', 'open_date', 'close_date', 'open_price', 'close_price',
            'real_profit', 'profit', 'type', 'reason', 'confidence']
    # 核心buy函数所必须的dict字段
    clo = ['code', 'open_date', 'open_price', 'type', 'confidence']
    ugly = list()  # 自定义的非交易时间，在这些时间点上将不会发生交易，通常是为了回避风险
    ntf = False  # 计算交易日的方法
    kline_data_location = None  # 回测过程中需要到那个位置读取k线数据
    kline_data_dbname = None
    kd = KlineData(kline_data_location, kline_data_dbname)

    @classmethod
    def VerifyFrame(cls, data, kline, func=None, start_date=None, end_date=None,
                    ugly=list(), ntf=False):
        """
        :param ntf: 按自然日[False]计算持有时间或交易日[True]持有时间
        :param ugly: 用户自定义的非交易时间，datetime类型的数组
        :param func:能够读取用于验证该模型的K线数据的函数
        :param data: Need to verify the signals
        :param kline: kline type of those signals
        :param start_date: The starting time for verifying the models's return
        :param end_date: The ending time for verifying the models's return
        :return:
        """
        try:
            cls.kline = kline
            cls.data = data
            if start_date is not None:
                cls.sd = start_date
            if end_date is not None:
                cls.ed = end_date
            cls.func = func if func is not None else cls.kd.read_data
            cls.ugly = ugly
            cls.ntf = ntf
            must = ['code', 'type', 'open_price', 'open_date', 'confidence']
            if set(must) <= set(data.columns):
                pass
            else:
                raise Exception
        except Exception:
            raise VerifyError('initialize this class raise error')
        pass

    @classmethod
    def modelparammodify(cls, **kw):
        """
        修改基本参数的值
        :param kw:
        :return:
        """
        try:
            keys = cls.model_param.keys()
            for k, v in zip(kw.keys(), kw.values()):
                if k in keys:
                    cls.model_param[k] = v
                else:
                    message = 'no find this key=%s in models param' % k
                    raise warning(message)
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def reference(cls, date):
        """
        :param date: aims'date
        :return: true or false
        """
        try:
            if date in cls.ugly:
                return False
            else:
                return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def close(cls, data, mark, op):
        """
        默认的执行平仓策略的函数，这个平仓策略是指按止赢&止损&最长持有时间这种规则来
        执行平仓操作。
        :param data: 用于检验卖出信息的K线数据，是买入时间点之后的、合理的、可交易
        的、最晚的，通过data就可以计算出在什么时间点卖出
        :param mark: 持仓类型
        :param op: 买价
        :return: 返回卖出的时间， 收益， 原因（-1表示止损， 1表示止盈， 0表示时间到）
        """
        sell_day = None
        _percent = 1
        if mark:  # 做空
            stop_get = cls.model_param['stop_get']
            stop_loss = cls.model_param['stop_loss']
            data = data[::-1]
            for i, r in data.iterrows():
                get_percent = r.low / op
                loss_percent = r.high / op
                sell_day = r.date
                if loss_percent >= 1 + stop_loss:  # 损失超过上限
                    return sell_day, loss_percent, -1, r.high
                elif get_percent < 1 - stop_get:  # 达到预期收益
                    return sell_day, get_percent, 1, r.low
                else:
                    _percent = r.close / op
                    close_price = r.close
        else:  # 做多
            stop_get = cls.model_param['stop_get']
            stop_loss = cls.model_param['stop_loss']
            data = data[::-1]
            for i, r in data.iterrows():
                get_percent = r.high / op
                loss_percent = r.low / op
                sell_day = r.date
                if loss_percent <= 1 - stop_loss:
                    return sell_day, loss_percent, -1, r.low
                elif get_percent > 1 + stop_get:
                    return sell_day, get_percent, 1, r.high
                else:
                    _percent = r.close / op
                    close_price = r.close
        return sell_day, _percent, 0, close_price  # 未能止损盈

    @classmethod
    def simple_close(cls, signal):
        """
        平仓的信息直接由回测的历史信号给出，这样我们在执行历史信号平仓函数的时候可以直接在
        历史信号中找到那个关于平仓的信息。当你想要执行这种类型的回测时，所给出的signal则
        必须包含额外的close_date,close_price这两个字段
        :param signal:
        :return:
        """
        try:
            # code = signal['code']
            close_date = signal['close_date']
            close_price = signal['close_price']
            open_price = signal['open_price']
            pf = close_price / open_price
            # d = cls.kd.read_one(code, close_date, cls.kline)
            # if close_price < d['close']:
            #     # 以卖出指导价卖出
            #     pf = close_price / open_price
            #     return close_date, pf, 0
            # else:
            #     pf = d['close'] / open_price
            #     return close_date, pf, 0
            return close_date, pf, 0, close_date
            pass
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def in_order_close(cls, signal):
        """
        适用于印度股市
        :param signal:
        :return:
        """
        try:
            code = signal['code']
            od = signal['open_date']
            open_price = signal['open_price']
            mark = signal['type']
            s = od
            for d in range(0, 12, 1):
                if cls.ntf:
                    # 持有时间按交易日计算
                    # 可能存在不合理的情况，因为目前我们不确定印度市场休市的安排
                    e = td.trade_period(od, days=int(d + cls.model_param['max_pst_days']),
                                        holidays=[])
                else:
                    # 持有时间按自然日计算
                    e = od + datetime.timedelta(days=int(d + cls.model_param['max_pst_days']))
                e = e + datetime.timedelta(minutes=int(cls.model_param['max_pst_mins']))
                try:
                    data = cls.func(code, s, e, cls.kline)
                except Exception:
                    raise TypeError('User-defined function raise a Exception')
                if len(data) > 2:
                    data = data[(data.date >= s) & (data.date <= e)]
                    data = data[:-2]
                    if len(data):
                        return cls.close(data, mark, open_price)
            return e, 1, 404, 0
        except Exception as ep:
            ExceptionInfo(ep)

    @classmethod
    def usa_order_close(cls, signal):
        """
        适用于美股融资融券当日冲销账户（要成为这一类用户，账户余额必须大于$25,000）,
        执行T+0交易规则，不受交割制度困扰（T+3），但可能会受到资金规模困扰，这与券商相关,
        外汇也适用于这种类型的平仓
        :param signal:
        :return:
        """
        try:
            code = signal['code']
            od = signal['open_date']
            open_price = signal['open_price']
            mark = signal['type']
            s = od
            for d in range(0, 12, 1):
                if cls.ntf:
                    # 持有时间按交易日计算
                    # 可能存在不合理的情况，因为目前我们不确定美股市场休市的安排
                    e = td.trade_period(od, days=int(d + cls.model_param['max_pst_days']),
                                        holidays=[])
                else:
                    # 持有时间按自然日计算
                    e = od + datetime.timedelta(days=int(d + cls.model_param['max_pst_days']))
                e = e + datetime.timedelta(minutes=int(cls.model_param['max_pst_mins']))
                try:
                    data = cls.func(code, s, e, cls.kline)
                except Exception:
                    raise TypeError('User-defined function raise a Exception')
                if len(data):
                    data = data[(data.date >= s) & (data.date <= e)]
                    if len(data):
                        return cls.close(data, mark, open_price)
            return e, 1, 404, 0
        except Exception as ep:
            ExceptionInfo(ep)

    @classmethod
    def default_order_close(cls, signal):
        """
        默认的一个平仓函数，它完成的任务就是接受开仓信号&用于验证这个信号的“未来的”、“历史的”
        数据，并将其传递给执行平仓动作的函数或直接在这里实现。总之，这个函数必要返回验证的结果。
        :return:
        """
        # 主要适用于中国A股（T+1），或与之交易规则基本一致的市场，其他市场可参考
        # 此函数描述了关于如何卖出资产的处理方式
        # 由于交易日不是连续的，当天买入后需第二交易日及以后才可以卖出
        # 这里最长等待12个休市日，如还未找到交易数据则本次交易收益计算无效
        # 为了确保做多与做空保持相同的风控策略，止盈止损系数对换
        # 这里的自然日不包括连续休市天数大于最长持有天数的那些天
        try:
            code = signal['code']
            date = signal['open_date']
            open_price = signal['open_price']
            mark = signal['type']
            od = datetime.datetime(date.year, date.month, date.day)
            s = od + datetime.timedelta(days=1)  # 买入时间的第二天
            for d in range(0, 12, 1):
                if cls.ntf:
                    # 持有时间按交易日计算
                    e = td.trade_period(od, days=int(d + cls.model_param['max_pst_days']))
                else:
                    # 持有时间按自然日计算
                    e = od + datetime.timedelta(days=int(d + cls.model_param['max_pst_days']))
                e = e + datetime.timedelta(minutes=int(cls.model_param['max_pst_mins']))
                try:
                    data = cls.func(code, s, e, cls.kline)
                except Exception:
                    raise TypeError('User-defined function raise a Exception')
                if len(data):
                    return cls.close(data, mark, open_price)
            return e, 1, 404, 0
        except Exception as ep:
            ExceptionInfo(ep)
            return date, 1, 500, 0

    @classmethod
    def hedging(cls, date, n):
        """
        通过给定的时间点和开仓数量，选择对冲组合，满足量少的方向
        :param date:
        :param n:
        :return:
        """
        try:
            data = cls.data[cls.data['open_date'] == date]
            pst = data[data.type == False]
            ngt = data[data.type == True]
            ngt_ = len(ngt)
            pst_ = len(pst)
            # t_ = n // 2
            _ = pst_ if pst_ < ngt_ else ngt_
            _ = _ if _ * 2 <= n else n // 2
            gt = ngt.sort_values(['confidence'], ascending=True).head(_)
            st = pst.sort_values(['confidence'], ascending=True).head(_)
            return pd.concat([gt, st], axis=0, join='outer', ignore_index=True)
            # if n <= (ngt_ + pst_):  # 总数够
            #     _ = pst_ if pst_ < ngt_ else ngt_
            #     gt = ngt.sort_values(['confidence'], ascending=True).head(_)
            #     st = pst.sort_values(['confidence'], ascending=True).head(_)
            #     return pd.concat([gt, st], axis=0, join='outer', ignore_index=True)
            # else: # 可选的数量不够
            #
            # # 倒序
            # return selected_signals.sort_values(['confidence'], ascending=True).head(n=n)
            pass
        except Exception as e:
            print(e)
            return pd.DataFrame([])

    @classmethod
    def optimal_choice(cls, date, n):
        """
        When more than one stock at the same time, We need to go
        according to a custom method to choose some stocks
        :param date: There is more than one stock time
        :param n: The number of choices
        :return: Selected stock
        """
        try:
            selected_signals = cls.data[cls.data['open_date'] == date]
            return selected_signals.sort_values(['confidence'], ascending=True).head(n=n)
        except Exception as e:
            print(e)
            return pd.DataFrame([])

    @classmethod
    def order_open(cls, signal, order_close=None):
        """
        开仓引擎
        根据signal提供的品种代码、建议买入时间点、建议买入价格、建仓类型，
        按order_close函数约定的交易规则执行交易，order_close会返回本次模拟交易
        的结果，它们分别是出售的时间，实际纯收益，出售原因。相关交易费用也将
        会在这里处理
        :param order_close: 用户自定义的平仓函数
        :param signal: need to buy stock
        :return: the result of this buy
        """
        c = signal['code']
        open_date = signal['open_date']
        if cls.reference(open_date):
            open_price = signal['open_price']
            mark = signal['type']
            if order_close is None:
                sell_date, profit_percent, r, close_price = cls.default_order_close(signal)
            else:
                try:
                    sell_date, profit_percent, r, close_price = order_close(signal)
                except Exception:
                    raise TypeError('User-defined function raise a Exception')
            # print(sell_day, profit_percent)
            profit = profit_percent
            stop_loss = cls.model_param['stop_loss']  # 0.02
            stop_get = cls.model_param['stop_get']
            if mark:  # 做空
                if profit > 1 + stop_loss:  # 亏损
                    profit = 1 + cls.model_param['fee'] + stop_loss
                elif profit < 1 - stop_get:
                    profit = 1 + cls.model_param['fee'] - stop_get
                else:
                    profit = profit_percent + cls.model_param['fee']  # 计算交易成本
                # sell_price = open_price * profit
                profit = profit * -1 + 1  # 做空的特殊处理
                profit_percent = profit_percent * -1 + 1
            else:
                if profit > 1 + stop_get:
                    profit = 1 - cls.model_param['fee'] + stop_get
                elif profit < 1 - stop_loss:
                    profit = 1 - cls.model_param['fee'] - stop_loss
                else:
                    profit = profit_percent - cls.model_param['fee']  # 计算交易成本
                # sell_price = open_price * profit
                profit -= 1
                profit_percent -= 1
            profit *= cls.model_param['lever']
            # profit_percent实际收益
            rlt = dict(code=c, open_date=open_date, open_price=open_price, close_date=sell_date,
                       close_price=close_price, profit=profit, real_profit=profit_percent,
                       type=mark, reason=r, confidence=signal['confidence'])
            return rlt

        else:
            return dict(code=c, open_date=open_date, open_price=signal['open_price'],
                        type=signal['type'], reason=500, confidence=signal['confidence'])

    @classmethod
    def verify_day(cls, optimal_choice=None, order_close=None):
        """
        日级别的回测验证
        :param optimal_choice: 同一时间点出现多个信号是，按照什么样的策略选择，需要
        通过这个函数来实现，默认按本验证器提供的函数选择
        :param order_close: 对于不同的市场而言卖出的规则可能不一样，这就需要按时间
        情况重写，默认按本验证器提供的函数实现（适用于A股市场）
        :return: models's win rate, Simple interest and Compound interest
        """
        good = pd.DataFrame([], columns=cls.cols)
        goods = pd.DataFrame([], columns=cls.cols)
        Rr = 1
        select_func = cls.optimal_choice if optimal_choice is None else optimal_choice
        order_close = cls.default_order_close if order_close is None else order_close
        sRr = 1 / cls.model_param['max_pst_vol']    # 一个标准单所占的资金比例
        for e in pd.date_range(start=cls.sd, end=cls.ed):
            # e    # 日期指针

            # 下面这段代码相当于模拟交易过程中的开仓
            pst_ = len(good)  # 当前持仓量
            need_count = cls.model_param['max_pst_vol'] - pst_  # 剩余仓位
            # print(e, 'need_count:', need_count, list(good.stock_code))
            br = Rr / need_count if need_count != 0 else 0
            br = sRr if br > sRr else br
            if need_count > 0 and Rr > 0:
                # 根据需要购买的数量选择购买的股票
                buys = select_func(e, int(need_count))
                g = pd.DataFrame([cls.order_open(dict(buys.loc[i]), order_close)
                                  for i in buys.index], columns=cls.cols)
                # 购买过程中可能有购买失败的
                g.dropna(axis=0, inplace=True)
                bct_ = len(g)
                if bct_ > 0:
                    g['Rr'] = br
                    Rr -= br * bct_
                    goods = pd.concat([g, goods], axis=0, join='outer', ignore_index=True)
                    good = pd.concat([g, good], axis=0, join='outer', ignore_index=True)

            pass
            # 下面这段代码相当于模拟交易过程中的平仓
            drop_rows = list(good[good['close_date'] == e].index)
            if len(drop_rows):
                s = good.loc[drop_rows]
                Rr += ((s.profit + 1) * s.Rr).sum()
                '''回笼资金后不补填缺口，仍以不高于原始资金量的比例入市'''
                Rr = 1 if Rr > 1 else Rr
                good.drop(drop_rows, axis=0, inplace=True)
            # progress_bar(total=test_days, complete=i)
            print('\r** {0} **'.format(e), end=' ', flush=True)
            pass
        if len(goods):
            menu = goods.copy(deep=True)
            tcs = len(goods)
            menu['MC'] = menu.profit * menu.Rr  # 边际贡献
            menu['date'] = menu.close_date.dt.normalize()
            menu = menu.groupby(['close_date'], as_index=False).agg({'MC': 'sum'})
            menu = menu.rename(columns={'MC': 'profit', 'close_date': 'date'})
            win_rate = (goods.profit > 0).sum() / tcs
            dcs = len(menu)  # 交易次数以日计
            avg_signals = len(goods) / 250.0
            profits = fi.already_get(menu.profit.tolist())
            max_dd = fi.max_drawdown(profits)
            spr = menu.profit.sum()
            cpr = (menu.profit.mean() + 1) ** dcs - 1  # 复利，估计数
            apr = fi.annualized_returns(menu.profit.tolist())   # 年化收益
            sharp = fi.sharp(menu.profit.tolist())
            dit = dict(win_rate=win_rate, tcs=tcs, dcs=dcs, avg_signals=avg_signals,
                       max_dd=max_dd, spr=spr, cpr=cpr, apr=apr, sharp=sharp,
                       max_pst_vol=cls.model_param['max_pst_vol'],
                       max_pst_date=cls.model_param['max_pst_days'],
                       stop_get=cls.model_param['stop_get'],
                       stop_loss=cls.model_param['stop_loss'],
                       lever=cls.model_param['lever'],
                       start_date=cls.sd, end_date=cls.ed, date=datetime.datetime.now())
            goods['stop_loss'] = cls.model_param['stop_loss']
            goods['stop_get'] = cls.model_param['stop_get']
            return dit, menu, goods
        else:
            return None, None, None

    @classmethod
    def financial_indicator(cls, details):
        """
        根据交易明细，计算常见的各财务指标
        :param details:
        :return:
        """
        try:
            must = ['profit', 'Rr', 'open_date']
            if set(must) <= set(details.columns):
                pass
            else:
                raise Exception('lost must columns')
            menu = details.copy(deep=True)
            tcs = len(details)
            menu['MC'] = menu.profit * menu.Rr  # 边际贡献
            menu['date'] = menu.close_date.dt.normalize()
            menu = menu.groupby(['date'], as_index=False).agg({'MC': 'sum'})
            menu = menu.rename(columns={'MC': 'profit'})
            win_rate = (details.profit > 0).sum() / len(details)
            dcs = len(menu)  # 交易次数以日计
            avg_signals = tcs / 250.0
            profits = fi.already_get(menu.profit.tolist())
            max_dd = fi.max_drawdown(profits)
            spr = menu.profit.sum()
            cpr = (menu.profit.mean() + 1) ** dcs - 1  # 复利，估计数
            apr = fi.annualized_returns(menu.profit.tolist())  # 年化收益
            sharp = fi.sharp(menu.profit.tolist())
            dit = dict(win_rate=win_rate, tcs=tcs, dcs=dcs, avg_signals=avg_signals,
                       max_dd=max_dd, spr=spr, cpr=cpr,
                       apr=apr, sharp=sharp, max_pst_vol=cls.model_param['max_pst_vol'],
                       max_pst_date=cls.model_param['max_pst_days'],
                       stop_get=cls.model_param['stop_get'],
                       stop_loss=cls.model_param['stop_loss'],
                       lever=cls.model_param['lever'],
                       start_date=cls.sd, end_date=cls.ed, date=datetime.datetime.now())
            details['stop_loss'] = cls.model_param['stop_loss']
            details['stop_get'] = cls.model_param['stop_get']
            return dit, menu
        except Exception as e:
            raise e

    @classmethod
    def verify_min(cls, optimal_choice=None, order_close=None):
        """
        日内分钟级别的回测验证
        :param optimal_choice:
        :param order_close:
        :return:
        """
        # test_days = (cls.ed - cls.sd).days
        good = pd.DataFrame([], columns=cls.cols)
        goods = pd.DataFrame([], columns=cls.cols)
        select_func = cls.optimal_choice if optimal_choice is None else optimal_choice
        order_close = cls.default_order_close if order_close is None else order_close
        times = {'min5': cls.min5, 'min15': cls.min15, 'min30': cls.min30, 'min60': cls.min60}
        time = times[re.search('min\d+', cls.kline, re.I).group()]
        Rr = 1
        sRr = 1 / cls.model_param['max_pst_vol']  # 标准单所占比例
        """年内"""
        for e in pd.date_range(start=cls.sd, end=cls.ed):
            # e = cls.sd + datetime.timedelta(days=i)
            need_count = cls.model_param['max_pst_vol'] - len(good)  # 当前持有的股票数量
            # print(e, 'position_count:', len(good))
            br = Rr / need_count if need_count != 0 else 0
            """日内"""
            for t in time:
                br = sRr if br > sRr else br
                bt = e + datetime.timedelta(hours=t // 100, minutes=t % 100)
                if need_count > 0 and Rr > 0:
                    # 根据需要购买的数量选择购买的股票
                    buys = select_func(bt, int(need_count))
                    # 购买
                    g = pd.DataFrame([cls.order_open(dict(buys.loc[i]), order_close) for i in buys.index],
                                     columns=cls.cols)
                    # 购买过程中可能有购买失败的
                    g.dropna(axis=0, inplace=True)
                    bct_ = len(g)  # 本次购买数量
                    if bct_ > 0:
                        """日内按最大持仓量计算固定投资比例，按实际资金池存量买入"""
                        # br = Rr / cls.model_param['max_pst_vol']
                        g['Rr'] = br
                        Rr -= br * bct_
                        goods = pd.concat([g, goods], axis=0, join='outer', ignore_index=True)
                        good = pd.concat([g, good], axis=0, join='outer', ignore_index=True)

                drop_rows = list(good[good['close_date'] <= bt].index)
                if len(drop_rows):
                    s = good.loc[drop_rows]
                    Rr += ((s.profit + 1) * s.Rr).sum()
                    '''回笼资金后不补填缺口，仍以不高于原始资金量的比例入市'''
                    Rr = 1 if Rr > 1 else Rr
                    good.drop(drop_rows, axis=0, inplace=True)
                need_count = cls.model_param['max_pst_vol'] - len(good)
                br = Rr / need_count if need_count != 0 else 0
                pass
            # """每一个交易日确认一次收益"""
            # db = goods[goods.open_date > e]  # e日新买入的股票
            # if len(db):
            #     # print(db)
            #     p = (db.profit * db.Rr).sum()
            #     rate_list.append(p)
            #     day_list.append(e)
            print('\r** {0} **'.format(e), end=' ', flush=True)
        if len(goods):
            menu = goods.copy(deep=True)
            tcs = len(goods)
            menu['MC'] = menu.profit * menu.Rr  # 边际贡献
            menu['date'] = menu.close_date.dt.strftime('%Y-%m-%d')
            menu['date'] = pd.to_datetime(menu.date, format='%Y-%m-%d')
            menu = menu.groupby(['date'], as_index=False).agg({'MC': 'sum'})
            menu = menu.rename(columns={'MC': 'profit'})
            win_rate = (goods.profit > 0).sum() / len(goods)
            dcs = len(menu)  # 交易次数以日计
            avg_signals = tcs / 250.0
            profits = fi.already_get(menu.profit.tolist())
            max_dd = fi.max_drawdown(profits)
            spr = menu.profit.sum()
            cpr = (menu.profit.mean() + 1) ** dcs - 1  # 复利，估计数
            apr = fi.annualized_returns(menu.profit.tolist())  # 年化收益
            sharp = fi.sharp(menu.profit.tolist())
            dit = dict(win_rate=win_rate, tcs=tcs, dcs=dcs, avg_signals=avg_signals,
                       max_dd=max_dd, spr=spr, cpr=cpr,
                       apr=apr, sharp=sharp, max_pst_vol=cls.model_param['max_pst_vol'],
                       max_pst_date=cls.model_param['max_pst_days'],
                       stop_get=cls.model_param['stop_get'],
                       stop_loss=cls.model_param['stop_loss'],
                       lever=cls.model_param['lever'],
                       start_date=cls.sd, end_date=cls.ed, date=datetime.datetime.now())
            goods['stop_loss'] = cls.model_param['stop_loss']
            goods['stop_get'] = cls.model_param['stop_get']
            return dit, menu, goods
        else:
            return None, None, None

    @classmethod
    def param_optimization(cls, param_table, on='day', order_close=None):
        """
        暴力参数求解
        :param param_table:包含max_pst_vol,max_pst_days,stop_get,stop_loss交易参数组合
        的参数表，这是一个df
        :param on:何种级别的回测
        :return:
        """
        if on not in ('day', 'min'):
            raise ValueError('this "on" must in (day, min)')
        rls = list()
        for i, r in param_table.iterrows():
            try:
                # p = dict(max_pst_vol=r.max_pst_vol, max_pst_days=r.max_pst_days, stop_get=r.stop_get, stop_loss=r.stop_loss)
                cls.modelparammodify(max_pst_vol=r.max_pst_vol, max_pst_days=r.max_pst_days,
                                     stop_get=r.stop_get, stop_loss=r.stop_loss)
                dit, mus, tdr = cls.verify_day(order_close) if on == 'day' else cls.verify_min(order_close)
                rp = dict(dit, **r)
            except Exception as e:
                ExceptionInfo(e)
                rp = dict(r)
            finally:
                rls.append(rp)
        rls = pd.DataFrame(rls)
        return rls

    @classmethod
    def verify_all(cls, order_close=None):
        """
        不考虑持仓量，资金配比，单独看待某个信号在给定的平仓函数下的收益
        :param order_close: 平仓函数
        :return:
        """
        trades = list()
        order_close = cls.default_order_close if order_close is None else order_close
        counts = len(cls.data)
        n = 1
        for i, r in cls.data.iterrows():
            d = cls.order_open(dict(cls.data.loc[i, cls.clo]), order_close)
            d = dict(close_date=d['close_date'], close_price=d['close_price'],
                     profit=d['profit'], reason=d['reason'])
            trades.append(dict(d, **r))
            print('\r{0}/{1}'.format(n, counts), end=' ', flush=True)
            n += 1
        # 在输入的原始信号数据后面附加了回测的结果
        details = pd.DataFrame(trades)
        return details

    @classmethod
    def index_profit(cls, sd, ed, kline, index_code=None):
        """
        计算回测验证期内的大盘收益
        :param sd:
        :param ed:
        :param kline: 选择计算大盘收益的k线粒度
        :return: 返回以kline计的收益列表
        """
        ic = cls.model_param['INDEX_REFERENCE'] if index_code is None else index_code
        # TODO(leungjain): 日内数据可能需要合并date、time，
        index_data = cls.kd.read_data(code=ic, start_date=sd, end_date=ed, kline=kline)
        index_data['last_close'] = index_data.close.shift(-1)
        index_data.dropna(inplace=True)
        index_data['profit'] = pd.eval('(index_data.close - index_data.last_close) '
                                       '/ index_data.last_close')
        return index_data.loc[:, ['date', 'profit']]

    @classmethod
    def capm(cls, goods, kline):
        """
        计算Alpha, Beta这两个指标，由于这两个指标的计算比较复杂，
        所以在回测过程中不主动计算他们，当用户需要计算这两个指标
        时，把verify_XXX函数返回的goods传递给capm就可以计算得出
        Alpha, Beta.
        :param kline:
        :param goods:
        :return:
        """
        try:
            kline = 'index_' + re.search('(min\d+)|(day)', kline, re.I).group()
            index_data = cls.index_profit(sd=goods.open_date.min(),
                                          ed=goods.close_date.max(), kline=kline)
            index_profit = list()
            for i, r in goods.iterrows():
                idp = index_data[(index_data.date > r['open_date']) &
                                 (index_data.date <= r['close_date'])]
                index_profit.append(idp.profit.sum())
            goods['index_profit'] = index_profit
            menu = goods.copy(deep=True)
            menu['MC'] = menu.profit * menu.Rr  # 边际贡献
            if re.search('min', kline, re.I) is not None:
                menu['close_date'] = menu.close_date.dt.strftime('%Y-%m-%d')
                menu['close_date'] = pd.to_datetime(menu.close_date,
                                                    format='%Y-%m-%d')
            menu = menu.groupby(['close_date'],
                                as_index=False).agg({'MC': 'sum', 'index_profit': 'mean'})
            menu = menu.rename(columns={'MC': 'profit', 'close_date': 'date'})
            Alpha, Beta = fi.CAPM(menu.profit.tolist(), menu.index_profit.tolist())
            return Alpha, Beta, menu
        except Exception as e:
            ExceptionInfo(e)
            return 'N/A', 'N/A', None

    @classmethod
    def similar_amount(cls, goods, kline, gap=5):
        """
        计算交易信号发生后gap分钟内发生的交易额，适用于A股
        :param goods:
        :return:
        """
        try:
            goods['sa'] = np.nan
            goods['sl'] = np.nan
            goods['sh'] = np.nan
            for i, g in goods.iterrows():
                sd = datetime.datetime(g.open_date.year, g.open_date.month, g.open_date.day)
                if g.open_date.hour == 0 and g.open_date.minute == 0:
                    # 日线，特殊处理
                    tme = {'$in':[1455, 1500]}
                else:
                    # 日内
                    if g.open_date.hour == 15:
                        # 日内收盘时的信号
                        tme = 1500
                    elif g.open_date.hour == 11 and g.open_date.minute == 30:
                        # 日内上午收盘时的信号
                        tme = 1305
                    else:
                        tme = (g.open_date.minute + gap) // 5
                        dt = sd + datetime.timedelta(hours=g.open_date.hour, minutes=tme * 5)
                        tme = dt.hour * 100 + dt.minute * 5
                d = cls.kd.read_data(code=g.code, start_date=sd, end_date=sd,
                                     kline=kline, time=tme)
                if len(d):
                    sa = d.amount.sum()
                    sl = d.low.min()
                    sh = d.high.max()
                else:
                    sa, sl, sh = np.nan, np.nan, np.nan

                goods.at[i, ['sa', 'sl', 'sh']] = sa, sl, sh
            goods['pv'] = pd.eval('(goods.sh - goods.sl) / goods.open_price')
            menu = goods.copy(deep=True)
            menu.dropna(axis=0, inplace=True)
            if len(menu):
                menu['date'] = menu.close_date.dt.strftime('%Y-%m-%d')
                menu['date'] = pd.to_datetime(menu.date, format='%Y-%m-%d')
                menu = menu.groupby(['date'], as_index=False).agg({'sa': 'sum', 'pv': 'mean'})
            return goods, menu
            pass
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def tick_amount(cls, goods, gap=5):
        try:
            from Calf import TickData as td
            goods['pa'] = np.nan
            goods['sa'] = np.nan
            goods['sl'] = np.nan
            goods['sh'] = np.nan
            for i, g in goods.iterrows():
                sd = datetime.datetime(g.open_date.year, g.open_date.month, g.open_date.day)
                if g.open_date.hour == 0 and g.open_date.minute == 0:
                    # 日线，特殊处理
                    tme = {'$gte': 1455, '$lte': 1500}
                    # tim = 0
                else:
                    # 日内
                    if g.open_date.hour == 15:
                        # 日内收盘时的信号
                        tme = {'$gte': 1455, '$lte': 1500}
                        # tim = 1500
                    elif g.open_date.hour == 11 and g.open_date.minute == 30:
                        # 日内上午收盘时的信号
                        tme = {'$gte': 1300, '$lte': 1300 + gap}
                        # tim = 1130
                    else:
                        dt = g.open_date + datetime.timedelta(minutes=gap)
                        stme = g.open_date.hour * 100 + g.open_date.minute
                        etme = dt.hour * 100 + dt.minute
                        tme = {'$gte': stme, '$lte': etme}
                        # tim = stme
                d = td.read_data(code=g.code, start_date=sd, end_date=sd,
                                 field={'date': True, 'time': True, 'price': True, 'volume': True},
                                 time=tme, price={'$lte': g.open_price})
                if len(d):
                    sa = (d.price * d.volume * 100).sum()
                    sl = d.price.min()
                    sh = d.price.max()
                else:
                    sa, sl, sh = 0, 0, 0

                k = cls.kd.read_one_min(code=g.code, date=g.open_date, kline='kline_min5')
                if k is not None:
                    pa = k['amount']
                else:
                    pa = 0

                goods.at[i, ['pa', 'sa', 'sl', 'sh']] = pa, sa, sl, sh
            goods['pv'] = pd.eval('(goods.sh - goods.sl) / goods.open_price')
            menu = goods.copy(deep=True)
            if len(menu):
                menu['date'] = menu.open_date.dt.strftime('%Y-%m-%d')
                # menu['open_date'] = pd.to_datetime(menu.open_date, format='%Y-%m-%d')
                menu = menu.groupby(['date'], as_index=False).agg({'pa': 'sum'})
            menu = menu.rename(columns={'pa': 'suma'})
            goods['date'] = goods.open_date.dt.strftime('%Y-%m-%d')
            goods = pd.merge(goods, menu, on='date')
            goods['Rr'] = goods.pa / goods.suma
            goods = goods.round({'Rr': 2})
            goods.drop(['date'], axis=1, inplace=True)
            menu = goods.copy(deep=True)
            menu.dropna(axis=0, inplace=True)
            menu['profit'] = menu.profit * menu.Rr
            if len(menu):
                menu['date'] = menu.close_date.dt.strftime('%Y-%m-%d')
                menu['date'] = pd.to_datetime(menu.date, format='%Y-%m-%d')
                menu = menu.groupby(['date'],
                                    as_index=False).agg({'profit': 'sum', 'sa': 'sum', 'pv': 'mean'})
            return goods, menu
            pass
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def order_repeat(cls, details):
        """
        检验交易清单中重复的订单，对于两个个交易订单来说，重复意味着两者的code与open_date相同
        :param details:
        :return:
        """
        try:
            must = ['code', 'open_date',]
            if set(must) <= set(details.columns):
                pass
            else:
                raise Exception('This details df must have "code" and "open_date"')
            details['f'] = 1
            details = details.groupby(['code', 'open_date'], as_index=False).agg({'f': 'sum'})
            Rrep = details[details.f > 1].f.sum() / details.f.sum() # 重复率
            return Rrep, details
            pass
        except Exception as e:
            raise e

    @classmethod
    def index_hedging(cls, details, index_code, kline):
        """
        测试利用股指对冲交易信号，以指数的收盘价为准
        :param details:
        :param index_code:
        :param kline:
        :return:
        """
        try:
            index_data = cls.index_profit(sd=details.open_date.min(),
                                          ed=details.close_date.max(),
                                          kline=kline, index_code=index_code)
            details['index_profit'] = 0
            for i, r in details.iterrows():
                ip = index_data[(index_data.date > r['open_date']) &
                                (index_data.date <= r['close_date'])].profit.sum()
                if r.type:
                    # 交易信号为空单，做多股指
                    details.at[i, ['index_profit']] = ip
                else:
                    # 做空股指
                    details.at[i, ['index_profit']] = ip * -1
            return details
            pass
        except Exception as e:
            raise e