# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/2/7 17:33
"""
hard_dependencies = ("pymongo")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(dependency)