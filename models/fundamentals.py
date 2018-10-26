# -*- coding: utf-8 -*-
from datetime import datetime

from .base_model import BaseModel


class BaseTTM(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime),
        ('name', str),  # 板块名称
        ('latest_profit_ratio', float),  # 最新市盈率
        ('stock_num', float),  # 股票家数
        ('loss_num', float),  # 亏损家数
        # 平均市盈率
        ('avg_profit_12m', float),  # 近一年
        ('avg_profit_6m', float),  # 近六月
        ('avg_profit_3m', float),  # 近三月
        ('avg_profit_1m', float),  # 近一月
    ]

    @classmethod
    def trans_data(cls, source_data):
        lpr = source_data[1].strip()
        ap1 = source_data[4].strip()
        ap3 = source_data[5].strip()
        ap6 = source_data[6].strip()
        ap12 = source_data[7].strip()
        _ = {'name': source_data[0].strip(),
             'latest_profit_ratio': float(lpr) if lpr != '--' else 0,
             'stock_nums': int(source_data[2].strip()),
             'loss_num': int(source_data[3].strip()),
             'avg_profit_1m': float(ap1) if ap1 != '--' else 0,
             'avg_profit_3m': float(ap3) if ap3 != '--' else 0,
             'avg_profit_6m': float(ap6) if ap6 != '--' else 0,
             'avg_profit_12m': float(ap12) if ap12 != '--' else 0,
             'date': source_data[-1]  # 这里必须写为 -1，因为有时候中间的项数会变化，但 date 一定是最后一个元素
             }
        return _


class ZYBK_TTM(BaseTTM):
    '''
    主要板块市盈率——滚动市盈率
    '''
    pass


class ZJH_TTM(BaseTTM):
    '''
    证监会行业市盈率——滚动市盈率
    '''
    __fields__ = BaseTTM.__fields__ + [
        ('code', str),
        ('lv', int)
    ]

    @classmethod
    def trans_data(cls, source_data, offset=0):
        _ = BaseTTM.trans_data(source_data)
        _['code'] = source_data[8].strip()
        _['lv'] = source_data[-2]
        return _


class ZZ_TTM(BaseTTM):
    '''
    证监会行业市盈率——滚动市盈率
    '''
    __fields__ = BaseTTM.__fields__ + [
        ('code', str),
        ('lv', int)
    ]

    @classmethod
    def trans_data(cls, source_data, offset=0):
        _ = BaseTTM.trans_data(source_data)
        _['code'] = source_data[8].strip()
        _['lv'] = source_data[-2]
        return _
