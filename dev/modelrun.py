# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/2/26 14:50
"""
import threading
import time
import datetime as dt
import json
import warnings
# import re
# from timeit import timeit
import pandas as pd
import pytz
from Calf import project_dir
from Calf.deprecation import deprecated
from Calf.exception import ExceptionInfo, WarningMessage
from Calf.utils import trading, fontcolor, sound_notice
from Calf import CalfDateTime
from Calf.dev import ModelAction, calibration
# from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


# from Calf.sys_config import config as cf


class ModelRun:
    """
    实时任务的运行是由两个类型的事件驱动的：

    1.由使用Calf模型的开发者指定时间点的集合，时钟走到相应的时点就运行客服函数。

    2.由K线数据更新这一事件引起的，这种类型的任务我们要求开发者在ModelAction的
    子类申明klines，并将一个list赋给klines，这个list是一个形如
    ['kline_min30','kline_min60']的列表，这意味着当kline_min30或kline_60
    这两个表的数据发生了更新将会驱动ModelRun去执行ModelAction的real函数，
    这里所谓的表的数据发生更新通常是指这种情况：比如在中国A股对于30分钟这一周期来说，
    上午10点钟到了，所有股票10点钟kline_min30的那更K线便产生了，这可能对那些
    依赖于kline_min30的模型而言，就需要去计算新的信号了。其他周期也是相同的道理。
    当然你也可以有其他的定义，总之是因为k线数据发生了更新，这种更新被记录到了
    相应的表中，ModelRun读到这种更新记录后就会执行ModelAction的real函数。
    有关K线更新的日志的相关信息你可以在KlineData中找到.
    """

    @classmethod
    def open_kline_update_log(cls):
        try:
            with open(project_dir + '/Calf/kline_update_log.json', encoding='utf-8') as file:
                content = json.load(file)
            return content
        except Exception as e:
            ExceptionInfo(e)
            return {}

    @classmethod
    def set_kline_update_log(cls, self, **kw):
        try:
            keys = self.keys()
            for k, v in zip(kw.keys(), kw.values()):
                if k in keys:
                    self[k] = v
                else:
                    print(WarningMessage('not find this key in original file'))
            self['datetime'] = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H:%M:%S')
            with open(project_dir + '/Calf/kline_update_log.json', 'w') as file:
                file.write(json.dumps(self))
            return self
        except Exception as e:
            ExceptionInfo(e)
            return self

    @classmethod
    @deprecated("function 'KScheduler' will be removed in next version")
    def KScheduler(cls, action, tz=None, deep_sleep=list()):
        """
        适用于A股的信号采集实时任务，适用于跨时区任务
        :param deep_sleep:
        :param action: 模型的运行管理对象
        :return:
        """
        if not isinstance(action, type(ModelAction)):
            raise TypeError('Object action must be a subclass of ModelAction')
        if tz is not None:
            if tz not in pytz.all_timezones:
                raise ValueError('this tz: %s not in pytz time zones' % tz)
            else:
                tz = pytz.timezone(tz)
        profit_probe_period = dt.timedelta(minutes=1)
        profit_probe_next = dt.datetime.now() if tz is None else dt.datetime.now(tz=tz).replace(tzinfo=None)
        _f = False  # 记录当天是否收盘
        klines = action.klines  # 需要跟踪的bar周期
        _id = cls.open_kline_update_log()  # 记录bar更新
        from Calf.data import KlineData as kd
        while 1:
            try:
                crt = dt.datetime.now() if tz is None else dt.datetime.now(tz=tz).replace(tzinfo=None)
                if not action.is_trade_day(dt.datetime(crt.year, crt.month, crt.day)):
                    print('{0} today is not in business'.format(crt))
                    time.sleep(60 * 60 * 2)  # sleep two hours
                    continue
                if action.trade_day_end(crt) and _f:
                    print(fontcolor.F_GREEN + '-' * 80)
                    print('# %s Today Overview #' % action.name)
                    print('Signal:')
                    action.signals_summary()
                    print('Order:')
                    action.orders_summary()
                    print(fontcolor.F_GREEN + '-' * 80 + fontcolor.END)
                    sound_notice('close.wav').start()
                    _f = False
                # open_am <= crt <= close_am or open_pm <= crt < close_pm
                if action.trade_date(crt):
                    # 交易日盘中
                    s_d = crt - dt.timedelta(minutes=3)
                    e_d = crt + dt.timedelta(minutes=3)
                    log = kd.read_log(start_date=s_d, end_date=e_d, status=200)
                    if len(log):
                        log['_id'] = log['_id'].astype('str')
                        for i, r in log.iterrows():
                            if r.kline in klines and r['_id'] != _id[r.kline]:
                                print('this kline %s find update' % r.kline)
                                action.real(r.kline)
                                print(r.kline + ' id update:' + _id[r.kline] + '-->' + r['_id'])
                                _id[r.kline] = r['_id']
                                cls.set_kline_update_log(_id)

                    if profit_probe_next <= crt:
                        print('profit probing date:{0}'.format(crt))
                        action.probing()
                        profit_probe_next += profit_probe_period
                    _f = True
                    time.sleep(5)
                else:
                    print('{0} this datetime is not in business'.format(crt))
                    profit_probe_next = crt
                    _f = False
                    sleep = 60 * 5 if crt.hour in deep_sleep else 60 * 30
                    time.sleep(sleep)

            except Exception as e:
                ExceptionInfo(e)

    @classmethod
    def forexrun(cls, drive_fun, real_fun, klines):
        """
        适用于外汇市场的实时任务。由于外汇交易是24小时全体候交易，但周末
        一般会休市，以及其他的特殊日期。在中国外汇程序化交易必须通过做市商
        的交易平台进行。Calf裁剪了一些对外汇的功能支持，包括实时收益监控，
        收盘报告。forexrun仅提供了模型信号实时计算的功能。
        forexrun提供了基于K线跟踪的实时信号的采集驱动，包括min5、min15、
        min30、min60、d1
        :param klines:
        :param real_fun: 实时任务
        :param drive_fun: 一个用于判断是否为交易日的函数，
        :return:
        """
        period_m5 = dt.timedelta(minutes=5)
        period_m15 = dt.timedelta(minutes=15)
        period_m30 = dt.timedelta(minutes=30)
        period_h1 = dt.timedelta(hours=1)
        period_d1 = dt.timedelta(days=1)
        now = dt.datetime.now()
        next_m5 = now
        next_m15 = now
        next_m30 = now
        next_h1 = now
        next_d1 = now
        sup_klines = ['forex_min5', 'forex_min15', 'forex_min30', 'forex_min60', 'forex_day1']
        if set(klines) <= set(sup_klines):
            pass
        else:
            raise Exception('The invalid kernel element')
        '''控制在恰当的时间进入系统'''
        tdy = dt.datetime(now.year, now.month, now.day)
        for k in klines:
            if k == 'forex_min5':
                ntm = (now.minute // 5) * 5 + 6
                next_m5 = tdy + dt.timedelta(hours=now.hour, minutes=ntm, seconds=30)
            elif k == 'forex_min15':
                ntm = (now.minute // 15) * 15 + 16
                next_m15 = tdy + dt.timedelta(hours=now.hour, minutes=ntm, seconds=30)
            elif k == 'forex_min30':
                ntm = (now.minute // 30) * 30 + 31
                next_m30 = tdy + dt.timedelta(hours=now.hour, minutes=ntm, seconds=30)
            elif k == 'forex_min60':
                next_h1 = now if now.minute <= 1 else tdy + dt.timedelta(hours=now.hour + 1, minutes=1, seconds=30)
            elif k == 'forex_day1':
                next_d1 = tdy if now.minute <= 1 else tdy + dt.timedelta(days=1, minutes=1, seconds=30)
            else:
                raise Exception('The invalid kernel element')
        print(fontcolor.F_GREEN + '-' * 80 + fontcolor.END)
        print(fontcolor.F_GREEN + 'Calf：Successful entry forex real task', fontcolor.END)
        print(fontcolor.F_GREEN + '-' * 80 + fontcolor.END)
        while 1:
            try:
                current = dt.datetime.now()
                if drive_fun():
                    if next_m5 <= current and 'forex_min5' in klines:
                        # print('min5:', next_m5)
                        real_fun('forex_min5')
                        next_m5 += period_m5
                        print('Task for forex_min5 have completed on {0} and next start up will be {1}'
                              .format(current, next_m5))
                    if next_m15 <= current and 'forex_min15' in klines:
                        # print('min5:', next_m15)
                        real_fun('forex_min15')
                        next_m15 += period_m15
                        print('Task for forex_min15 have completed on {0} and next start up will be {1}'
                              .format(current, next_m15))
                    if next_m30 < current and 'forex_min30' in klines:
                        print('min30:', next_m30)
                        real_fun('forex_min30')
                        next_m30 += period_m30
                        print('Task for forex_min30 have completed on {0} and next start up will be {1}'
                              .format(current, next_m30))
                    if next_h1 < current and 'forex_min60' in klines:
                        print('h1:', next_h1)
                        real_fun('forex_min60')
                        next_h1 += period_h1
                        print('Task for forex_min60 have completed on {0} and next start up will be {1}'
                              .format(current, next_h1))
                    if next_d1 < current and 'forex_day1' in klines:
                        real_fun('forex_day1')
                        next_d1 += period_d1
                        print('Task for forex_day1 have completed on {0} and next start up will be {1}'
                              .format(current, next_d1))
                    time.sleep(60)
                else:
                    print(fontcolor.F_RED + '-' * 80 + fontcolor.END)
                    print(fontcolor.F_RED + 'Note:Non-transaction time;Date:' + str(current), fontcolor.END)
                    print(fontcolor.F_RED + '-' * 80 + fontcolor.END)
                    time.sleep(60 * 60)
            except Exception as e:
                ExceptionInfo(e)

    @classmethod
    def timing(cls, func, times):
        """
        定时任务.
        在交易日执行定时任务
        :param times:
        :param func:形如[[10, 0], [10, 30], [11, 0], [11, 30], [13, 30], [14, 0], [14, 30], [15, 0]]
        这会使得func在每个交易日的10点、10点30分···执行
        :return:
        """
        try:
            warnings.warn(
                "The function  will be deprecated\n"
                "Please use \033[91m DScheduler\033[0m instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            def merge(h, m):
                return pd.Timedelta(hours=h, minutes=m)

            times['time'] = times.apply(lambda r: merge(r['hour'], r['minute']), axis=1)
            times['log'] = pd.datetime(2018, 1, 1)

            def tim(tms):
                while 1:
                    try:
                        crt = dt.datetime.now()
                        if not trading.is_trade_day(crt):
                            print('{0} today is not in business'.format(crt))
                            time.sleep(60 * 60 * 2)  # sleep two hours
                            continue
                        tms['date'] = pd.datetime(crt.year, crt.month, crt.day) + tms.time
                        tm = tms[tms.hour == crt.hour]
                        if len(tm):
                            for i, r in tm.iterrows():
                                if crt >= r.date != r.log:
                                    print('timing task run', r.date, r.log)
                                    func()
                                    tms.at[i, 'log'] = r.date
                                    pass
                            time.sleep(60)
                        else:
                            time.sleep(60 * 60)
                        pass
                    except Exception as ep:
                        ExceptionInfo(ep)

            t = threading.Thread(target=tim, args=(times,))
            t.start()
        except Exception as e:
            ExceptionInfo(e)

    @classmethod
    def rerun(cls, action, deep_sleep=list(), offset=None):
        """
        复盘演示
        :param action:
        :param deep_sleep:
        :param offset:
        :return:
        """
        from Calf.data import KlineData as kd
        profit_probe_period = dt.timedelta(minutes=1)
        profit_probe_next = CalfDateTime.now(offset=offset)
        _f = False  # 记录当天是否收盘
        klines = action.klines  # 需要跟踪的bar周期
        _id = cls.open_kline_update_log()  # 记录bar更新
        while 1:
            try:
                crt = CalfDateTime.now(offset=offset)
                if not trading.is_trade_day(dt.datetime(crt.year, crt.month, crt.day)):
                    print('{0} today is not in business'.format(crt))
                    time.sleep(60 * 60 * 2)  # sleep two hours
                    continue
                if action.trade_day_end(crt) and _f:
                    print(fontcolor.F_GREEN + '-' * 80)
                    print('# %s Today Overview #' % action.name)
                    print('Signal:')
                    action.signals_summary()
                    print('Order:')
                    action.orders_summary()
                    print(fontcolor.F_GREEN + '-' * 80 + fontcolor.END)
                    sound_notice('close.wav').start()
                    _f = False
                # open_am <= crt <= close_am or open_pm <= crt < close_pm
                if action.trade_date(crt):
                    # 交易日盘中
                    s_d = crt - dt.timedelta(minutes=3)
                    e_d = crt + dt.timedelta(minutes=3)
                    log = kd.read_log(start_date=s_d, end_date=e_d, status=200)
                    if len(log):
                        log['_id'] = log['_id'].astype('str')
                        for i, r in log.iterrows():
                            if r.kline in klines and r['_id'] != _id[r.kline]:
                                print('this kline %s find update' % r.kline)
                                action.real(r.kline, start_time=crt)
                                print(r.kline + ' id update:' + _id[r.kline] + '-->' + r['_id'])
                                _id[r.kline] = r['_id']
                                cls.set_kline_update_log(_id)

                    if profit_probe_next <= crt:
                        print('profit probing date:{0}'.format(crt))
                        # action.probing()
                        profit_probe_next += profit_probe_period
                    _f = True
                    time.sleep(5)
                else:
                    print('{0} this datetime is not in business'.format(crt))
                    profit_probe_next = crt
                    _f = False
                    # sleep = 60 * 30
                    # if crt.hour == 9 or crt.hour == 12:
                    #     sleep = 60 * 5
                    sleep = 60 * 5 if crt.hour in deep_sleep else 60 * 30
                    time.sleep(sleep)

            except Exception as e:
                ExceptionInfo(e)

    @classmethod
    def DScheduler(cls, action, start_date=None, execute_date=None, end_date=None,
                   execute_interval=3, tz=None, **kwargs):
        """
        一个依托于时间驱动的实时任务，action所挂载的任务由相应的时间驱动，
        这跟run方法由K线更新驱动不一样，时区功能未起作用
        :param action:
        :param start_date:like '09:30:00'
        :param execute_date:like '09:30:00-11:30:00' or '09:30:00-11:30:00 13:00:00-15:00:00'
        :param end_date:like '15:00:00'
        :param execute_interval:连续任务的执行时间间隔，以秒计
        :param tz:时区
        :return:
        """
        fmt = '%Y-%m-%d %H:%M:%S'
        if start_date is not None:
            try:
                sdt = dt.datetime.strptime('2000-01-01 ' + start_date, fmt)
            except Exception:
                raise TypeError('this start_date param like a "09:30:00" string')
        if execute_date is not None:
            try:
                xdt = []
                dts = execute_date.split(' ')
                for et in dts:
                    t = et.split('-')
                    s = dt.datetime.strptime('2000-01-01 ' + t[0], fmt)
                    e = dt.datetime.strptime('2000-01-01 ' + t[1], fmt)
                    # if s > e:
                    # 如果execute的start大于end说明是当天的end到第二天的start
                    # raise TypeError('execute start datetime must less than end')
                    xdt.append([s, e])
                    del s, e, t
                del dts
            except Exception:
                raise TypeError('this start_date param like a "09:30:00-11:30:00" or'
                                ' "09:30:00-11:30:00 13:00:00-15:00:00"')
        if end_date is not None:
            try:
                edt = dt.datetime.strptime('2000-01-01 ' + end_date, fmt)
            except Exception:
                raise TypeError('this end_date param like a "15:30:00" string')
        if tz is not None:
            if tz not in pytz.all_timezones:
                raise ValueError('Only timezones from the pytz library are supported')
            else:
                tz = pytz.timezone(tz)
        # from pytz import FixedOffset, utc
        from apscheduler.triggers.date import DateTrigger
        from apscheduler.triggers.interval import IntervalTrigger
        from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

        calibration()
        
        while 1:
            # scheduler = BlockingScheduler(daemonic=False)
            # crt = CalfDateTime.now(tz, offset)
            crt = dt.datetime.now() if tz is None else dt.datetime.now(tz=tz).replace(tzinfo=None)
            tdy = dt.datetime(crt.year, crt.month, crt.day)
            # 非交易日
            if not action.is_trade_day(tdy):
                print(fontcolor.F_RED + '-' * 80)
                print('Note:Non-transaction date;Datetime:' + str(crt))
                print('-' * 80 + fontcolor.END)
                delta = (tdy + dt.timedelta(days=1) - crt).seconds
                delta = 1 if delta < 1 else delta
                time.sleep(delta)  # sleep to next day
                continue
            # 交易日
            else:
                try:
                    nsds = list()
                    executors = {'default': ThreadPoolExecutor(4),
                                 'processpool': ProcessPoolExecutor(4)}
                    job_defaults = {'coalesce': True, 'max_instances': 1}
                    scheduler = BackgroundScheduler(executors=executors,
                                                    job_defaults=job_defaults,
                                                    daemonic=False,
                                                    timezone=tz)
                    if start_date is not None:
                        d = tdy + dt.timedelta(hours=sdt.hour, minutes=sdt.minute,
                                               seconds=sdt.second)
                        nsds.append(d + dt.timedelta(days=1))

                        def action_start(args):
                            print(fontcolor.F_GREEN + '-' * 80)
                            print('Calf-Note:start task running on ', dt.datetime.now(tz=tz))
                            print('-' * 80 + fontcolor.END)
                            try:
                                def start(args):
                                    action.start(args=args)

                                t = threading.Thread(target=start, args=(args,))
                                t.start()
                            except Exception as ep:
                                ExceptionInfo(ep)

                        scheduler.add_job(func=action_start, trigger=DateTrigger(d),
                                          id='action_start', args=[kwargs])
                    if execute_date is not None:
                        def action_execute(args):
                            print(fontcolor.F_GREEN + '-' * 80)
                            print('Calf-Note:execute task running on ', dt.datetime.now(tz=tz))
                            print('-' * 80 + fontcolor.END)
                            try:
                                def exe(args):
                                    action.execute(args=args)

                                t = threading.Thread(target=exe, args=(args,))
                                t.start()
                                t.join(execute_interval - 1)
                                # action.execute(args=args)
                            except Exception as ep:
                                ExceptionInfo(ep)

                        for x in xdt:
                            sd = tdy + dt.timedelta(hours=x[0].hour, minutes=x[0].minute,
                                                    seconds=x[0].second)
                            ed = tdy + dt.timedelta(hours=x[1].hour, minutes=x[1].minute,
                                                    seconds=x[1].second)
                            if sd > ed:
                                # 当出现了‘21:30:00-04:00:00’这种类型的格式，表示任务执行时间应该
                                # 从当天的21:30到第二天的04:00
                                ed = ed + dt.timedelta(days=1)
                            else:
                                pass
                            scheduler.add_job(func=action_execute,
                                              trigger=IntervalTrigger(seconds=execute_interval,
                                                                      start_date=sd,
                                                                      end_date=ed), args=[kwargs])
                            nsds.append(sd + dt.timedelta(days=1))

                    if end_date is not None:
                        def action_end(args):
                            print(fontcolor.F_GREEN + '-' * 80)
                            print('Calf-Note:end task running on ', dt.datetime.now(tz=tz))
                            print('-' * 80 + fontcolor.END)
                            try:
                                def end(args):
                                    action.end(args=args)

                                t = threading.Thread(target=end, args=(args,))
                                t.start()
                            except Exception as ep:
                                ExceptionInfo(ep)

                        d = tdy + dt.timedelta(hours=edt.hour, minutes=edt.minute,
                                               seconds=edt.second)
                        nsds.append(d + dt.timedelta(days=1))
                        scheduler.add_job(func=action_end, trigger=DateTrigger(d),
                                          id='action_end', timezone=tz, args=[kwargs])
                    print(fontcolor.F_GREEN + '-' * 80)
                    print('Note:enter Calf real task and mount these tasks:')
                    scheduler.print_jobs()
                    print('Datetime:' + str(crt))
                    print('-' * 80 + fontcolor.END)
                    scheduler.start()
                    # 计算距离下一次启动应该休眠多久
                    if len(nsds) == 0:
                        break
                    # ed = CalfDateTime.now(tz, offset)
                    nd = dt.datetime.now() if tz is None else dt.datetime.now(tz=tz).replace(tzinfo=None)
                    delta = (min(nsds) - nd)
                    delta = delta.seconds + delta.days * 86400 - 1
                    print(fontcolor.F_YELLOW + '-' * 80)
                    print('Note:Calf will sleep {0} seconds and restart on {1}:'.format(delta, min(nsds)))
                    print('Datetime:', str(crt))
                    print('-' * 80 + fontcolor.END)
                    delta = 1 if delta < 1 else delta
                    time.sleep(delta)
                    scheduler.shutdown(wait=False)
                    del scheduler
                except Exception as e:
                    ExceptionInfo(e)
            pass
