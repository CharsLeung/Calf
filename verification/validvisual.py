# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/3/15 16:07
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker as mticker
from Calf.verification import FinanceIndex
from Calf.exception import ExceptionInfo
import datetime as dt

# 中文和负号的正常显示
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')


class ValidVisual:

    @classmethod
    def finance(cls, fi):
        # 使用ggplot的绘图风格
        plt.style.use('ggplot')

        # 构造数据
        values = [3.2, 2.1, 3.5, 2.8, 18]
        feature = ['个人能力', 'QC知识', '解决问题能力', '服务质量意识', '团队精神']

        N = len(values)
        # 设置雷达图的角度，用于平分切开一个圆面
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False)

        # 为了使雷达图一圈封闭起来，需要下面的步骤
        values = np.concatenate((values, [values[0]]))
        angles = np.concatenate((angles, [angles[0]]))

        # 绘图
        fig = plt.figure()
        # 这里一定要设置为极坐标格式
        ax = fig.add_subplot(111, polar=True)
        # 绘制折线图
        ax.plot(angles, values, 'o-', linewidth=2)
        # 填充颜色
        ax.fill(angles, values, alpha=0.25)
        # 添加每个特征的标签
        ax.set_thetagrids(angles * 180 / np.pi, feature)
        # 设置雷达图的范围
        ax.set_ylim(0, 5)
        # 添加标题
        plt.title('活动前后员工状态表现')
        # 添加网格线
        ax.grid(True)
        # 显示图形
        plt.show()

    @classmethod
    def profit(cls, menu, index=None, title=None, save=None):
        m0 = menu.date.min() - dt.timedelta(days=1)
        m1 = m0 - dt.timedelta(days=1)
        menu = menu.append(pd.DataFrame([[m0, 0], [m1, 0]], columns=['date', 'profit']))
        menu.fillna(0, inplace=True)
        menu = menu.sort_values(['date'], ascending=True)
        y = FinanceIndex.already_get(menu.profit.tolist())
        plt.figure(figsize=(12, 6))

        ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=3, colspan=4)
        # ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y%m%d'))
        x = mdates.date2num(menu.date.astype(dt.date))
        ax1.plot(x[1:len(x)], y[1:len(x)], label="profit", linewidth=2)

        ax1.fill_between(x[1:len(x)], 0, y[1:len(x)], alpha=.4)
        if 'index_profit' in menu.columns or index is not None:
            if index is not None:
                index = index.sort_values(['date'], ascending=True)
                iy = FinanceIndex.already_get(index.index_profit.tolist())
                ix = mdates.date2num(index.date.astype(dt.date))
            else:
                iy = FinanceIndex.already_get(menu.index_profit.tolist())
                ix = x
            ax1.plot(ix[1:len(ix)], iy[1:len(ix)], label="index_profit", linewidth=2)
            ax1.fill_between(ix[1:len(ix)], 0, iy[1:len(ix)], alpha=.4)
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
        # plt.xticks(range(len(x)), x, rotation=90)
        ax1.set_xlabel('日期')
        ax1.set_ylabel('累计收益')
        title = '(%s)' % title if title is not None else ''
        ax1.set_title('累计收益/日' + title)
        ax1.legend()

        mth = menu.loc[:, ['date', 'profit']].copy()
        mth['date'] = mth.date.dt.strftime('%Y-%m-%d')
        mth['date'] = mth.date.map(lambda x: x[0:7])
        mth = mth.groupby(['date'], as_index=False).agg({'profit': 'sum'})
        ax2 = plt.subplot2grid((6, 4), (4, 0), rowspan=2, colspan=4)
        xt = list(mth.date.unique())
        x = range(0, len(xt), 1)
        y = mth.profit
        ax2.bar(x, y, label="profit")
        ax2.set_xticks(x)
        ax2.set_xticklabels(xt)
        ax2.set_xlabel('月份')
        ax2.set_ylabel('累计收益')
        ax2.legend()
        # plt.xlabel("")
        # plt.ylabel("")
        # plt.title("累计收益")
        plt.legend()
        if save is not None:
            plt.savefig(filename=save, format='png', transparent=True)
        else:
            plt.show()

    @classmethod
    def profit_bar(cls, menu):
        m0 = menu.date.min() - dt.timedelta(days=1)
        m1 = m0 - dt.timedelta(days=1)
        menu = menu.append(pd.DataFrame([[m0, 0], [m1, 0]], columns=['date', 'profit']))
        menu.fillna(0, inplace=True)
        menu = menu.sort_values(['date'], ascending=True)

        plt.figure(figsize=(12, 6))

        ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=3, colspan=4)
        y = FinanceIndex.already_get(menu.profit.tolist())
        # ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y%m%d'))
        x = mdates.date2num(menu.date.astype(dt.date))
        ax1.plot(x[1:len(x)], y[1:len(x)], label="profit", linewidth=2)

        ax1.fill_between(x[1:len(x)], 0, y[1:len(x)], alpha=.4)
        if 'index_profit' in menu.columns:
            iy = FinanceIndex.already_get(menu.index_profit.tolist())
            ix = x
            ax1.plot(ix[1:len(ix)], iy[1:len(ix)], label="index_profit", linewidth=2)
            ax1.fill_between(ix[1:len(ix)], 0, iy[1:len(ix)], alpha=.4)
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
        # plt.xticks(range(len(x)), x, rotation=90)
        ax1.set_xlabel('日期')
        ax1.set_ylabel('累计收益')
        ax1.set_xlabel('日期')
        ax1.set_title('累计收益/日')
        ax1.legend()

        ax2 = plt.subplot2grid((6, 4), (4, 0), rowspan=2, colspan=4)
        x = mdates.date2num(menu.date.astype(dt.date))
        y = menu.profit
        if 'index_profit' in menu.columns:
            width = 0.4
            x = x
            ax2.bar(x[1:len(x)], y[1:len(x)], label="profit", alpha=.8)
            iy = menu.index_profit
            ix = x
            ax2.bar(ix[1:len(ix)], iy[1:len(ix)], label="index_profit", alpha=.8)
        else:
            ax2.bar(x[1:len(x)], y[1:len(x)], label="profit")
        # ax2.set_xticks(x)
        # ax2.set_xticklabels(xt)
        ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
        ax2.set_xlabel('日期')
        ax2.set_ylabel('累计收益')
        ax2.axhline(0)
        ax1.legend()
        # plt.xlabel("")
        # plt.ylabel("")
        # plt.title("累计收益")
        plt.legend()
        plt.show()

    @classmethod
    def show(cls, kline_data, signals, render_path, title='', mas=[],
             sub_title=None):
        """
        在K线图上标注信号的买卖点
        :param kline_data: K线数据，可以包含均线，均线的columns
        包含在mas中
        :param signals: 必须包含open_date,close_date,open_price,
        close_price,profit,type这几个字段
        :param title:
        :param render_path: html存储的位置
        :param mas: eg.['ma5', 'ma10']
        :param sub_title:
        :return:
        """
        try:
            from pyecharts import Kline, Line, Overlap, Bar

            if sub_title is None:
                lc = len(signals[signals['type'] == False])
                sc = len(signals[signals['type'] == True])
                lr = round(signals[signals['type'] == False].profit.sum() * 100, 2)
                sr = round(signals[signals['type'] == True].profit.sum() * 100, 2)
                info = '多单(数量:{} 收益:{}%) 空单(数量:{} 收益:{}%)'.format(lc, lr, sc, sr)
            else:
                info = sub_title
            ml = []
            for i, r in signals.iterrows():
                if r.type:  # 空单，在图上以绿色表示
                    color = '#0f0'
                else:
                    color = '#f00'
                p = str(round(r.profit * 100, 2)) + '%'
                ml.append([
                    # {'label': {'position': 'middle'}, 'lineStyle': {'color': color}},
                    {'name': 'open', 'coord': [r.open_date, r.open_price], 'value': p,
                     'label': {'position': 'middle'}, 'lineStyle': {'color': color}, 'symbolSize': 5},
                    {'name': 'open', 'coord': [r.close_date, r.close_price], 'symbolSize': 5}
                ])

            data = kline_data.sort_values('date', ascending=True)
            kln = Kline(title=title, subtitle=info, title_pos='center')
            kln.add('Price', data.date.tolist(),
                    data.loc[:, ['open', 'close', 'low', 'high']].as_matrix(),
                    tooltip_tragger="axis", tooltip_axispointer_type='cross',
                    is_legend_show=False, is_more_utils=True, is_xaxis_show=True,
                    # yaxis_min=int(data.low.min() - (data.high.max() - data.low.min()) / 4),
                    is_datazoom_show=True, datazoom_range=[90, 100], xaxis_name='时间',
                    datazoom_type='both',
                    mark_line_raw=ml)

            overlap = Overlap(width=1200, height=600)
            overlap.add(kln)
            for ma in mas:
                overlap.add(
                    Line().add(ma, data.date.tolist(), data[ma].tolist(),
                               tooltip_tragger="axis", is_datazoom_show=True,
                               is_legend_show=True, is_yaxis_show=False,
                               is_xaxis_show=True)
                )
            
            overlap.render(path=render_path)
            pass
        except Exception as e:
            ExceptionInfo(e)
pass