# encoding: utf-8

"""
project = Calf
file_name = __init__.py
author = Administrator
datetime = 2020/5/18 0018 上午 11:03
from = office desktop
"""
hard_dependencies = ("ftplib", "pyftpdlib")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(dependency)

if missing_dependencies:
    # 注意，如果开发人员自建了与系统环境中相同名称的包，可能会抛出包引入异常
    #
    raise ImportError(
        "Missing required dependencies {0}".format(missing_dependencies))
del hard_dependencies, missing_dependencies

from .pyftpserver import FtpServer
from .pyftpclient import FtpClient
