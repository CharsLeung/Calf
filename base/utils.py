# -*- coding: utf-8 -*-
import time

# from configobj import ConfigObj

# from model_data_get import project_dir


def log(*args, **kwargs):
    print(time.strftime("%H:%M:%S", time.localtime()), args, kwargs)


def list_combine(key_list, value_list):
    tmp = zip(key_list, value_list)
    return dict((k, v) for k, v in tmp)


def dict_combine(dict1, dict2):
    for key in dict2.keys():
        if key not in dict1.keys():
            dict1[key] = dict2[key]
        else:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                dict_combine(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
    return dict1
