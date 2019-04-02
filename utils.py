# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2017/11/27 14:10
"""
import datetime as dt
import warnings
# import pygame
import threading
import smtplib
import email.mime.multipart
import email.mime.text
from Calf import config
from business_calendar import Calendar, MO, TU, WE, TH, FR
from Calf.exception import ExceptionInfo

warnings.filterwarnings('ignore')


class fontcolor:
    F_RED = '\033[31m'
    F_GREEN = '\033[32m'
    F_YELLOW = '\033[33m'
    F_BLUE = '\033[34m'
    F_PURPLE = '\033[35m'
    F_GREEN_BLUE = '\033[36m'
    B_WHITE_F_BLACK = '\033[7;37;30m'
    END = '\033[0m'


def progress_bar(total, complete, **kwargs):
    isr = int(60 * complete / total)
    sr = ' ' * isr
    print('\rRun:{0}\033[7;37;30m{1}\033[0m{2}/{3}'.format(kwargs, sr, complete, total),
          end='', flush=True)


def play_music(sound, second=10):
    """
    播放一段声音文件
    :param second: 播放的时间
    :param sound:文件名
    :return:
    """
    try:
        # sys.path[1]
        # file = project_dir + '\Calf\Files\\' + sound
        # pygame.mixer.init()
        # # print("播放音乐1")
        # track = pygame.mixer.music.load(file)
        # pygame.mixer.music.play()
        # time.sleep(second)
        # pygame.mixer.music.stop()
        pass
    except Exception as e:
        ExceptionInfo(e)
        pass


def sound_notice(sound_name):
    """
    以多线程的方式播放一段音频文件
    :param sound_name:
    :return:
    """
    try:
        t = threading.Thread(target=play_music, args=(sound_name,))
        return t
    except Exception as e:
        ExceptionInfo(e)


class trading:
    """
    关于交易所的一些基本概况
    """
    # TODO(leungjain): 注意需要手动添加每个市场每年的非周末节假日休市安排
    market = config.default_market_id(info_type='MarketHolidays')
    holidays = config.load_market_holidays(market=market) if market is not None else list()
    workdays = [MO, TU, WE, TH, FR]

    def __init__(self, market=None, source='file', **kwargs):
        """
        关于市场节假日的相关方法
        :param market: 'China_Stock_A':'SSE','USA_Stock':'NYSE','HK_Stock':'HKEX'
        :param source: 节假日或交易日信息存储的位置：file->本地xml文件，db->数据库
        :param kwargs: start_date end_date，获取节假日信息的前沿 后沿，避免加载大量的
        节假日数据
        """
        if market is not None:
            trading.market = market
            trading.holidays = config.load_market_holidays(
                market=market, by=source, **kwargs
            )
        # else:
        #     trading.market = None
        #     trading.holidays = []
        pass

    @classmethod
    def trade_days(cls, start, end):
        """
        给定两个时间，计算这个时间段内有多少个交易日
        :param start:
        :param end:
        :return:
        """
        try:
            start = dt.datetime(start.year, start.month, start.day)
            end = dt.datetime(end.year, end.month, end.day)
            cal = Calendar(workdays=cls.workdays, holidays=cls.holidays)
            days = cal.busdaycount(start, end)
            return days
        except Exception as e:
            ExceptionInfo(e)
            return 0

    @classmethod
    def trade_period(cls, start, days, holidays=None):
        """
        计算某个时间x个交易日后的时间,或之前（days为一个负数）
        :param holidays:
        :param start:
        :param days:
        :return:
        """
        try:
            start = dt.datetime(start.year, start.month, start.day)
            holidays = cls.holidays if holidays is None else holidays
            cal = Calendar(workdays=cls.workdays, holidays=holidays)
            end = cal.addbusdays(start, days)
            return end
        except Exception as e:
            ExceptionInfo(e)
            return start

    @classmethod
    def is_trade_day(cls, date, holidays=None):
        """
        判断给定的这个时间是否是交易日（以日记）
        :param holidays:
        :param date: 需要判断的时间
        :return:
        """
        try:
            holidays = cls.holidays if holidays is None else holidays
            cal = Calendar(workdays=cls.workdays, holidays=holidays)
            flag = cal.isbusday(dt.datetime(date.year, date.month, date.day))
            return flag
        except Exception as e:
            ExceptionInfo(e)
            return False

    @classmethod
    def trade_day_range(cls, start, end, holidays=None):
        """
        给定两个时间，返回这之间的交易日
        :param start:
        :param end:
        :param holidays:
        :return: list or a null list
        """
        try:
            start = dt.datetime(start.year, start.month, start.day)
            end = dt.datetime(end.year, end.month, end.day)
            holidays = cls.holidays if holidays is None else holidays
            cal = Calendar(workdays=cls.workdays, holidays=holidays)
            dls = cal.range(start, end)
            return list(dls)
        except Exception as e:
            ExceptionInfo(e)
            return []

    @classmethod
    def fix_interval(cls, date, category, direction=-1):
        """
        为了取得足够量的数据，不同的K线应具有合理的间隔
        :param date:
        :param category:
        :param direction:
        :return:
        """
        pass

    @classmethod
    def fix_time(cls, kline, date):
        """
        基本kline表的time字段通常与实际不符，我们需要知道距
        某个时点最近的一条K线的time, 这个方法目前只适用于中国股票
        并且强烈建议只在不间歇的实时任务中使用
        :param kline:
        :param date:
        :return:
        """
        try:
            t = date.hour * 100 + date.minute
            if kline == 'kline_min30':
                if 1000 <= t < 1030:
                    return 1000
                elif 1030 <= t < 1100:
                    return 1030
                elif 1100 <= t < 1130:
                    return 1100
                elif 1130 <= t < 1330:
                    return 1300
                elif 1330 <= t < 1400:
                    return 1330
                elif 1400 <= t < 1430:
                    return 1400
                elif 1430 <= t < 1450:
                    return 1430
                else:
                    return 1500
            elif kline == 'kline_min60':
                if 1030 <= t < 1130:
                    return 1030
                elif 1130 <= t < 1400:
                    return 1300
                elif 1400 <= t < 1450:
                    return 1400
                else:
                    return 1500
            else:
                return 0
        except Exception as e:
            ExceptionInfo(e)
            return 0


class Email:
    @classmethod
    def send_email(cls, msgTo, content):
        try:
            msg = email.mime.multipart.MIMEMultipart()
            msgFrom = 'leungjain@163.com'  # 从该邮箱发送
            msgTo = msgTo  # 发送到该邮箱
            smtpSever = 'smtp.163.com'  # 163邮箱的smtp Sever地址
            smtpPort = '25'  # 开放的端口
            sqm = '7891190129lj'  # 在登录smtp时需要login中的密码应当使用授权码而非账户密码
            msg['from'] = msgFrom
            msg['to'] = msgTo
            msg['subject'] = '曲速智选'
            content = content

            txt = email.mime.text.MIMEText(content)
            msg.attach(txt)
            smtp = smtplib.SMTP()

            '''
            smtplib的connect（连接到邮件服务器）、login（登陆验证）、sendmail（发送邮件）
            '''
            smtp.connect(smtpSever, smtpPort)
            smtp.login(msgFrom, sqm)
            smtp.sendmail(msgFrom, msgTo, str(msg))
            smtp.quit()
            # print('发送成功')
            return True
        except Exception as e:
            print(e)
            # print('发送失败!')
            return False

import os
import shutil
import zipfile


class File:
    """
    create by: zjf and write more
    """
    filename = []

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def rename(cls, src, dst):
        try:
            os.rename(src, dst)
        except Exception as e:
            print(e)

    @classmethod
    def remove_file(cls, file):
        """
        :param file:like "f:zjf/love.png"
        :return:
        """
        try:
            os.remove(file)
        except Exception as e:
            # by:modify leungjian==print(e)->ExceptionInfo(e)
            # The same place behind is the same
            ExceptionInfo(e)

    @classmethod
    def copy_file(cls, src, dst):
        try:
            shutil.copy(src=src, dst=dst)
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def move_file(cls, src, dst):
        try:
            shutil.move(src=src, dst=dst)
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def get_all_file(cls, path):
        alllist = os.listdir(path)
        for ifile in alllist:
            paths = os.path.join(path, ifile)
            # 这里得到的path有可能是文件价
            if os.path.isdir(paths):
                # 是的话需要递归
                cls.get_all_file(path=paths)
            cls.filename.append(paths)
        return cls.filename

    @classmethod
    def decompression(cls, src, dst="temp/"):
        f = zipfile.ZipFile(src, 'r')
        for file in f.namelist():
            f.extract(file, dst)

    @classmethod
    def check_file(cls, path):
        """
        检查文件夹，有返回0
        没有的，新建，返回1
        其他返回-1
        :param path:
        :return:
        """
        # 引入模块
        import os

        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")

        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists = os.path.exists(path)

        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)

            # print(path + ' 创建成功')
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            # print(path + ' 目录已存在')
            return False
        pass

    def create_file(self, path):
        os.mknod(path)
pass
# Email.send_email(msgTo='leungjain@qq.com', content='hhhhhh')
# date1 = dt.datetime(2017, 9, 29)
# print(trading.fix_time(kline='min60', date=date1))
# date2 = dt.datetime(2018, 4, 6)
# # print(trading.trade_days(date1, date2))
# r = trading.is_trade_day(date2)
# print(r)
# sound_notice('alert.wav').start()