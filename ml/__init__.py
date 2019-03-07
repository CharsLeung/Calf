# encoding: utf-8

"""
@version: 1.1
@author: LeungJain
@time: 2018/3/27 15:27
@describe: 这个包提供了一些我们在量化分析领域常用的机器学习与数据
挖掘算法，它们可能在某些特定的环境中发挥作用
"""
hard_dependencies = ("tensorflow")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(dependency)
