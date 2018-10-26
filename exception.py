# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2017/11/24 11:09
"""
import traceback


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def ErrorMessage(message):
    message = '\033[31m' + message + '\033[0m'
    return message


def WarningMessage(message):
    message = '\033[93m' + message + '\033[0m'
    return message


def SuccessMessage(message):
    message = '\033[32m' + message + '\033[0m'
    return message


def ExceptionInfo(e=''):
    trace_info = traceback.format_exc()
    print(ErrorMessage(trace_info + '\n' + str(e)))


class MongoIOError(BaseException):
    def __init__(self, value):
        self.value = value

    @property
    def __str__(self):
        return repr(ErrorMessage('MongoIOError:' + self.value))


class FileError(BaseException):
    def __init__(self, value):
        self.value = value

    @property
    def __str__(self):
        return repr(ErrorMessage('FileError:' + self.value))


class warning(Warning):
    def __init__(self, value):
        self.value = value

    @property
    def __str__(self):
        return repr(WarningMessage('Warning' + self.value))

# print(SuccessMessage("Warning: No active frommets remain. Continue?") +'sddf'+ bcolors.ENDC)
# print('as')
# import sys
# import time
#
#
# def view_bar(num, total):
#     rate = num / total
#     rate_num = int(rate * 100)
#     r = '\r[%s%s]%d%%' % ("=" * num, " " * (100 - num), rate_num,)
#     sys.stdout.write(r)
#     sys.stdout.flush()
#
#
# if __name__ == '__main__':
#     for i in range(0, 101):
#         time.sleep(0.1)
#         view_bar(i, 100)

