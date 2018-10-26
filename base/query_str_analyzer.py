# -*- coding: utf-8 -*-
import uuid
from datetime import datetime, date, time

from .utils import dict_combine


def analyzer(query_str):
    items = query_str.split(' and ')
    condition = dict()
    for item in items:
        i_list = item.split(' ')

        if len(i_list) >= 3:
            key = i_list[0]
            sign = i_list[1]
            value = verify_values(key, i_list[2:])
            dict_combine(condition, optimse_condition(key, sign, value))
            # print(condition)
            # condition = optimse_condition(key, sign, value, condition)
        else:
            continue
    return condition


def verify_values(key, value_list):
    l = len(value_list)
    if l > 1:
        tv = ''
        #
        # if sign in ['in', 'contains']:
        #     if value_list[0].startswith('[') and value_list[-1].endswith(']'):
        #         tv = value_list
        #         tv[0] = value_list[0][1:]
        #         tv[-1] = value_list[-1][:-1]
        # else:
        if value_list[0].startswith('"') and value_list[-1].endswith('"'):
            if l > 2:
                tv = '{s} {m} {e}'.format(s=value_list[0][1:], m=' '.join(value_list[1:-1]), e=value_list[-1][:-1])
            else:
                tv = value_list[0][1:] + value_list[-1][:-1]
        return tv
    else:
        if '.' in value_list[0]:
            v = float(value_list[0])
        elif '-' in value_list[0]:
            v = uuid.UUID(value_list[0])
        elif 'None' in value_list[0]:
            v = None
        elif key == 'stock_code':
            v = str(value_list[0])
        else:
            v = int(value_list[0])
        return v


# Cassandra sign
# sign_dict = {
#     'in': 'in',
#     'contains': 'contains',
#     '>': 'gt',
#     '>=': 'gte',
#     '<': 'lt',
#     '<=': 'lte'
# }


# MongoDB sign
sign_dict = {
    'in': '$in',
    'notin': '$nin',  # not ready, need debug
    'contains': 'contains',
    '!=': '$not',  # not ready, need debug
    '>': '$gt',
    '>=': '$gte',
    '<': '$lt',
    '<=': '$lte'
}


def optimse_condition(key, sign, value):
    if key == 'date':
        if value is None:
            value = datetime.combine(date.today(), time.min)
        else:
            import re
            r = re.search('(^\d{4})[./-]*(\d{1,2})[./-]*(\d{1,2}$)', str(value))
            value = datetime(year=int(r.group(1)), month=int(r.group(2)), day=int(r.group(3)))
    # elif key == 'stock_code':
    #     if not value.startswith('"'):
    #         value = '"{}'.format(value)
    #     if not value.endswith('"'):
    #         value = '{}"'.format(value)
    if sign == '=':
        return {key: value}
    elif sign in sign_dict.keys():
        # Cassandra
        # k = key + '__' + sign_dict[sign]
        # return {k: value}
        # MongoDB
        return {key: {sign_dict[sign]: value}}


# if __name__ == '__main__':
#     cql = 'stock_code = "600000" and date < 20170701 and low > 18.0 and test = "qwer rewq weqr qrwe" and low < 20.0'
#     # cql = 'id in [123,456]'
#     print(analyzer(cql))
