# -*- coding: utf-8 -*-
from .base_model import BaseModel


class Capital(BaseModel):
    # __table_name__ = 'capital'
    # stock_code = columns.Integer(indicators=True)
    # market = columns.TinyInt()
    # date = columns.Integer()
    # capitalization = columns.Decimal()           # 总股本（万股）
    # circulationstock_A = columns.Decimal()       # 流通A股(万股)
    # real_circulationstock_A = columns.Decimal()  # 实际流通A股(万股）
    # capitalization_change = columns.Decimal()    # 股本较上期变化(%)
    # market_capitalization = columns.Decimal()    # 截止当天总市值（亿元）
    # market_capitalization_change = columns.Decimal()    # 总市值较上期变化(%)
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('date', int, -1),
        ('capitalization', float, -1),
        ('circulationstock_A', float, -1),
        ('real_circulationstock_A', float, -1),
        ('capitalization_change', float, -1),
        ('market_capitalization', float, -1),
        ('market_capitalization_change', float, -1),
    ]


    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code'))
        _['market'] = source_data.get('market')
        _['date'] = source_data.get('\xb1\xe4\xb8\xfc\xc8\xd5\xc6\xda')
        _['capitalization'] = float(source_data.get('\xd7\xdc\xb9\xc9\xb1\xbe(\xcd\xf2\xb9\xc9)'))
        _['circulationstock_A'] = float(source_data.get('\xc1\xf7\xcd\xa8A\xb9\xc9(\xcd\xf2\xb9\xc9)'))
        _['real_circulationstock_A'] = float(source_data.get('\xca\xb5\xbc\xca\xc1\xf7\xcd\xa8A\xb9\xc9(\xcd\xf2\xb9\xc9)'))
        _['capitalization_change'] = float(source_data.get('\xb9\xc9\xb1\xbe\xbd\xcf\xc9\xcf\xc6\xda\xb1\xe4\xbb\xaf(%)'))
        _['market_capitalization'] = float(source_data.get('\xbd\xd8\xd6\xb9\xb5\xb1\xcc\xec\xd7\xdc\xca\xd0\xd6\xb5(\xd2\xda\xd4\xaa)'))
        _['market_capitalization_change'] = float(source_data.get('\xd7\xdc\xca\xd0\xd6\xb5\xbd\xcf\xc9\xcf\xc6\xda\xb1\xe4\xbb\xaf(%)'))
        return _