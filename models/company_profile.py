from .base_model import BaseModel
from datetime import datetime

class company_profile(BaseModel):
    __fields__ = BaseModel.__fields__ + [
    ('market', int, -1),
    ('stock_code', int, -1)
    ]
    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['region'] = source_data.get('\xc1\xaa\xcf\xb5\xb5\xe7\xbb\xb0')
        _['category'] = source_data.get('\xd0\xd0\xd2\xb5\xc0\xe0\xb1\xf0')
        _['market'] = int(source_data.get('market'))
        _['stock_code'] = int(source_data.get('stock_code'))
        return _