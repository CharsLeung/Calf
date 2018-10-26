# -*- coding: utf-8 -*-
from .base_model import BaseModel

class Companyinfo(BaseModel):
    # __table_name__ = 'companyinfo'
    # stock_code = columns.Integer(indicators=True)
    # market = columns.TinyInt()
    # season = columns.Integer()
    # net_profit = columns.Decimal()          # 净利润（万元）
    # npr = columns.Decimal()                 # 净利润增长率(%)
    # turnover = columns.Decimal()            # 营业总收入(万元)  \xd3\xaa\xd2\xb5\xd7\xdc\xca\xd5\xc8\xeb(\xcd\xf2\xd4\xaa)
    # tr = columns.Decimal()                  # 营业总收入增长率(%)
    # roe = columns.Decimal()                 # 加权净资产收益率(%)
    # alr = columns.Decimal()                 # 资产负债比率(%)
    # npcc = columns.Decimal()                # 净利润现金含量(%)
    # beps = columns.Decimal()                # 基本每股收益(元)
    # eps_deduct = columns.Decimal()          # 每股收益-扣除(元)
    # eps_dilute = columns.Decimal()          # 每股收益-摊薄(元)
    # cafps = columns.Decimal()               # 每股资本公积金(元)
    # upps = columns.Decimal()                # 每股未分配利润(元)
    # naps = columns.Decimal()                # 每股净资产(元)
    # epcf = columns.Decimal()                # 每股经营现金流量(元)
    # gr_oncf = columns.Decimal()             # 经营活动现金净流量增长率（%）
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('season', int, -1),
        ('net_profit', float, -1),
        ('npr', float, -1),
        ('turnover', float, -1),
        ('tr', float, -1),
        ('roe', float, -1),
        ('alr', float, -1),
        ('npcc', float, -1),
        ('beps', float, -1),
        ('eps_deduct', float, -1),
        ('eps_dilute', float, -1),
        ('cafps', float, -1),
        ('upps', float, -1),
        ('naps', float, -1),
        ('epcf', float, -1),
        ('gr_oncf', float, -1),
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code'))
        _['market'] = source_data.get('market')
        _['season'] = source_data.get('\xb2\xc6\xce\xf1\xd6\xb8\xb1\xea')
        _['net_profit'] = float(source_data.get('\xbe\xbb\xc0\xfb\xc8\xf3(\xcd\xf2\xd4\xaa)'))
        _['npr'] = float(source_data.get('\xbe\xbb\xc0\xfb\xc8\xf3\xd4\xf6\xb3\xa4\xc2\xca(%)'))
        _['turnover'] = float(source_data.get('\xd3\xaa\xd2\xb5\xd7\xdc\xca\xd5\xc8\xeb(\xcd\xf2\xd4\xaa)'))
        _['tr'] = float(source_data.get('\xd3\xaa\xd2\xb5\xd7\xdc\xca\xd5\xc8\xeb\xd4\xf6\xb3\xa4\xc2\xca(%)'))
        _['roe'] = float(source_data.get('\xbc\xd3\xc8\xa8\xbe\xbb\xd7\xca\xb2\xfa\xca\xd5\xd2\xe6\xc2\xca(%)'))
        _['alr'] = float(source_data.get('\xd7\xca\xb2\xfa\xb8\xba\xd5\xae\xb1\xc8\xc2\xca(%)'))
        _['npcc'] = float(source_data.get('\xbe\xbb\xc0\xfb\xc8\xf3\xcf\xd6\xbd\xf0\xba\xac\xc1\xbf(%)'))
        _['beps'] = float(source_data.get('\xbb\xf9\xb1\xbe\xc3\xbf\xb9\xc9\xca\xd5\xd2\xe6(\xd4\xaa)'))
        _['eps_deduct'] = float(source_data.get('\xc3\xbf\xb9\xc9\xca\xd5\xd2\xe6-\xbf\xdb\xb3\xfd(\xd4\xaa)'))
        _['eps_dilute'] = float(source_data.get('\xc3\xbf\xb9\xc9\xca\xd5\xd2\xe6-\xcc\xaf\xb1\xa1(\xd4\xaa)'))
        _['cafps'] = float(source_data.get('\xc3\xbf\xb9\xc9\xd7\xca\xb1\xbe\xb9\xab\xbb\xfd\xbd\xf0(\xd4\xaa)'))
        _['upps'] = float(source_data.get('\xc3\xbf\xb9\xc9\xce\xb4\xb7\xd6\xc5\xe4\xc0\xfb\xc8\xf3(\xd4\xaa)'))
        _['naps'] = float(source_data.get('\xc3\xbf\xb9\xc9\xbe\xbb\xd7\xca\xb2\xfa(\xd4\xaa)'))
        _['epcf'] = float(source_data.get('\xc3\xbf\xb9\xc9\xbe\xad\xd3\xaa\xcf\xd6\xbd\xf0\xc1\xf7\xc1\xbf(\xd4\xaa)'))
        _['gr_oncf'] = float(source_data.get('\xbe\xad\xd3\xaa\xbb\xee\xb6\xaf\xcf\xd6\xbd\xf0\xbe\xbb\xc1\xf7\xc1\xbf\xd4\xf6\xb3\xa4\xc2\xca(%)'))
        return _