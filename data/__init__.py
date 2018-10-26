# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/20 15:17
@describe: Calf模型最基础的研究对象是金融证券的K线数据，大部分工作就是围绕
K线数据来操作的
"""

# 关于Calf的数据IO将通过此包下的一系列工具完成，Calf能够顺利的访问数据库
# 资源，需要在引用Calf的顶级包（或文件夹）下创建一个名为db_config.json
# 的数据库服务器访问路径配置文件， 它是一个形如:
# {’default‘: {'ip':'0.0.0.0', 'port': 10000, 'dbname': 'ppp', ....},
# 'db2':{....},
# 'db3':{....},
# }，这样的json文件，其中’default‘是必须的，它是默认的访问位置
# 此外Calf还需要一个用于记录Kline更新的json文件，它记载了数据库中每个周期
# 下最新的K线的_id值，它主要是用在实时任务中判断K线数据是否发生了更新。
# 它是一个形如：
# {"kline_min30": "5aa22f25ae17be3521266751", "kline_min60": "5aa22f2aae17be42b55ef283",
# "XDXR_day": "5a93af2fae17bef65467952a", "datetime": "2018-03-09 14:52:48"}的json文件

from Calf.models.base_model import BaseModel
from Calf.exception import MongoIOError
from Calf.models import DayXDXR, Day, Minute, SellList, signal, MonthIndex, WeekIndex, DayIndex, \
    MintueIndex
from Calf.models.asset import Asset
from Calf.models.baseinfo import rrads
from Calf.models.order import Orders, OrdersHis, RmdsHis
from Calf.models.self_models import TradeMenu, ModelFinanceIndex, Naughtiers
from Calf.models.zjf_model import Risk_and_Position, kline_data_update_mark, Risk, Position, \
    Inflexion, Buy_Point


def KLINE_MODEL_TABLE(location=None, dbname=None, tablename=None):
    """
    K线数据源的映射
    :param location:
    :param dbname:
    :param tablename:
    :return:
    """
    if tablename == 'XDXR_day':
        return DayXDXR('XDXR_day', location, dbname)
    elif tablename == 'kline_day':
        return Day('kline_day', location, dbname)
    elif tablename == 'kline_min5':
        return Minute('kline_min5', location, dbname)
    elif tablename == 'kline_min15':
        return Minute('kline_min15', location, dbname)
    elif tablename == 'kline_min30':
        return Minute('kline_min30', location, dbname)
    elif tablename == 'kline_min60':
        return Minute('kline_min60', location, dbname)
    elif tablename == 'index_month':
        return MonthIndex('index_month', location, dbname)
    elif tablename == 'index_week':
        return WeekIndex('index_week', location, dbname)
    elif tablename == 'index_day':
        return DayIndex('index_day', location, dbname)
    elif tablename == 'index_min5':
        return MintueIndex('index_min5', location, dbname)
    elif tablename == 'index_min15':
        return MintueIndex('index_min15', location, dbname)
    elif tablename == 'index_min30':
        return MintueIndex('index_min30', location, dbname)
    elif tablename == 'index_min60':
        return MintueIndex('index_min60', location, dbname)
    elif tablename == 'forex_min30':
        return BaseModel('forex_min30', location, dbname)
    elif tablename == 'forex_min60':
        return BaseModel('forex_min60', location, dbname)
    elif tablename == 'forex_day':
        return BaseModel('forex_day', location, dbname)
    elif tablename == 'fx_kline_min30':
        return BaseModel('fx_kline_min30', location, dbname)
    elif tablename == 'fx_kline_min60':
        return BaseModel('fx_kline_min60', location, dbname)
    elif tablename == 'fx_kline_day':
        return BaseModel('fx_kline_day', location, dbname)
    elif tablename == 'bt_coin_day':
        return BaseModel('bt_coin_day', location, dbname)
    elif tablename == 'hk_kline_day':
        return BaseModel('hk_kline_day', location, dbname)
    elif tablename == 'hk_kline_min60':
        return BaseModel('hk_kline_min60', location, dbname)
    elif tablename == 'hk_kline_min30':
        return BaseModel('hk_kline_min30', location, dbname)
    elif tablename == 'usa_kline_day':
        return BaseModel('usa_kline_day', location, dbname)
    elif tablename == 'usa_kline_min60':
        return BaseModel('usa_kline_min60', location, dbname)
    elif tablename == 'usa_kline_min30':
        return BaseModel('usa_kline_min30', location, dbname)
    elif tablename == 'in_kline_day':
        return BaseModel('in_kline_day', location, dbname)
    elif tablename == 'ge_kline_day':
        return BaseModel('ge_kline_day', location, dbname)
    elif tablename == 'en_kline_day':
        return BaseModel('en_kline_day', location, dbname)
    elif tablename == 'qh_index_day':
        return BaseModel('qh_index_day', location, dbname)
    elif tablename == 'global_index_day':
        return BaseModel('global_index_day', location, dbname)
    # TODO(leungjain): IC前缀的表为期货连续，之前有专门的期货数据表，
    # 在未来有可能将两者合并为一个表
    elif tablename == 'IC_day':
        return BaseModel('IC_day', location, dbname)
    elif tablename == 'IC_min5':
        return BaseModel('IC_min5', location, dbname)
    elif tablename == 'data_logs':
        return kline_data_update_mark('kline_data_update_mark',
                                      location, dbname)
    else:
        info = 'not find this "%s" in model list' % tablename
        raise ValueError(info)


def MODEL_TABLE(location=None, dbname=None, tablename=None):
    """
    数据源的映射,主要是指一些公共的数据源
    :param location:
    :param dbname:
    :param tablename:
    :return:
    """
    if tablename == 'signals_his':
        return SellList('signals_his', location, dbname)
    elif tablename == 'signals':
        return signal('signals', location, dbname)
    elif tablename == 'orders':
        return Orders('orders', location, dbname)
    elif tablename == 'orders_simulated':
        return BaseModel('orders_simulated', location, dbname)
    elif tablename == 'orders_his':
        return OrdersHis('orders_his', location, dbname)
    elif tablename == 'trademenu':
        return TradeMenu('trademenu', location, dbname)
    elif tablename == 'financeindex':
        return ModelFinanceIndex('financeindex', location, dbname)
    elif tablename == 'risk_and_position':
        return Risk_and_Position('risk_and_position', location, dbname)
    elif tablename == 'risk':
        return Risk('risk', location, dbname)
    elif tablename == 'position':
        return Position('position', location, dbname)
    elif tablename == 'naughtiers':
        return Naughtiers('naughtiers', location, dbname)
    elif tablename == 'inflexion':
        return Inflexion('inflexion', location, dbname)
    elif tablename == 'buy_point':
        return Buy_Point('buy_point', location, dbname)
    elif tablename == 'asset':
        return Asset('asset', location, dbname)
    elif tablename == 'rmds_his':
        return RmdsHis('rmds_his', location, dbname)
    elif tablename == 'RRADS':
        return rrads('announce', location, dbname)
    elif tablename == 'accounts':
        return BaseModel('accounts', location, dbname)
    elif tablename == 'clients':
        return BaseModel('clients', location, dbname)
    else:
        info = 'not find this "%s" in model list' % tablename
        raise MongoIOError(info)


def SELF_TABLE(location=None, dbname=None, tablename=None):
    """
    用户自定义的一些表
    :param location:
    :param dbname:
    :param tablename:
    :return:
    """
    return BaseModel(tablename, location, dbname)


from .realdata import RealData
from .basedata import BaseData
from .klinedata import KlineData
from .signaldata import SignalData
from .orderdata import OrderData
from .modeldata import ModelData
from .tickdata import TickData
from .webdata import WebData
