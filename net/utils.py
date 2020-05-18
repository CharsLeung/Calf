# encoding: utf-8

"""
project = Calf
file_name = utils
author = Administrator
datetime = 2020/5/18 0018 上午 10:22
from = office desktop
"""
from urllib.request import urlopen


def get_export_ip():
    ip = eval(str(urlopen('http://httpbin.org/ip').read(),
                  'utf-8'))['origin']
    return ip
