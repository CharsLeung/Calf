# -*- coding: utf-8 -*-
from .base_model import BaseModel


class Feature(BaseModel):
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
        ('last_close', float, -1),
        ('last_high', float, -1),
        ('last_low', float, -1),
        ('capital', float, -1),
        ('K', float, -1),
        ('D', float, -1),
        ('J', float, -1),
        ('ma5', float, -1),
        ('ma10', float, -1),
        ('ma20', float, -1),
        ('ma30', float, -1),
        ('ma60', float, -1),
        ('ma120', float, -1),
        ('V_ma60', float, -1),
        ('v_ma5', float, -1),
        ('v_ma10', float, -1),
        ('v_ma20', float, -1),
        ('sema', float, -1),
        ('lema', float, -1),
        ('dif', float, -1),
        ('dea', float, -1),
        ('macd', float, -1),
        ('RSI1', float, -1),
        ('RSI2', float, -1),
        ('RSI3', float, -1),
        ('PDI', float, -1),
        ('MDI', float, -1),
        ('ADX', float, -1),
        ('ADXR', float, -1),
        ('DIF', float, -1),
        ('DIFMA', float, -1),
        ('TRIX', float, -1),
        ('MATRIX', float, -1),
        ('BR', float, -1),
        ('AR', float, -1),
        ('CR', float, -1),
        ('MA1', float, -1),
        ('MA2', float, -1),
        ('MA3', float, -1),
        ('MA4', float, -1),
        ('VR', float, -1),
        ('MAVR', float, -1),
        ('OBV', float, -1),
        ('MAOBV', float, -1),
        ('SWL', float, -1),
        ('SWS', float, -1),
        ('EMV', float, -1),
        ('MAEMV', float, -1),
        ('WR1', float, -1),
        ('WR2', float, -1),
        ('CCI', float, -1),
        ('ROC', float, -1),
        ('MAROC', float, -1),
        ('MTM', float, -1),
        ('MTMMA', float, -1),
        ('BOLL', float, -1),
        ('UB', float, -1),
        ('LB', float, -1),
        ('PSY', float, -1),
        ('PSYMA', float, -1),

    ]

    @classmethod
    def trans_data(cls, source_data):
        _ = dict()
        _['amount'] = int(source_data.get('amount'))
        _['close'] = float(source_data.get('close'))
        _['date'] = int(source_data.get('date'))
        _['high'] = float(source_data.get('high'))
        _['low'] = float(source_data.get('low'))
        _['market'] = source_data.get('market')
        _['open'] = float(source_data.get('open'))
        _['stock_code'] = int(source_data.get('stock_code'))
        _['volume'] = float(source_data.get('volume'))
        _['last_close'] = float(source_data.get('last_close'))
        _['last_high'] = float(source_data.get('last_high'))
        _['last_low'] = float(source_data.get('last_low'))
        _['capital'] = float(source_data.get('capital'))
        _['K'] = float(source_data.get('K'))
        _['D'] = float(source_data.get('D'))
        _['J'] = float(source_data.get('J'))
        _['ma5'] = float(source_data.get('ma5'))
        _['ma10'] = float(source_data.get('ma10'))
        _['ma30'] = float(source_data.get('ma30'))
        _['ma60'] = float(source_data.get('ma60'))
        _['ma120'] = float(source_data.get('ma120'))
        _['v_ma60'] = float(source_data.get('v_ma60'))
        _['v_ma5'] = float(source_data.get('v_ma5'))
        _['v_ma10'] = float(source_data.get('v_ma10'))
        _['v_ma20'] = float(source_data.get('v_ma20'))
        _['sema'] = float(source_data.get('sema'))
        _['lema'] = float(source_data.get('lema'))
        _['dif'] = float(source_data.get('dif'))
        _['dea'] = float(source_data.get('dea'))
        _['macd'] = float(source_data.get('macd'))
        _['RSI1'] = float(source_data.get('RSI1'))
        _['RSI2'] = float(source_data.get('RSI2'))
        _['RSI3'] = float(source_data.get('RSI3'))
        _['PDI'] = float(source_data.get('PDI'))
        _['MDI'] = float(source_data.get('MDI'))
        _['ADX'] = float(source_data.get('ADX'))
        _['ADXR'] = float(source_data.get('ADXR'))
        _['DIF'] = float(source_data.get('DIF'))
        _['DIFMA'] = float(source_data.get('DIFMA'))
        _['TRIX'] = float(source_data.get('TRIX'))
        _['MATRIX'] = float(source_data.get('MATRIX'))
        _['BR'] = float(source_data.get('BR'))
        _['AR'] = float(source_data.get('AR'))
        _['CR'] = float(source_data.get('CR'))
        _['MA1'] = float(source_data.get('MA1'))
        _['MA2'] = float(source_data.get('MA2'))
        _['MA3'] = float(source_data.get('MA3'))
        _['MA4'] = float(source_data.get('MA4'))
        _['VR'] = float(source_data.get('VR'))
        _['MAVR'] = float(source_data.get('MAVR'))
        _['OBV'] = float(source_data.get('OBV'))
        _['MAOBV'] = float(source_data.get('MAOBV'))
        _['SWL'] = float(source_data.get('SWL'))
        _['SWS'] = float(source_data.get('SWS'))
        _['EMV'] = float(source_data.get('EMV'))
        _['MAEMV'] = float(source_data.get('MAEMV'))
        _['WR1'] = float(source_data.get('WR1'))
        _['WR2'] = float(source_data.get('WR2'))
        _['CCI'] = float(source_data.get('CCI'))
        _['ROC'] = float(source_data.get('ROC'))
        _['MAROC'] = float(source_data.get('MAROC'))
        _['MTM'] = float(source_data.get('MTM'))
        _['MTMMA'] = float(source_data.get('MTMMA'))
        _['BOLL'] = float(source_data.get('BOLL'))
        _['UB'] = float(source_data.get('UB'))
        _['LB'] = float(source_data.get('LB'))
        _['PSY'] = float(source_data.get('PSY'))
        _['PSYMA'] = float(source_data.get('PSYMA'))
        return _

    @classmethod
    def insert_if_not_exist(cls, *args, **kwargs):
        _ = kwargs if len(kwargs) else args[0]
        ne = list()
        for item in _:
            if cls.not_exists(date=item['date'], fenxiang=item['fenxiang']):
                ne.append(item)
        cls.insert_batch(ne)
