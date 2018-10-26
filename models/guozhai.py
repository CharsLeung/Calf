# -*- coding: utf-8 -*-
from datetime import datetime

from model_data_get.Controller.utils import list_combine, log
from .base_model import BaseModel


class GuoZhai(BaseModel):
    __table_name__ = 'GuoZhai'
    # date = columns.Integer(indicators=True)
    # fenxiang = columns.TinyInt(indicators=True)  # 分项 0-总值，1-1年以下，2-1~3年，3-3~5年，4-5~7年，5-7~10年，6-10年以上
    # cfzs = columns.Decimal()                # 财富总数
    # qjzs = columns.Decimal()                # 全价总数
    # jjzs = columns.Decimal()                # 净价总数
    # pjszfjq = columns.Decimal()             # 平均市值法久期（年）
    # pjxjlfjq = columns.Decimal()            # 平均现金流法久期（年）
    # pjszftx = columns.Decimal()             # 平均市值法凸性
    # pjxjlftx = columns.Decimal()            # 平均现金流法凸性
    # pjdqsyl = columns.Decimal()             # 平均现金流法到期收益率（%）
    # pjszfdqsy = columns.Decimal()           # 平均市值法到期收益率（%）
    # pjjdjz = columns.Decimal()              # 平均几点价值（元）
    # pjdcq = columns.Decimal()               # 平均代偿期（年）
    # pjpxl = columns.Decimal()               # 平均派息率（%）
    # zszsz = columns.Decimal()               # 指数上日总市值（亿元）
    # cfzszdf = columns.Decimal()             # 财富指数涨跌幅（%）
    # qjzszdf = columns.Decimal()             # 全价指数涨跌幅（%）
    # jjzszdf = columns.Decimal()             # 净价指数涨跌幅（%）
    # xqjsl = columns.Decimal()               # 现券结算量（亿元）
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime, -1),
        ('fenxiang', int, -1),  # 分项 0-总值，1-1年以下，2-1~3年，3-3~5年，4-5~7年，5-7~10年，6-10年以上
        ('cfzs', float, -1),  # 财富总数
        ('qjzs', float, -1),  # 全价总数
        ('jjzs', float, -1),  # 净价总数
        ('pjszfjq', float, -1),  # 平均市值法久期（年）
        ('pjxjlfjq', float, -1),  # 平均现金流法久期（年）
        ('pjszftx', float, -1),  # 平均市值法凸性
        ('pjxjlftx', float, -1),  # 平均现金流法凸性
        ('pjdqsyl', float, -1),  # 平均现金流法到期收益率（%）
        ('pjszfdqsy', float, -1),  # 平均市值法到期收益率（%）
        ('pjjdjz', float, -1),  # 平均几点价值（元）
        ('pjdcq', float, -1),  # 平均代偿期（年）
        ('pjpxl', float, -1),  # 平均派息率（%）
        ('zszsz', float, -1),  # 指数上日总市值（亿元）
        ('cfzszdf', float, -1),  # 财富指数涨跌幅（%）
        ('qjzszdf', float, -1),  # 全价指数涨跌幅（%）
        ('jjzszdf', float, -1),  # 净价指数涨跌幅（%）
        ('xqjsl', float, -1),  # 现券结算量（亿元）
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = source_data.split('%')
        rl = list()
        if len(_) == 103:
            sp = '-'
            year, month, day = _[0].split(sp)
            date = int(year + month + day)
            title = ['date', 'fenxiang', 'cfzs', 'qjzs', 'jjzs',
                     'pjszfjq', 'pjxjlfjq', 'pjszftx', 'pjxjlftx',
                     'pjdqsyl', 'pjszfdqsy', 'pjjdjz', 'pjdcq', 'pjpxl',
                     'zszsz', 'cfzszdf', 'qjzszdf', 'jjzszdf', 'xqjsl']
            l = len(_)
            f = 0
            d = [date, 0]
            for i in range(1, l):
                try:
                    data, fx = _[i].split('_')
                    if int(fx[0]) == f:
                        pass
                    else:
                        rl.append(list_combine(title, d))
                        f = int(fx)
                        d = [date, f]
                    d.append(float(data))
                except Exception as e:
                    log('GuoZhai trans error: ', e.message)
                    continue
            rl.append(list_combine(title, d))  # fx 为 6 时，for循环已经结束，导致 fx = 6 的所有数据没有放入 rl 中
        return rl

    @classmethod
    def insert_if_not_exist(cls, *args, **kwargs):
        _ = kwargs if len(kwargs) else args[0]
        ne = list()
        for item in _:
            if cls.not_exists(date=item['date'], fenxiang=item['fenxiang']):
                ne.append(item)
        cls.insert_batch(ne)
