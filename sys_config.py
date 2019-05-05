# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/3/30 13:15
"""
import json
import datetime as dt
import xml.etree.ElementTree as ET

from Calf import project_dir


class config(object):

    @classmethod
    def default_market_id(cls, info_type):
        """

        :param info_type:
        :return:
        """
        if info_type == 'MarketInfo':
            tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
            root = tree.getroot()
            if root.attrib['default_market']:
                return root.attrib['default_market']
            else:
                return None
        elif info_type == 'MarketHolidays':
            tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
            root = tree.getroot()
            if root.attrib['default_market']:
                return root.attrib['default_market']
            else:
                return None
        else:
            return None

    @classmethod
    def switch_default_market(cls, default_market):
        """
        切换默认的执行市场
        :param default_market: 市场ID
        :return:
        """
        tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
        root = tree.getroot()
        market_id_exist_flag = False
        for e in root:
            if e.attrib['id'] == default_market:
                market_id_exist_flag = True
                break
        if not market_id_exist_flag:
            raise Exception('this market id "%s" not exist' % default_market)
        root.attrib = {'default_market': default_market}

        tree_ = ET.parse(project_dir + "/Calf/MarketInfo.xml")
        root_ = tree_.getroot()
        market_id_exist_flag = False
        for e in root_:
            if e.attrib['id'] == default_market:
                market_id_exist_flag = True
                break
        if not market_id_exist_flag:
            raise Exception('this market id "%s" not exist' % default_market)
        root_.attrib = {'default_market': default_market}

        tree.write(project_dir + "/Calf/MarketHolidays.xml")
        tree_.write(project_dir + "/Calf/MarketInfo.xml")

    @classmethod
    def add_holidays(cls, market, holidays):
        """
        为证券市场添加节假日信息。周末休市是全球证券市场普遍的
        规则，对于那些交易所的特殊安排需要我们特殊处理，比如
        中国A股的法定节假日，有很多不是在周末，我们需要手动添加
        它们。
        :param market:
        :param holidays:
        :return:
        """
        try:
            shs = list()
            for sh in holidays:
                h = dt.datetime.strptime(sh, '%Y-%m-%d')
                shs.append(h.strftime('%Y-%m-%d'))
        except Exception:
            raise Exception('this holidays Must be a date string list like "[2018-01-01"]')
        tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
        root = tree.getroot()
        for e in root:
            if e.attrib['id'] == market:
                raise Exception('this market id "%s" already exists' % market)
        mk = ET.Element('market')
        mk.attrib = {'id': market}
        for d in shs:
            m = ET.Element('day')
            m.text = d
            mk.append(m)
        root.append(mk)
        tree.write(project_dir + "/Calf/MarketHolidays.xml")

    @classmethod
    def load_market_holidays(cls, market, by='file', **kwargs):
        if by == 'file':
            tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
            root = tree.getroot()
            for e in root:
                if e.attrib['id'] == market:
                    days = e.findall('day')
                    return [d.text for d in days]
        else:
            # by db
            exchanges = {'China_Stock_A': 'SSE', 'USA_Stock': 'NYSE', 'HK_Stock': 'HKEX'}
            if market in exchanges.keys():
                from Calf.data import ModelData as md
                if 'start_date' in kwargs.keys():
                    sd = kwargs['start_date']
                else:
                    sd = dt.datetime.now() - dt.timedelta(days=365)
                if 'end_date' in kwargs.keys():
                    ed = kwargs['end_date']
                else:
                    ed = dt.datetime.now() + dt.timedelta(days=365)
                hds = md().read_data('MarketCalendar', exchange=exchanges[market],
                                     open=0, date={'$gte': sd, '$lte': ed})
                return hds.date.tolist()
            else:
                Exception("not find this market: {}'s calendar data in database".format(market))
        raise Exception('not find this market id "%s"' % market)

    @classmethod
    def update_holiday(cls, market, holiday):
        """
        为某个市场添加一天假日
        :param market:
        :param holiday:
        :return:
        """
        try:
            h = dt.datetime.strptime(holiday)
            holiday = h.strftime('%Y-%m-%d')
        except Exception:
            raise Exception('this holiday Must be a date string like "2018-01-01"')
        tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
        root = tree.getroot()
        node = root.findall("./market/[@id='{}']".format(market))
        if len(node):
            for n in node:
                day = ET.Element('day')
                day.text = holiday
                n.append(day)
            tree.write(project_dir + "/Calf/MarketInfo.xml")
        else:
            raise Exception('not find this market id "%s"' % market)

    @classmethod
    def delete_holidays(cls, market):
        """
        删除某个市场关于节假日的信息
        :param market:
        :return:
        """
        tree = ET.parse(project_dir + "/Calf/MarketHolidays.xml")
        root = tree.getroot()
        node = root.findall("./market/[@id='{}']".format(market))
        if len(node):
            for n in node:
                root.remove(n)
            tree.write(project_dir + "/Calf/MarketHolidays.xml")
        else:
            raise Exception('not find this market id "%s"' % market)

    @classmethod
    def load_market_info(cls, market):
        tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
        root = tree.getroot()
        for e in root:
            if e.attrib['id'] == market:
                trade_date = e.find('trade_date')
                ao = trade_date.find('am_open').text
                ac = trade_date.find('am_close').text
                po = trade_date.find('pm_open').text
                pc = trade_date.find('pm_close').text
                return dict(market=market, am_open=ao, am_close=ac, pm_open=po, pm_close=pc)
        raise Exception('not find this market id "%s"' % market)

    @classmethod
    def add_market_info(cls, **kw):
        tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
        root = tree.getroot()
        for e in root:
            if e.attrib['id'] == kw['id']:
                raise Exception('this market id "%s" already exists' % kw['id'])
        market = ET.Element('market')
        market.attrib = {'id': kw['id']}
        trade_date = ET.Element('trade_date')
        for k, v in zip(kw.keys(), kw.values()):
            m = ET.Element(k)
            m.text = v
            trade_date.append(m)

        market.append(trade_date)
        root.append(market)
        tree.write(project_dir + "/Calf/MarketInfo.xml")

    @classmethod
    def delete_market_info(cls, market):
        tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
        root = tree.getroot()
        node = root.findall("./market/[@id='{}']".format(market))
        if len(node):
            for n in node:
                root.remove(n)
            tree.write(project_dir + "/Calf/MarketInfo.xml")
        else:
            raise Exception('not find this market id "%s"' % market)

    @classmethod
    def update_market_info(cls, node_tag, attrib=None, value=None, type='text'):
        if type == 'text':
            tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
            root = tree.getroot()
            node = root.find(node_tag)
            node.text = value
        elif type == 'attrib':
            tree = ET.parse(project_dir + "/Calf/MarketInfo.xml")
            root = tree.getroot()
            node = root.findall("./market/[@id='test']")
            print(len(node))
            node[0].set(attrib, value)
            print(node[0].attrib['id'])
        else:
            raise Exception('type must in (text, attrib)')

    @classmethod
    def add_database(cls, id, host, dbname=None, username=None, password=None, dbauth=None, **kw):
        """
        为Calf系统添加一个目标数据库
        :param id:这个目标数据库的标识
        :param host:数据库的地址,形如‘127.0.0.1:27017’，
        或‘127.0.0.1’这样将使用默认的端口，也可以同时配置多个主机，
        比如‘127.0.0.1:27017,127.0.0.2:27018’,这样配置是为了访问分片mongos
        :param dbname:库名
        :param username:用户名
        :param password:密码
        :param dbauth:用户角色
        :return:
        """
        try:
            db = dict(host=host)
            if dbname is not None:
                db['dbname'] = dbname
            if username is not None and password is not None:
                db['username'] = username
                db['password'] = password
            if dbauth is not None:
                db['dbauth'] = dbauth
            db = dict(db, **kw)
            with open(project_dir + '/Calf/db_config.json', 'r', encoding='utf-8') as file:
                content = json.load(file)
                file.close()
                del file
            keys = content.keys()
            if id in keys:
                raise Exception('this id "%s" already exists' % id)
            else:
                content[id] = db
                with open(project_dir + '/Calf/db_config.json', 'w', encoding='utf-8') as file:
                    file.write(json.dumps(content))
        except Exception:
            raise Exception

    @classmethod
    def update_database(cls, id, **kw):
        """
        更新Calf系统中的目标数据库参数
        :param id:
        :param kw:
        :return:
        """
        with open(project_dir + '/Calf/db_config.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
            file.close()
        keys = content.keys()
        if id not in keys:
            raise Exception('this id "%s" not exists in dbs' % id)
        else:
            sub_keys = content[id].keys()
            for k, v in zip(kw.keys(), kw.values()):
                if k in sub_keys:
                    content[id][k] = v
                else:
                    raise Exception('not find this key:"%s" in original file' % k)
            with open(project_dir + '/Calf/db_config.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(content))

    @classmethod
    def delete_database(cls, id):
        """
        删除某个数据库配置
        :param id:
        :return:
        """
        with open(project_dir + '/Calf/db_config.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
            file.close()
        with open(project_dir + '/Calf/db_config.json', 'w', encoding='utf-8') as file:
            content.pop(id)
            file.write(json.dumps(content))
            file.close()


pass


# config.add_holiday()
# d = config.load_market_info('China_stock_A')
# print(d)
# config.add_market_info(id='test', am_open='as', am_close='ac', pm_open='po', pm_close='pc')
# config.update_market_info(node_tag='market', attrib='id', value='leung', type='attrib')
# config.delete_market_info('test')
# config.delete_holidays(market='China_Stock_A')
# config.add_holidays(market='China_Stock_A', holidays=holidays)

# print(config.load_market_holidays(market='China_Stock_A', by='db'))
# config.switch_default_market('China_Stock_A')


def f1():
    import pandas as pd
    from Calf.data import WebData as wd

    data = wd.Stooq_index_data('SPX')
    # print(data.head())
    # print(data.tail())
    data = data[data.date >= dt.datetime(1900, 1, 1)]

    tdr = data.loc[:, ['date']]
    tdr['open'] = 1

    ald = pd.DataFrame()
    ald['date'] = pd.date_range(data.date.min(), data.date.max())

    days = pd.merge(ald, tdr, on=['date'], how='outer')
    days.fillna(0, inplace=True)

    d3 = pd.DataFrame([])
    d3['date'] = pd.to_datetime(config.load_market_holidays('USA_Stock'))
    d3 = d3[d3.date > data.date.max()]
    d3['open'] = 0

    d2 = pd.DataFrame([])
    d2['date'] = pd.date_range(
        data.date.max() + dt.timedelta(days=1),
        d3.date.max()
    )

    d3 = pd.merge(d2, d3, how='outer', on=['date'])
    d3.fillna(1, inplace=True)
    for i, r in d3.iterrows():
        if r.date.weekday() in (5, 6):
            d3.at[i, ['open']] = 0

    days = pd.concat([days, d3])
    days['exchange'] = 'NYSE'
    days['open'] = days.open.astype('int')

    # from Calf.data import ModelData as md
    #
    # md().insert_data('MarketCalendar', days)
    pass


# f1()

def f2():
    import pandas as pd
    from Calf.data import WebData as wd

    data = wd.Stooq_index_data('HSI')
    # print(data.head())
    # print(data.tail())
    data = data[data.date >= dt.datetime(1900, 1, 1)]

    tdr = data.loc[:, ['date']]
    tdr['open'] = 1

    ald = pd.DataFrame()
    ald['date'] = pd.date_range(data.date.min(), data.date.max())

    days = pd.merge(ald, tdr, on=['date'], how='outer')
    days.fillna(0, inplace=True)

    d3 = pd.DataFrame([])
    d3['date'] = pd.to_datetime(config.load_market_holidays('HK_Stock'))
    d3 = d3[d3.date > data.date.max()]
    d3['open'] = 0

    d2 = pd.DataFrame([])
    d2['date'] = pd.date_range(
        data.date.max() + dt.timedelta(days=1),
        d3.date.max()
    )

    d3 = pd.merge(d2, d3, how='outer', on=['date'])
    d3.fillna(1, inplace=True)
    for i, r in d3.iterrows():
        if r.date.weekday() in (5, 6):
            d3.at[i, ['open']] = 0

    days = pd.concat([days, d3])
    days['exchange'] = 'HKEX'
    days['open'] = days.open.astype('int')

    # from Calf.data import ModelData as md
    #
    # md().insert_data('MarketCalendar', days)
    pass


# f2()

def f3():
    import pandas as pd
    from Calf.data import WebData as wd

    # data = wd.Stooq_index_data('SHC')
    data = wd.yahoo_stock_data('000001.SS', dt.datetime(1980, 1, 1), dt.datetime(2019, 4, 8))
    # print(data.head())
    # print(data.tail())
    data = data[data.date >= dt.datetime(1900, 1, 1)]

    tdr = data.loc[:, ['date']]
    tdr['open'] = 1

    ald = pd.DataFrame()
    ald['date'] = pd.date_range(data.date.min(), data.date.max())

    days = pd.merge(ald, tdr, on=['date'], how='outer')
    days.fillna(0, inplace=True)

    d3 = pd.DataFrame([])
    d3['date'] = pd.to_datetime(config.load_market_holidays('China_Stock_A'))
    d3 = d3[d3.date > data.date.max()]
    d3['open'] = 0

    d2 = pd.DataFrame([])
    d2['date'] = pd.date_range(
        data.date.max() + dt.timedelta(days=1),
        d3.date.max()
    )

    d3 = pd.merge(d2, d3, how='outer', on=['date'])
    d3.fillna(1, inplace=True)
    for i, r in d3.iterrows():
        if r.date.weekday() in (5, 6):
            d3.at[i, ['open']] = 0

    days = pd.concat([days, d3])
    days['exchange'] = 'SSE'
    days['open'] = days.open.astype('int')

    from Calf.data import ModelData as md

    md().insert_data('MarketCalendar', days)
    md(location='server').insert_data('MarketCalendar', days)
    pass


# f3()