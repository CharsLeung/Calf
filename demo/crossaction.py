# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/21 10:49
"""
import datetime as dt

import multiprocessing

from Calf import ModelAction
from Calf import KlineData as kd
from Calf.utils import trading
from Calf.demo.crossmodel import crossmodel
import pandas as pd
import numpy as np


class CrossAction(ModelAction):
    """
    这就是一个模型的核心驱动类,我们以中国A股为例
    """

    def batch_his(self, start, end):
        # 方案一，我们不使用多进程，直接对全市场的股票进行历史信号采集
        codes = kd.field(table_name='XDXR_day', field_name='stock_code')
        traitors = pd.DataFrame([])
        # 为了更快的演示程序，我们只计算10只股票
        for sc in codes[0:9]:
            _rls = self.one_his(sc, start, end)
            traitors = pd.concat([traitors, _rls], axis=0, join='outer', ignore_index=True)
        # 最后我们建议将traitors存入数据库，这肯定需要自己去执行
        # 为了方便演示，这个不存入数据库,直接输出
        print(traitors.head(2).T)
        # 为了区别开每一次历史数据的采集结果，我们添加一个字段version
        traitors['version'] = 1
        # 为了方便下一步的验证，我们将这个结果保存为一个csv文件
        traitors.to_csv(path_or_buf='D:traitors.csv', index=False)
        pass

    @classmethod
    def probing(cls, **kwargs):
        pass

    @classmethod
    def signals_summary(cls, **kwargs):
        pass

    @classmethod
    def orders_summary(cls, **kwargs):
        pass

    def one(self, code, sd, ed):
        data = kd.read_data(code=code, start_date=sd, end_date=ed, kline='XDXR_day')
        rl = crossmodel(data).real_signal()
        return rl
        pass

    @classmethod
    def real(cls, **kwargs):
        # 包装一个函数
        def real_func(di):
            return CrossAction(di['kline'], di['date'], di['task'], di['codes']).batch()

        scs = np.array(kd.field('XDXR_day', 'stock_code'))
        bt = dt.timedelta(2018, 3, 21)
        args = [{'kline': 'XDXR_day', 'date': bt, 'task': i, 'codes': scs} for i in range(1, 5, 1)]
        pool = multiprocessing.Pool(processes=4)
        result = pool.map(real_func, args)
        pool.close()
        pool.join()
        [print(r) for r in result]
        pass

    def one_his(self, code, sd, ed):
        data = kd.read_data(code=code, start_date=sd, end_date=ed, kline='XDXR_day')
        rls = crossmodel(data).his_signals()
        return rls
        pass

    @classmethod
    def is_trade_day(cls, date):
        return trading.is_trade_day(date)

    def batch(self, **kwargs):
        # 这里我们演示使用多线程完成实时信号的采集过程
        # Calf的策略开发规范明确了一个’窄依赖‘的执行流
        # 所以我们只要正确划分市场、品种、Symbol就不会
        # 影响多进程的执行结果
        # 本例演示的是针对于中国A股市场，股票
        # 所以我们只需划分股票代码
        codes = self.codes
        # 这里我们按进程的编号，把所有的股票代码划分了4个块
        # 每个进程根据其进程代码负责相应的块
        l = codes.size // 4
        start = (self.task - 1) * l if 0 < self.task < 5 else 0
        end = self.task * l if 0 < self.task < 4 else codes.size - 1
        print('Task:', self.task, 'Aims:', self.date_time, 'SI:', start, 'EI:', end, 'for:', self.kline)
        ed = self.date_time - dt.timedelta(days=60)
        traitors = pd.DataFrame([self.one(sc, self.date_time, ed) for sc in codes[start:end]])
        traitors['version'] = 24
        # 为了方便下一步的验证，我们将这个结果保存为一个csv文件
        traitors.to_csv(path_or_buf='D:real_traitors_{}.csv'.format(self.task), index=False)
        pass

    @classmethod
    def start(cls):
        print('开盘前处理的任务', dt.datetime.now())

    @classmethod
    def execute(cls):
        print('盘中不间断的任务', dt.datetime.now())

    @classmethod
    def end(cls):
        print('盘后处理的任务', dt.datetime.now())

    def __init__(self, kline, date_time, task=0, codes=None):
        self.task = task
        self.kline = kline
        self.date_time = date_time
        self.codes = codes if codes is not None else np.array(kd.field(kline, 'stock_code'))
        pass


if __name__ == '__main__':
    import datetime as dt

    s = dt.datetime(2017, 1, 1)
    e = dt.datetime(2018, 1, 1)
    CrossAction(kline='XDXR_day', date_time=e).probing()
    # 这样我们就把A股市场的所有股票的历史数据采集下来，并保存在一个位置
    pass
