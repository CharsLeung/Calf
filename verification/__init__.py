# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/3/20 15:24
"""
from Calf.exception import WarningMessage
from .validator import ModelValidator, VerifyError
try:
    __import__('matplotlib')
    from .validvisual import ValidVisual
except ImportError as e:
    print(WarningMessage(str(e)))
# from .validvisual import ValidVisual

Model_Param = {
    'RISK_FREE': 0.045,  # 无风险收益或固定收益，常常以国债基金、标准利率、银行短期存款确定即货币的时间价值
    'INDEX_MARKET_REFERENCE': '399303',  # 在确认收益时，附加一列大盘的涨跌行情，计算市场无风险收益时选择的大盘指数
}

# 在回测过程中描述股票卖出原因中，用以下字典解释
reason = {
    'stop_get': 1,  # 止盈
    'stop_loss': -1,  # 止损
    'timeout': 0,  # 已达到最长持有天数
    'missing': 404,  # 未找到在休市天数上限以内的股价数据
    'error': 500,  # 其他未知的程序错误
}
