#!/usr/bin/env python
# coding: utf-8


import os

from twisted.application import service, internet
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, utils, task
from twisted.python import log
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile


class CollectorFactory(Factory):
    '''
    采集器工厂
    '''
    def __init__(self, serv):
        self._serv = serv

    def buildProtocol(self, addr):
        return CollectorProtocol(self._serv)


class CollectorProtocol(LineReceiver):
    '''
    接口协议，处理状态查询，服务控制
    '''
    def __init__(self, service):
        self._service = service

    def connectionMade(self):
        self._service.add_query_protocol(self)

    def lostConnection(self):
        self._service.del_query_protocol(self)


class CollectorServices(service.Service):
    '''
    采集进程控制服务
    '''
    _query_protocols = []

    def __init__(self, port):
        self._before_cmds = ['/bin/rm -r -f '
                             '*.log collections/* libtorrent_logs*']
        self._run_cmd = '/usr/bin/python'
        self._run_args = ('collector.py', 'result.json', 'collector.stat')
        self._timeout = 10 * 60
        self._restart_times = 0
        self._work_d = None
        self._task = None
        self._work_stat = None
        self._serv = None
        self._port = port

    def startService(self):
        log.msg('start run collectord')
        if self._work_d is None:
            self._start_work()
        self._task = task.LoopingCall(self._readstat, 'collector.stat')
        self._task.start(10.0)
        log.msg('start listen %d' % self._port)
        self._serv = reactor.listenTCP(self._port, CollectorFactory(self))

    def stopService(self):
        log.msg('stop run collectord')

    def add_query_protocol(self, protocol):
        self._query_protocols.append(protocol)

    def del_query_protocol(self, protocol):
        self._query_protocols.remove(protocol)

    def _start_work(self):
        self._restart_times += 1
        log.msg('restart task times %d' % self._restart_times)
        for cmd in self._before_cmds:
            os.system(cmd)
        self._work_d = utils.getProcessOutput(self._run_cmd,
                                              self._run_args)
        self._work_d.addCallbacks(self._work_finish, self._work_err)

    def _work_finish(self, result):
        log.msg('process exit, msg[%s]' % result)
        self._work_d = None

    def _work_err(self, result):
        log.err('process exit, error[%s]' % result.getErrorMessage())
        self._work_d = None

    def _readstat(self, statfile):
        if self._work_d is None:
            self._start_work()
        if self._query_protocols and os.path.isfile(statfile):
            try:
                with open(statfile, 'rb') as f:
                    self._work_stat = f.read()
            except Exception as err:
                self._work_stat = err.message
                log.err(err.message)

            out = ['run times: %d\n\n' % (self._restart_times),
                   self._work_stat]
            out = ''.join(out)
            for protocol in self._query_protocols:
                protocol.sendLine(out)

# 创建log目录
if not os.path.isdir('./collectord_log'):
    os.mkdir('./collectord_log')

application = service.Application('collectord')
logfile = DailyLogFile('collectord.log', './collectord_log')
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
CollectorServices(31000).setServiceParent(application)
