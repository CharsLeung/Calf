# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2018/11/7 14:30
"""
# 1901~2100年农历数据表
# 数据来源: http://data.weather.gov.hk/gts/time/conversion1_text_c.htm
# 节气计算公式[Y*D+C]-L 及误差调节参考的下文
# ====================================================================

from datetime import date, datetime
import calendar

START_YEAR = 1901

month_DAY_BIT = 12
month_NUM_BIT = 13


def _cnDay(_day):
    """ 阴历-日
        Arg:
            type(_day) int 1 数字形式的阴历-日
        Return:
            String "初一"
    """
    _cn_day = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
               "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "廿十",
               "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
    return _cn_day[(_day - 1) % 30]


def _cnMonth(_month):
    """ 阴历-月
        Arg:
            type(_day) int 13 数字形式的阴历-月
        Return:
            String "闰正月"
    """
    _cn_month = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"]
    leap = (_month >> 4) & 0xf
    m = _month & 0xf
    _month = _cn_month[(m - 1) % 12]
    if leap == m:
        _month = "闰" + _month
    return _month


def _cnYear(_year):
    """ 阴历-年
        Arg:
            type(_year) int 2018 数字形式的年份
        Return:
            String "戊戍[狗]" 汉字形式的年份
    """
    _tian_gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    _di_zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    _sheng_xiao = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    return _tian_gan[(_year - 4) % 10] + _di_zhi[(_year - 4) % 12] + '[' + _sheng_xiao[(_year - 4) % 12] + ']'


def _upperYear(_date):
    """ 年份大写 如：二零一八 """
    _upper_num = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    _upper_year = ""
    for i in str(_date.year):
        _upper_year += _upper_num[int(i)]
    return _upper_year


def _upperWeek(_date):
    """ 星期大写 如：星期一 """
    _week_day = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return _week_day[_date.weekday()]


def _cnMonthDays(_cn_year, _cn_month):
    """ 计算阴历月天数
        Arg:
            type(_cn_year) int 2018 数字年份
            type(_cn_month) int 6 数字阴历月份
        Return:
            int 30或29,该年闰月，闰月天数
    """
    # 农历数据 每个元素的存储格式如下：
    #   16~13    12          11~0
    #  闰几月 闰月日数  1~12月份农历日数
    _cn_month_list = [
        0x00752, 0x00ea5, 0x0ab2a, 0x0064b, 0x00a9b, 0x09aa6, 0x0056a, 0x00b59, 0x04baa, 0x00752,  # 1901 ~ 1910
        0x0cda5, 0x00b25, 0x00a4b, 0x0ba4b, 0x002ad, 0x0056b, 0x045b5, 0x00da9, 0x0fe92, 0x00e92,  # 1911 ~ 1920
        0x00d25, 0x0ad2d, 0x00a56, 0x002b6, 0x09ad5, 0x006d4, 0x00ea9, 0x04f4a, 0x00e92, 0x0c6a6,  # 1921 ~ 1930
        0x0052b, 0x00a57, 0x0b956, 0x00b5a, 0x006d4, 0x07761, 0x00749, 0x0fb13, 0x00a93, 0x0052b,  # 1931 ~ 1940
        0x0d51b, 0x00aad, 0x0056a, 0x09da5, 0x00ba4, 0x00b49, 0x04d4b, 0x00a95, 0x0eaad, 0x00536,  # 1941 ~ 1950
        0x00aad, 0x0baca, 0x005b2, 0x00da5, 0x07ea2, 0x00d4a, 0x10595, 0x00a97, 0x00556, 0x0c575,  # 1951 ~ 1960
        0x00ad5, 0x006d2, 0x08755, 0x00ea5, 0x0064a, 0x0664f, 0x00a9b, 0x0eada, 0x0056a, 0x00b69,  # 1961 ~ 1970
        0x0abb2, 0x00b52, 0x00b25, 0x08b2b, 0x00a4b, 0x10aab, 0x002ad, 0x0056d, 0x0d5a9, 0x00da9,  # 1971 ~ 1980
        0x00d92, 0x08e95, 0x00d25, 0x14e4d, 0x00a56, 0x002b6, 0x0c2f5, 0x006d5, 0x00ea9, 0x0af52,  # 1981 ~ 1990
        0x00e92, 0x00d26, 0x0652e, 0x00a57, 0x10ad6, 0x0035a, 0x006d5, 0x0ab69, 0x00749, 0x00693,  # 1991 ~ 2000
        0x08a9b, 0x0052b, 0x00a5b, 0x04aae, 0x0056a, 0x0edd5, 0x00ba4, 0x00b49, 0x0ad53, 0x00a95,  # 2001 ~ 2010
        0x0052d, 0x0855d, 0x00ab5, 0x12baa, 0x005d2, 0x00da5, 0x0de8a, 0x00d4a, 0x00c95, 0x08a9e,  # 2011 ~ 2020
        0x00556, 0x00ab5, 0x04ada, 0x006d2, 0x0c765, 0x00725, 0x0064b, 0x0a657, 0x00cab, 0x0055a,  # 2021 ~ 2030
        0x0656e, 0x00b69, 0x16f52, 0x00b52, 0x00b25, 0x0dd0b, 0x00a4b, 0x004ab, 0x0a2bb, 0x005ad,  # 2031 ~ 2040
        0x00b6a, 0x04daa, 0x00d92, 0x0eea5, 0x00d25, 0x00a55, 0x0ba4d, 0x004b6, 0x005b5, 0x076d2,  # 2041 ~ 2050
        0x00ec9, 0x10f92, 0x00e92, 0x00d26, 0x0d516, 0x00a57, 0x00556, 0x09365, 0x00755, 0x00749,  # 2051 ~ 2060
        0x0674b, 0x00693, 0x0eaab, 0x0052b, 0x00a5b, 0x0aaba, 0x0056a, 0x00b65, 0x08baa, 0x00b4a,  # 2061 ~ 2070
        0x10d95, 0x00a95, 0x0052d, 0x0c56d, 0x00ab5, 0x005aa, 0x085d5, 0x00da5, 0x00d4a, 0x06e4d,  # 2071 ~ 2080
        0x00c96, 0x0ecce, 0x00556, 0x00ab5, 0x0bad2, 0x006d2, 0x00ea5, 0x0872a, 0x0068b, 0x10697,  # 2081 ~ 2090
        0x004ab, 0x0055b, 0x0d556, 0x00b6a, 0x00752, 0x08b95, 0x00b45, 0x00a8b, 0x04a4f, ]
    if _cn_year < START_YEAR:
        return 30

    leap_month, leap_day, month_day = 0, 0, 0  # 闰几月，该月多少天 传入月份多少天

    tmp = _cn_month_list[_cn_year - START_YEAR]

    if tmp & (1 << (_cn_month - 1)):
        month_day = 30
    else:
        month_day = 29

    # 闰月
    leap_month = (tmp >> month_NUM_BIT) & 0xf
    if leap_month:
        if tmp & (1 << month_DAY_BIT):
            leap_day = 30
        else:
            leap_day = 29

    return [month_day, leap_month, leap_day]


def _getNumCnDate(_date):
    """ 获取数字形式的农历日期
        Args:
            _date = datetime(year, month, day)
        Return:
            _year, _month, _day
            返回的月份，高4bit为闰月月份，低4bit为其它正常月份
    """
    # 农历数据 每个元素的存储格式如下：
    # 7~6    5~1
    # 春节月  春节日
    _cn_year_list = [
        0x53, 0x48, 0x3d, 0x50, 0x44, 0x39, 0x4d, 0x42, 0x36, 0x4a,  # 1901 ~ 1910
        0x3e, 0x52, 0x46, 0x3a, 0x4e, 0x43, 0x37, 0x4b, 0x41, 0x54,  # 1911 ~ 1920
        0x48, 0x3c, 0x50, 0x45, 0x38, 0x4d, 0x42, 0x37, 0x4a, 0x3e,  # 1921 ~ 1930
        0x51, 0x46, 0x3a, 0x4e, 0x44, 0x38, 0x4b, 0x3f, 0x53, 0x48,  # 1931 ~ 1940
        0x3b, 0x4f, 0x45, 0x39, 0x4d, 0x42, 0x36, 0x4a, 0x3d, 0x51,  # 1941 ~ 1950
        0x46, 0x3b, 0x4e, 0x43, 0x38, 0x4c, 0x3f, 0x52, 0x48, 0x3c,  # 1951 ~ 1960
        0x4f, 0x45, 0x39, 0x4d, 0x42, 0x35, 0x49, 0x3e, 0x51, 0x46,  # 1961 ~ 1970
        0x3b, 0x4f, 0x43, 0x37, 0x4b, 0x3f, 0x52, 0x47, 0x3c, 0x50,  # 1971 ~ 1980
        0x45, 0x39, 0x4d, 0x42, 0x54, 0x49, 0x3d, 0x51, 0x46, 0x3b,  # 1981 ~ 1990
        0x4f, 0x44, 0x37, 0x4a, 0x3f, 0x53, 0x47, 0x3c, 0x50, 0x45,  # 1991 ~ 2000
        0x38, 0x4c, 0x41, 0x36, 0x49, 0x3d, 0x52, 0x47, 0x3a, 0x4e,  # 2001 ~ 2010
        0x43, 0x37, 0x4a, 0x3f, 0x53, 0x48, 0x3c, 0x50, 0x45, 0x39,  # 2011 ~ 2020
        0x4c, 0x41, 0x36, 0x4a, 0x3d, 0x51, 0x46, 0x3a, 0x4d, 0x43,  # 2021 ~ 2030
        0x37, 0x4b, 0x3f, 0x53, 0x48, 0x3c, 0x4f, 0x44, 0x38, 0x4c,  # 2031 ~ 2040
        0x41, 0x36, 0x4a, 0x3e, 0x51, 0x46, 0x3a, 0x4e, 0x42, 0x37,  # 2041 ~ 2050
        0x4b, 0x41, 0x53, 0x48, 0x3c, 0x4f, 0x44, 0x38, 0x4c, 0x42,  # 2051 ~ 2060
        0x35, 0x49, 0x3d, 0x51, 0x45, 0x3a, 0x4e, 0x43, 0x37, 0x4b,  # 2061 ~ 2070
        0x3f, 0x53, 0x47, 0x3b, 0x4f, 0x45, 0x38, 0x4c, 0x42, 0x36,  # 2071 ~ 2080
        0x49, 0x3d, 0x51, 0x46, 0x3a, 0x4e, 0x43, 0x38, 0x4a, 0x3e,  # 2081 ~ 2090
        0x52, 0x47, 0x3b, 0x4f, 0x45, 0x39, 0x4c, 0x41, 0x35, 0x49,  # 2091 ~ 2100
    ]
    _year, _month, _day = _date.year, 1, 1
    _code_year = _cn_year_list[_year - START_YEAR]
    """ 获取当前日期与当年春节的差日 """
    _span_days = (_date - datetime(_year, ((_code_year >> 5) & 0x3), ((_code_year >> 0) & 0x1f))).days
    # print("span_day: ", _span_days)

    if _span_days >= 0:
        """ 新年后推算日期，差日依序减月份天数，直到不足一个月，剪的次数为月数，剩余部分为日数 """
        """ 先获取闰月 """
        _month_days, _leap_month, _leap_day = _cnMonthDays(_year, _month)
        while _span_days >= _month_days:
            """ 获取当前月份天数，从差日中扣除 """
            _span_days -= _month_days
            if _month == _leap_month:
                """ 如果当月还是闰月 """
                _month_days = _leap_day
                if _span_days < _month_days:
                    """ 指定日期在闰月中 ???"""
                    _month = (_leap_month << 4) | _month
                    break
                """ 否则扣除闰月天数，月份加一 """
                _span_days -= _month_days
            _month += 1
            _month_days = _cnMonthDays(_year, _month)[0]
        _day += _span_days
        return _year, _month, _day
    else:
        """ 新年前倒推去年日期 """
        _month = 12
        _year -= 1
        _month_days, _leap_month, _leap_day = _cnMonthDays(_year, _month)
        while abs(_span_days) > _month_days:
            _span_days += _month_days
            _month -= 1
            if _month == _leap_month:
                _month_days = _leap_day
                if abs(_span_days) <= _month_days:  # 指定日期在闰月中
                    _month = (_leap_month << 4) | _month
                    break
                _span_days += _month_days
            _month_days = _cnMonthDays(_year, _month)[0]
        _day += (_month_days + _span_days)  # 从月份总数中倒扣 得到天数
        return _year, _month, _day


def getCnDate(_date):
    """ 获取完整的农历日期
        Args:
            _date = datetime(year, month, day)
        Return:
            "农历 xx[x]年 xxxx年x月xx 星期x"
    """
    (_year, _month, _day) = _getNumCnDate(_date)
    return "农历 %s年 %s年%s%s %s " % (_cnYear(_year), _upperYear(_date),
                                   _cnMonth(_month), _cnDay(_day), _upperWeek(_date))


def getCnYear(_date):
    """ 获取农历年份
        Args:
            _date = datetime(year, month, day)
        Return:
            "x月"
    """
    _year = _getNumCnDate(_date)[0]
    return "%s年" % _cnYear(_year)


def getCnMonth(_date):
    """ 获取农历月份
        Args:
            _date = datetime(year, month, day)
        Return:
            "xx"
    """
    _month = _getNumCnDate(_date)[1]
    return "%s" % _cnMonth(_month)


def getCnDay(_date):
    """ 获取农历日
        Args:
            _date = datetime(year, month, day)
        Return:
            "农历 xx[x]年 xxxx年x月xx 星期x"
    """
    _day = _getNumCnDate(_date)[2]
    return "%s" % _cnDay(_day)


def getSolarTerms(_date):
    """ 查询节气 待改查表法
        输入日期
        输出节气 "\0" "立春"
    """
    # 当前流程：
    # 判断世纪
    # 获取年份后两位
    # 根据月份选择公式
    # 矫正
    # 对应日期
    # 查表法流程:
    # 检索当年节气表
    # 检索当月节气日
    # 判断是否相等
    # _jie_qi = [
    #     [''],
    #     ["小寒", "大寒"],  # 1月
    #     ["立春", "雨水"],  # 2月
    #     ["惊蛰", "春分"],  # 3月
    #     ["清明", "谷雨"],  # 4月
    #     ["立夏", "小满"],  # 5月
    #     ["芒种", "夏至"],  # 6月
    #     ["小暑", "大暑"],  # 7月
    #     ["立秋", "处暑"],  # 8月
    #     ["白露", "秋分"],  # 9月
    #     ["寒露", "霜降"],  # 10月
    #     ["立冬", "小雪"],  # 11月
    #     ["大雪", "冬至"]]  # 12月
    # _century = 0
    # if _date.year >= 2000:
    #     _century = 1
    # _year = _date.year % 100
    # _month = _date.month
    # _D = 0.2422
    # _M = 1
    # if _date.month == 1:
    #     # 小寒
    #     _C = [6.11, 5.4055][_century]
    #     _solar_day = (_year * _D + _C) - ((_year - 1) / 4)
    #     if _date.year == 1982:  # 矫正
    #         _solar_day += 1
    #     if _date.year == 2019:  # 矫正
    #         _solar_day -= 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     _C = [20.84, 20.12][_century]
    #     _solar_day = (_year * _D + _C) - ((_year - 1) / 4)
    #     if _date.year == 2082:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 2:
    #     # 立春
    #     _C = [4.15, 3.87][_century]
    #     _solar_day = (_year * _D + _C) - ((_year - 1) / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 雨水
    #     _C = [18.73, 18.73][_century]
    #     _solar_day = (_year * _D + _C) - ((_year - 1) / 4)
    #     if _date.year == 2026:  # 矫正
    #         _solar_day -= 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 3:
    #     # 惊蛰
    #     _C = [5.63, 5.63][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 春分
    #     _C = [20.646, 20.646][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 2084:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 4:
    #     # 清明
    #     _C = [5.59, 4.81][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 谷雨
    #     _C = [20.888, 20.1][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 5:
    #     # 立夏
    #     _C = [6.318, 5.52][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1911:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 小满
    #     _C = [21.86, 21.04][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 2008:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 6:
    #     # 芒种
    #     _C = [6.5, 5.678][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1902:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 夏至
    #     _C = [22.20, 21.37][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1928:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 7:
    #     # 小暑
    #     _C = [7.928, 7.108][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1925 | _date.year == 2016:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 大暑
    #     _C = [23.65, 22.83][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1922:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 8:
    #     # 立秋
    #     _C = [8.35, 7.5][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 2002:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 处暑
    #     _C = [23.95, 23.13][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 9:
    #     # 白露
    #     _C = [8.44, 7.646][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1927:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 秋分
    #     _C = [23.822, 23.042][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1942:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 10:
    #     # 寒露
    #     _C = [9.098, 8.318][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 霜降
    #     _C = [24.218, 23.438][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 2089:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 11:
    #     # 立冬
    #     _C = [8.218, 7.438][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 2089:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 小雪
    #     _C = [23.08, 22.36][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1978:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # _M += 1
    # if _date.month == 12:
    #     # 大雪
    #     _C = [7.9, 7.18][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1954:  # 矫正
    #         _solar_day += 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][0]
    #     # 冬至
    #     _C = [22.60, 21.94][_century]
    #     _solar_day = (_year * _D + _C) - (_year / 4)
    #     if _date.year == 1918 | _date.year == 2021:  # 矫正
    #         _solar_day -= 1
    #     if _date.day == _solar_day // 1:
    #         return _jie_qi[_M][1]
    # return _jie_qi[0][0]
    ct = _date  # 取当前时间
    year = ct.year

    # 返回指定公历日期的儒略日
    def julian_day():
        # ct = self.localtime  # 取当前时间
        y = ct.year
        month = ct.month
        day = ct.day
        if month <= 2:
            month += 12
            y -= 1
        b = y / 100
        b = 2 - b + y / 400
        dd = day + 0.5000115740  # 本日12:00后才是儒略日的开始(过一秒钟)*/
        return int(365.25 * (y + 4716) + 0.01) + int(30.60001 * (month + 1)) + dd + b - 1524.5

    # 返回指定年份的节气的儒略日数
    def julian_day_of_ln_jie(y, st):
        s_stAccInfo = [
            0.00, 1272494.40, 2548020.60, 3830143.80, 5120226.60, 6420865.80,
            7732018.80, 9055272.60, 10388958.00, 11733065.40, 13084292.40, 14441592.00,
            15800560.80, 17159347.20, 18513766.20, 19862002.20, 21201005.40, 22529659.80,
            23846845.20, 25152606.00, 26447687.40, 27733451.40, 29011921.20, 30285477.60]
        # 已知1900年小寒时刻为1月6日02:05:00
        base1900_SlightColdJD = 2415025.5868055555
        if (st < 0) or (st > 24):
            return 0.0
        stJd = 365.24219878 * (y - 1900) + s_stAccInfo[st] / 86400.0
        return base1900_SlightColdJD + stJd

    for i in range(24):
        # 因为两个都是浮点数，不能用相等表示
        delta = julian_day() - julian_day_of_ln_jie(year, i)
        if -.5 <= delta <= .5:
            # 节气
            jie = '小寒大寒立春雨水惊蛰春分清明谷雨立夏小满芒种夏至' \
                  '小暑大暑立秋处暑白露秋分寒露霜降立冬小雪大雪冬至'
            return jie[i * 2:(i + 1) * 2]
    return ''


# 作者：Yovey
# 链接：https: // www.jianshu.com / p / 8
# dc0d7ba2c2a
# 來源：简书
# 简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
def _showMonth(_date):
    """ 测试：
        输出农历日历
    """
    print(getCnDate(_date))  # 根据数组索引确定农历日期
    print(getCnYear(_date))  # 返回干支年
    print(getCnMonth(_date))  # 返回农历月
    print(getCnDay(_date))  # 返回农历日
    print(getSolarTerms(_date))  # 返回节气
    print(_upperYear(_date))  # 返回大写年份
    print(_upperWeek(_date))  # 返回大写星期


# pre = datetime.now()
# _showMonth(datetime.now())  # 测试所有入口
# late = datetime.now()
# pop = late - pre
# print(pop * 10000)  # 看一下性能
# print(type(pre))  # 展示一下日期类型
import datetime


class Lunar(object):
    # ******************************************************************************
    # 下面为阴历计算所需的数据,为节省存储空间,所以采用下面比较变态的存储方法.
    # ******************************************************************************
    # 数组g_lunar_month_day存入阴历1901年到2050年每年中的月天数信息，
    # 阴历每月只能是29或30天，一年用12（或13）个二进制位表示，对应位为1表30天，否则为29天
    g_lunar_month_day = [
        0x4ae0, 0xa570, 0x5268, 0xd260, 0xd950, 0x6aa8, 0x56a0, 0x9ad0, 0x4ae8, 0x4ae0,  # 1910
        0xa4d8, 0xa4d0, 0xd250, 0xd548, 0xb550, 0x56a0, 0x96d0, 0x95b0, 0x49b8, 0x49b0,  # 1920
        0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada8, 0x2b60, 0x9570, 0x4978, 0x4970, 0x64b0,  # 1930
        0xd4a0, 0xea50, 0x6d48, 0x5ad0, 0x2b60, 0x9370, 0x92e0, 0xc968, 0xc950, 0xd4a0,  # 1940
        0xda50, 0xb550, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950, 0xb4a8, 0x6ca0,  # 1950
        0xb550, 0x55a8, 0x4da0, 0xa5b0, 0x52b8, 0x52b0, 0xa950, 0xe950, 0x6aa0, 0xad50,  # 1960
        0xab50, 0x4b60, 0xa570, 0xa570, 0x5260, 0xe930, 0xd950, 0x5aa8, 0x56a0, 0x96d0,  # 1970
        0x4ae8, 0x4ad0, 0xa4d0, 0xd268, 0xd250, 0xd528, 0xb540, 0xb6a0, 0x96d0, 0x95b0,  # 1980
        0x49b0, 0xa4b8, 0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada0, 0xab60, 0x9370, 0x4978,  # 1990
        0x4970, 0x64b0, 0x6a50, 0xea50, 0x6b28, 0x5ac0, 0xab60, 0x9368, 0x92e0, 0xc960,  # 2000
        0xd4a8, 0xd4a0, 0xda50, 0x5aa8, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950,  # 2010
        0xb4a0, 0xb550, 0xb550, 0x55a8, 0x4ba0, 0xa5b0, 0x52b8, 0x52b0, 0xa930, 0x74a8,  # 2020
        0x6aa0, 0xad50, 0x4da8, 0x4b60, 0x9570, 0xa4e0, 0xd260, 0xe930, 0xd530, 0x5aa0,  # 2030
        0x6b50, 0x96d0, 0x4ae8, 0x4ad0, 0xa4d0, 0xd258, 0xd250, 0xd520, 0xdaa0, 0xb5a0,  # 2040
        0x56d0, 0x4ad8, 0x49b0, 0xa4b8, 0xa4b0, 0xaa50, 0xb528, 0x6d20, 0xada0, 0x55b0,  # 2050
    ]
    # 数组gLanarMonth存放阴历1901年到2050年闰月的月份，如没有则为0，每字节存两年
    g_lunar_month = [
        0x00, 0x50, 0x04, 0x00, 0x20,  # 1910
        0x60, 0x05, 0x00, 0x20, 0x70,  # 1920
        0x05, 0x00, 0x40, 0x02, 0x06,  # 1930
        0x00, 0x50, 0x03, 0x07, 0x00,  # 1940
        0x60, 0x04, 0x00, 0x20, 0x70,  # 1950
        0x05, 0x00, 0x30, 0x80, 0x06,  # 1960
        0x00, 0x40, 0x03, 0x07, 0x00,  # 1970
        0x50, 0x04, 0x08, 0x00, 0x60,  # 1980
        0x04, 0x0a, 0x00, 0x60, 0x05,  # 1990
        0x00, 0x30, 0x80, 0x05, 0x00,  # 2000
        0x40, 0x02, 0x07, 0x00, 0x50,  # 2010
        0x04, 0x09, 0x00, 0x60, 0x04,  # 2020
        0x00, 0x20, 0x60, 0x05, 0x00,  # 2030
        0x30, 0xb0, 0x06, 0x00, 0x50,  # 2040
        0x02, 0x07, 0x00, 0x50, 0x03  # 2050
    ]
    START_YEAR = 1901
    # 天干
    gan = '甲乙丙丁戊己庚辛壬癸'
    # 地支
    zhi = '子丑寅卯辰巳午未申酉戌亥'
    # 生肖
    xiao = '鼠牛虎兔龙蛇马羊猴鸡狗猪'
    # 月份
    lm = '正二三四五六七八九十冬腊'
    # 日份
    ld = '初一初二初三初四初五初六初七初八初九初十' \
         '十一十二十三十四十五十六十七十八十九二十' \
         '廿一廿二廿三廿四廿五廿六廿七廿八廿九三十'
    # 节气
    jie = '小寒大寒立春雨水惊蛰春分清明谷雨立夏小满芒种夏至' \
          '小暑大暑立秋处暑白露秋分寒露霜降立冬小雪大雪冬至'

    def __init__(self, dt=None):
        '''初始化：参数为datetime.datetime类实例，默认当前时间'''
        self.localtime = dt if dt else datetime.datetime.today()

    def sx_year(self):  # 返回生肖年
        ct = self.localtime  # 取当前时间
        year = self.ln_year() - 3 - 1  # 农历年份减3 （说明：补减1）
        year = year % 12  # 模12，得到地支数
        return self.xiao[year]

    def gz_year(self):  # 返回干支纪年
        ct = self.localtime  # 取当前时间
        year = self.ln_year() - 3 - 1  # 农历年份减3 （说明：补减1）
        G = year % 10  # 模10，得到天干数
        Z = year % 12  # 模12，得到地支数
        return self.gan[G] + self.zhi[Z]

    def gz_month(self):  # 返回干支纪月（未实现）
        pass

    def gz_day(self):  # 返回干支纪日
        ct = self.localtime  # 取当前时间
        C = ct.year // 100  # 取世纪数，减一
        y = ct.year % 100  # 取年份后两位（若为1月、2月则当前年份减一）
        y = y - 1 if ct.month == 1 or ct.month == 2 else y
        M = ct.month  # 取月份（若为1月、2月则分别按13、14来计算）
        M = M + 12 if ct.month == 1 or ct.month == 2 else M
        d = ct.day  # 取日数
        i = 0 if ct.month % 2 == 1 else 6  # 取i （奇数月i=0，偶数月i=6）
        # 下面两个是网上的公式
        # http://baike.baidu.com/link?url=MbTKmhrTHTOAz735gi37tEtwd29zqE9GJ92cZQZd0X8uFO5XgmyMKQru6aetzcGadqekzKd3nZHVS99rewya6q
        # 计算干（说明：补减1）
        G = 4 * C + C // 4 + 5 * y + y // 4 + 3 * (M + 1) // 5 + d - 3 - 1
        G = G % 10
        # 计算支（说明：补减1）
        Z = 8 * C + C // 4 + 5 * y + y // 4 + 3 * (M + 1) // 5 + d + 7 + i - 1
        Z = Z % 12
        # 返回 干支纪日
        return self.gan[G] + self.zhi[Z]

    def gz_hour(self):  # 返回干支纪时（时辰）
        ct = self.localtime  # 取当前时间
        # 计算支
        Z = round((ct.hour / 2) + 0.1) % 12  # 之所以加0.1是因为round的bug!!
        # 返回 干支纪时（时辰）
        return self.zhi[Z]

    def ln_year(self):  # 返回农历年
        year, _, _ = self.ln_date()
        return year

    def ln_month(self):  # 返回农历月
        _, month, _ = self.ln_date()
        return month

    def ln_day(self):  # 返回农历日
        _, _, day = self.ln_date()
        return day

    def ln_date(self):  # 返回农历日期整数元组（年、月、日）（查表法）
        delta_days = self._date_diff()
        # 阳历1901年2月19日为阴历1901年正月初一
        # 阳历1901年1月1日到2月19日共有49天
        if (delta_days < 49):
            year = self.START_YEAR - 1
            if (delta_days < 19):
                month = 11;
                day = 11 + delta_days
            else:
                month = 12;
                day = delta_days - 18
            return (year, month, day)
        # 下面从阴历1901年正月初一算起
        delta_days -= 49
        year, month, day = self.START_YEAR, 1, 1
        # 计算年
        tmp = self._lunar_year_days(year)
        while delta_days >= tmp:
            delta_days -= tmp
            year += 1
            tmp = self._lunar_year_days(year)
        # 计算月
        (foo, tmp) = self._lunar_month_days(year, month)
        while delta_days >= tmp:
            delta_days -= tmp
            if (month == self._get_leap_month(year)):
                (tmp, foo) = self._lunar_month_days(year, month)
                if (delta_days < tmp):
                    return (0, 0, 0)
                    return (year, month, delta_days + 1)
                delta_days -= tmp
            month += 1
            (foo, tmp) = self._lunar_month_days(year, month)
        # 计算日
        day += delta_days
        return (year, month, day)

    def ln_date_str(self):  # 返回农历日期字符串，形如：农历正月初九
        _, month, day = self.ln_date()
        return '农历{}月{}'.format(self.lm[month - 1], self.ld[(day - 1) * 2:day * 2])

    def ln_jie(self):  # 返回农历节气
        ct = self.localtime  # 取当前时间
        year = ct.year
        for i in range(24):
            # 因为两个都是浮点数，不能用相等表示
            delta = self._julian_day() - self._julian_day_of_ln_jie(year, i)
            if -.5 <= delta <= .5:
                return self.jie[i * 2:(i + 1) * 2]
        return ''

    # 显示日历
    def calendar(self):
        pass

    #######################################################
    #      下面皆为私有函数
    #######################################################
    def _date_diff(self):
        '''返回基于1901/01/01日差数'''
        return (self.localtime - datetime.datetime(1901, 1, 1)).days

    def _get_leap_month(self, lunar_year):
        flag = self.g_lunar_month[(lunar_year - self.START_YEAR) // 2]
        if (lunar_year - self.START_YEAR) % 2:
            return flag & 0x0f
        else:
            return flag >> 4

    def _lunar_month_days(self, lunar_year, lunar_month):
        if (lunar_year < self.START_YEAR):
            return 30
        high, low = 0, 29
        iBit = 16 - lunar_month;
        if (lunar_month > self._get_leap_month(lunar_year) and self._get_leap_month(lunar_year)):
            iBit -= 1
        if (self.g_lunar_month_day[lunar_year - self.START_YEAR] & (1 << iBit)):
            low += 1
        if (lunar_month == self._get_leap_month(lunar_year)):
            if (self.g_lunar_month_day[lunar_year - self.START_YEAR] & (1 << (iBit - 1))):
                high = 30
            else:
                high = 29
        return (high, low)

    def _lunar_year_days(self, year):
        days = 0
        for i in range(1, 13):
            (high, low) = self._lunar_month_days(year, i)
            days += high
            days += low
        return days

    # 返回指定公历日期的儒略日
    def _julian_day(self):
        ct = self.localtime  # 取当前时间
        year = ct.year
        month = ct.month
        day = ct.day
        if month <= 2:
            month += 12
            year -= 1
        B = year / 100
        B = 2 - B + year / 400
        dd = day + 0.5000115740  # 本日12:00后才是儒略日的开始(过一秒钟)*/
        return int(365.25 * (year + 4716) + 0.01) + int(30.60001 * (month + 1)) + dd + B - 1524.5

    # 返回指定年份的节气的儒略日数
    def _julian_day_of_ln_jie(self, year, st):
        s_stAccInfo = [
            0.00, 1272494.40, 2548020.60, 3830143.80, 5120226.60, 6420865.80,
            7732018.80, 9055272.60, 10388958.00, 11733065.40, 13084292.40, 14441592.00,
            15800560.80, 17159347.20, 18513766.20, 19862002.20, 21201005.40, 22529659.80,
            23846845.20, 25152606.00, 26447687.40, 27733451.40, 29011921.20, 30285477.60]
        # 已知1900年小寒时刻为1月6日02:05:00
        base1900_SlightColdJD = 2415025.5868055555
        if (st < 0) or (st > 24):
            return 0.0
        stJd = 365.24219878 * (year - 1900) + s_stAccInfo[st] / 86400.0
        return base1900_SlightColdJD + stJd


# 测试
def test(ct=None):
    ln = Lunar(ct)
    print('公历 {} 北京时间 {}'.format(ln.localtime.date(), ln.localtime.time()))
    print('{} 【{}】 {}年 {}日 {}时'.format(ln.ln_date_str(), ln.gz_year(), ln.sx_year(), ln.gz_day(), ln.gz_hour()))
    print('节气：{}'.format(ln.ln_jie()))


pass
# ct = datetime.datetime(2018, 11, 6)
# test(ct)
# import pandas as pd
# import datetime as dt
#
# dates = pd.DataFrame()
# dates['date'] = pd.date_range(dt.datetime(1990, 1, 1), dt.datetime(2018, 10, 31))
# dates['solar1'] = dates.date.map(lambda d: getSolarTerms(d))
# dates['solar2'] = dates.date.map(lambda d: Lunar(d).ln_jie())
# dates = dates[(dates.solar1 != '') | (dates.solar2 != '')]
# a = 1
# pass
