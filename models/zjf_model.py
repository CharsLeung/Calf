import datetime

from Calf.models.base_model import BaseModel


class risk_and_position(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('date', datetime),
        ('risk_index', int),
        ('sug_position', int)
    ]


class Risk_and_Position(risk_and_position):
    pass


class Kline_data_update_mark(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('date', datetime, -1),
        ('status', int, 0),
        ('kline', str, ''),
        ('other', str, '')
    ]
    # send_date = "{'model': 'macd', 'status':1,'time':'%s','kline':%s}


class kline_data_update_mark(Kline_data_update_mark):
    # __tablename__ = 'kline_data_update_mark'
    pass


class risk(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('date', datetime),
        ('risk_index', int),
    ]


class Risk(risk):
    pass


class position(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('date', datetime),
        ('sug_position', int)
    ]


class Position(risk):
    pass


class inflexion(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('date', datetime),
        ('strategy', str),
        ('date_list', list),
        ('other', str),
    ]


class Inflexion(inflexion):
    pass


class buy_point(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', str),
        ('date', datetime),
        ('buy_date', datetime),
        ('strategy', str),
        ('buy_sell', int),  # 1表示买 -1表示卖
        ('other', str),
    ]


class Buy_Point(inflexion):
    pass
