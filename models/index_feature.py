from .base_model import BaseModel
from datetime import datetime

class index_feature(BaseModel):
    __fields__ = BaseModel.__fields__ + [
        ('amount', int, -1),
        ('close', float, -1),
        ('date', int, -1),
        ('high', float, -1),
        ('low', float, -1),
        ('market', int, -1),
        ('open', float, -1),
        ('stock_code', int, -1),
        ('volume', float, -1),
        ('last_close', float, -1)
    ]

    @classmethod
    def trans_data(cls, source_data):
        # _ = dict()
        source_data['amount'] = int(source_data.get('amount'))
        # source_data['queue_brar_sum1'] = object(source_data.get('queue_brar_sum1'))
        # source_data['queue_brar_sum2'] = object(source_data.get('queue_brar_sum2'))
        # source_data['queue_brar_sum3'] = object(source_data.get('queue_brar_sum3'))
        # source_data['queue_brar_sum4'] = object(source_data.get('queue_brar_sum4'))
        # _['close'] = float(source_data.get('close'))
        # d = str(int(source_data.get('date')))
        # d = source_data.get('date')
        # source_data['date'] = datetime(year=int(d[:4]), month=int(d[4:6]), day=int(d[6:]))
        # _['high'] = float(source_data.get('high'))
        # _['low'] = float(source_data.get('low'))
        source_data['market'] = int(source_data.get('market'))
        # _['open'] = float(source_data.get('open'))
        source_data['stock_code'] = int(source_data.get('stock_code'))
        return source_data