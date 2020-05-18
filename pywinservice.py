# encoding: utf-8

"""
project = Calf
file_name = pyService
author = Administrator
datetime = 2020/5/18 0018 上午 9:55
from = office desktop
"""
import sys
import time
import win32api
import win32event
import win32service
import win32serviceutil
import servicemanager


class PyService(win32serviceutil.ServiceFramework):
    """
    python windows服务
    """

    _svc_name_ = "PyService"
    _svc_display_name_ = "PyService"
    _svc_description_ = "python Service"

    def __init__(self, args):
        self.log('init')
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('start')
            self.start()
            self.log('wait')
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            self.log('done')
        except BaseException as e:
            self.log('Exception : %s' % e)
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        self.stop()
        self.log('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self):
        # 在这里重载服务
        time.sleep(10000)

    def stop(self):
        pass

    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))

    def sleep(self, minute):
        win32api.Sleep((minute*1000), True)

    def runService(self):
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(PyService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(PyService)
        pass