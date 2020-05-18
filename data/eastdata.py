# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2019-06-11 13:21
"""
import requests
import pandas as pd
import datetime as dt


class EastNotices:
    TYPE_NOTICES = {
        'ALL': 0,
        'MAJOR': 1,
        'FINANCE_REPORT': 2,
        'CAPITAL_RAISING': 3,
        'RISK_TIP': 4,
        'RECAPITALIZE': 5,
        'INFO_MODIFY': 6,
        'HOLD_MODIFY': 7
    }

    def __init__(self, code, page_index=1, page_size=50,
                 deadline=None):
        self.code = code
        self.page_index = page_index
        self.page_size = page_size
        self.deadline = deadline
        self.init_flag = True
        self.close_flag = False
        self.AllTotalCount = 0
        self.AllPages = 1
        pass

    def reset(self):
        self.page_index = 1
        self.init_flag = True
        self.close_flag = False
        pass

    def urls(self, tp):
        _ = ''
        if tp == self.TYPE_NOTICES['ALL']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=KkDtqWKz&SecNodeType=' \
                '0&FirstNodeType=0&rt=52007673'
        if tp == self.TYPE_NOTICES['MAJOR']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=WmufSGNt&SecNodeType=' \
                '0&FirstNodeType=5&rt=52008070'
        if tp == self.TYPE_NOTICES['FINANCE_REPORT']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=DMHRqKbq&SecNodeType=' \
                '0&FirstNodeType=1&rt=52008152'
        if tp == self.TYPE_NOTICES['CAPITAL_RAISING']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=laAQQPtq&SecNodeType=' \
                '0&FirstNodeType=2&rt=52008160'
        if tp == self.TYPE_NOTICES['RISK_TIP']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=QKpNPMVg&SecNodeType=' \
                '0&FirstNodeType=3&rt=52008164'
        if tp == self.TYPE_NOTICES['RECAPITALIZE']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=IhtquGBD&SecNodeType=' \
                '0&FirstNodeType=6&rt=52008167'
        if tp == self.TYPE_NOTICES['INFO_MODIFY']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=eqXSrweY&SecNodeType=' \
                '0&FirstNodeType=4&rt=52008169'
        if tp == self.TYPE_NOTICES['HOLD_MODIFY']:
            _ = 'http://data.eastmoney.com/notices/getdata.ashx?' \
                'StockCode={code}&CodeType=1&PageIndex={PageIndex}' \
                '&PageSize={PageSize}&jsObj=XuWxQsIM&SecNodeType=' \
                '0&FirstNodeType=7&rt=52008175'
        _ = _.format(
                 code=self.code,
                 PageIndex=self.page_index,
                 PageSize=self.page_size
                )
        return _

    def get(self, tp):
        data = requests.get(self.urls(tp))
        data = data.text[15:]
        data = data[:-1].replace('null', 'None') \
            .replace('false', 'False').replace('true', 'True')
        data = eval(data)
        if self.init_flag:
            self.AllTotalCount = data['TotalCount']
            self.AllPages = data['pages']
            self.init_flag = False
            if data['TotalCount'] == 0:
                self.close_flag = True
                return pd.DataFrame()
        nts = data['data']
        notices = []
        for n in nts:
            notices.append(dict(
                date=n['NOTICEDATE'][:19],
                title=n['NOTICETITLE'],
                types=[x['COLUMNNAME'] for x in n['ANN_RELCOLUMNS']],
                eutime=n['EUTIME'][:19],
                url=n['Url']
            ))
        notices = pd.DataFrame(notices)
        notices['date'] = pd.to_datetime(notices.date)
        notices['eutime'] = pd.to_datetime(notices.eutime)
        if self.deadline is not None:
            if notices.date.min() <= self.deadline:
                self.close_flag = True
            notices = notices[notices.date >= self.deadline]

        if len(notices) < self.page_size:
            self.close_flag = True

        self.page_index += 1
        return notices
        pass

    def get_notices(self, tp):
        nts = self.get(tp)
        yield nts
        for i in range(2, self.AllPages + 1):
            if self.close_flag:
                self.reset()
                break
            nts = self.get(tp)
            yield nts
        pass


class EastData:

    @classmethod
    def get_all_notices(cls):
        pass


# ns = EastNotices('002885', page_size=10, deadline=dt.datetime(2018, 1, 1)).get_notices(EastNotices.TYPE_NOTICES['RISK_TIP'])
# for n in ns:
#     print(n.head())
