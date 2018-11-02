# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/11/2 16:17
"""
import pandas as pd
from Calf.data import ModelData


class OtherData(ModelData):
    """
    一些莫名其妙的数据库读
    """

    def get_stock_plate(self, code):
        """
        查询某股票属于那个板块，包括细分板块
        :param code:
        :return: df with [big_plate_name, big_plate_index, big_plate_code,
        xf_plate_name, xf_plate_index, xf_plate_code, stock_code]
        """
        try:
            if isinstance(code, str):
                code = [code]
            elif isinstance(code, list):
                pass
            else:
                raise TypeError('this type of code must in (str, list)')
            codes = self.read_data(table_name='stock_code_plate', stock_code={'$in': code},
                                   field={'_id': 0, 'stock_code': 1, 'index_code': 1,
                                          'name': 1, 'hangye': 1})
            if len(codes):
                codes = codes.rename(columns={
                    'hangye': 'xf_plate_code', 'index_code': 'xf_plate_index', 'name': 'xf_plate_name'
                })
                codes['big_plate_code'] = codes.xf_plate_code.map(lambda x: x[0:5])
                plates = self.read_data(table_name='plate', hangye={'$in': codes.big_plate_code.tolist()},
                                        field={'_id': 0, 'hangyezhishu': 1, 'name': 1, 'hangye': 1})
                plates = plates.rename(columns={
                    'hangyezhishu': 'big_plate_index', 'name': 'big_plate_name', 'hangye': 'big_plate_code'
                })
                codes = pd.merge(codes, plates, on=['big_plate_code'])
                return codes
                pass
            else:
                return None
        except Exception as e:
            print(e)
            return None