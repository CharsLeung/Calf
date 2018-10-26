from .base_model import BaseModel


class Transaction(BaseModel):
    # __table_name__ = 'transaction'
    # stock_code = columns.Integer(indicators=True)
    # market = columns.TinyInt()
    # date = columns.Integer()
    # time = columns.Integer()
    # price = columns.Decimal()
    # change = columns.BigInt()
    # volume = columns.Integer()
    # amount = columns.Integer()
    # type = columns.Integer()
    __fields__ = BaseModel.__fields__ + [
        ('stock_code', int, -1),
        ('market', int, -1),
        ('date', int, -1),
        ('time', int, -1),
        ('price',float,-1),
        ('change',int,-1),
        ('amount', int, -1),
        ('type', int, -1),
    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        #('time,price,change,volume,amount,type\n')
        _['stock_code'] = int(source_data.get('stock_code'))
        _['market'] = source_data.get('market')
        _['date'] = source_data.get('date')
        hour, minute = source_data.get('time').split(':')
        _['time'] = int(hour + minute)
        _['price'] = float(source_data.get('price'))
        _['change'] = int(source_data.get('change'))
        #_['volume'] = int(source_data.get('volume'))
        _['amount'] = int(source_data.get('amount'))
        _['type'] = int(source_data.get('type'))
        return _