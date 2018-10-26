from .base_model import BaseModel


class MinuteTime(BaseModel):
    # __table_name__ = 'minutetime'
    # stock_code = columns.Integer(indicators=True)
    # market = columns.TinyInt()
    # date = columns.Integer(indicators=True)
    # current_price = columns.Decimal()
    # volume = columns.Integer()
    # type = columns.Integer()
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('date', int, -1),
        ('current_price', float, -1),
        ('volume', int, -1),
        ('num', int, -1),
        ('type', int, -1),
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['stock_code'] = int(source_data.get('stock_code'))
        _['market'] = source_data.get('market')
        _['date'] = source_data.get('date')
        _['num'] = int(source_data.get('num'))
        _['current_price'] = float(source_data.get('current_price'))
        _['volume'] = int(source_data.get('volume'))
        _['type'] = int(source_data.get('type'))
        return _