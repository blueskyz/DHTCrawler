#!/usr/bin/env python
# coding: utf-8


import os
import sys
import time
import json
import random
import traceback as tb

import libtorrent as lt


class Collector(object):
    '''
    一个简单的 bt 下载工具，依赖开源库 libtorrent.
    '''
    # libtorrent下载配置
    _upload_rate_limit = 200000
    _download_rate_limit = 200000
    _active_downloads = 30
    _alert_queue_size = 4000
    _dht_announce_interval = 60
    _torrent_upload_limit = 20000
    _torrent_download_limit = 20000
    _auto_manage_startup = 30
    _auto_manage_interval = 15

    # 主循环 sleep 时间
    _sleep_time = 0.5
    _start_port = 32800
    _sessions = []
    _infohash_queue_from_getpeers = []
    _info_hash_set = {}
    _current_meta_count = 0
    _meta_list = {}

    def __init__(self,
                 session_nums=50,
                 delay_interval=20,
                 exit_time=15*60,
                 result_file=None,
                 stat_file=None):
        self._session_nums = session_nums
        self._delay_interval = delay_interval
        self._exit_time = exit_time
        self._result_file = result_file
        self._stat_file = stat_file
        self._backup_result()

        try:
            with open(self._result_file, 'rb') as f:
                self._meta_list = json.load(f)
        except Exception as err:
            pass

    def _backup_result(self):
        back_file = '%s_%s' % (time.strftime('%Y%m%d'), self._result_file)
        if os.path.isfile(self._result_file) and not os.path.isfile(back_file):
            os.system('cp %s %s_%s' %
                      (self._result_file,
                       time.strftime('%Y%m%d'),
                       self._result_file))

    def _get_runtime(self, interval):
        day = interval / (60*60*24)
        interval = interval % (60*60*24)
        hour = interval / (60*60)
        interval = interval % (60*60)
        minute = interval / 60
        interval = interval % 60
        second = interval
        return 'day: %d, hour: %d, minute: %d, second: %d' % \
               (day, hour, minute, second)

    # 辅助函数
    # 事件通知处理函数
    def _handle_alerts(self, session, alerts):
        while len(alerts):
            alert = alerts.pop()
            if isinstance(alert, lt.add_torrent_alert):
                alert.handle.set_upload_limit(self._torrent_upload_limit)
                alert.handle.set_download_limit(self._torrent_download_limit)
            elif isinstance(alert, lt.dht_announce_alert):
                info_hash = alert.info_hash.to_string().encode('hex')
                if info_hash in self._meta_list:
                    self._meta_list[info_hash] += 1
                else:
                    self._meta_list[info_hash] = 1
                    self._current_meta_count += 1
            elif isinstance(alert, lt.dht_get_peers_alert):
                info_hash = alert.info_hash.to_string().encode('hex')
                if info_hash in self._meta_list:
                    self._meta_list[info_hash] += 1
                else:
                    self._infohash_queue_from_getpeers.append(info_hash)
                    self._meta_list[info_hash] = 1
                    self._current_meta_count += 1

    # 创建 session 对象
    def create_session(self, begin_port=32800):
        self._start_port = begin_port
        for port in range(begin_port, begin_port + self._session_nums):
            session = lt.session()
            session.set_alert_mask(lt.alert.category_t.all_categories)
            session.listen_on(port, port)
            session.add_dht_router('router.bittorrent.com', 6881)
            session.add_dht_router('router.utorrent.com', 6881)
            session.add_dht_router('router.bitcomet.com', 6881)
            session.add_dht_router('dht.transmissionbt.com', 6881)
            settings = session.get_settings()
            settings['upload_rate_limit'] = self._upload_rate_limit
            settings['download_rate_limit'] = self._download_rate_limit
            settings['active_downloads'] = self._active_downloads
            settings['auto_manage_startup'] = self._auto_manage_startup
            settings['auto_manage_interval'] = self._auto_manage_interval
            settings['dht_announce_interval'] = self._dht_announce_interval
            settings['alert_queue_size'] = self._alert_queue_size
            session.set_settings(settings)
            self._sessions.append(session)
        return self._sessions

    # 添加磁力链接
    def add_magnet(self, link):
        # 创建临时下载目录
        if not os.path.isdir('collections'):
            os.mkdir('collections')

        count = 0
        for session in self._sessions:
            params = {'save_path': os.path.join(os.curdir,
                                                'collections',
                                                'magnet_' + str(count)),
                      'storage_mode':
                      lt.storage_mode_t.storage_mode_sparse,
                      'paused': False,
                      'auto_managed': True,
                      'duplicate_is_error': True,
                      'url': link}
            session.async_add_torrent(params)
            count += 1

    def start_work(self):
        # 清理屏幕
        begin_time = time.time()
        show_interval = self._delay_interval
        while True:
            for session in self._sessions:
                session.post_torrent_updates()
                self._handle_alerts(session, session.pop_alerts())
            time.sleep(self._sleep_time)
            if show_interval > 0:
                show_interval -= 1
                continue
            show_interval = self._delay_interval

            # 统计信息显示
            show_content = ['torrents:']
            interval = time.time() - begin_time
            show_content.append('  pid: %s' % os.getpid())
            show_content.append('  time: %s' %
                                time.strftime('%Y-%m-%d %H:%M:%S'))
            show_content.append('  run time: %s' % self._get_runtime(interval))
            show_content.append('  start port: %d' % self._start_port)
            show_content.append('  collect session num: %d' %
                                len(self._sessions))
            show_content.append('  info hash nums from get peers: %d' %
                                len(self._infohash_queue_from_getpeers))
            show_content.append('  torrent collection rate: %f /minute' %
                                (self._current_meta_count * 60 / interval))
            show_content.append('  current torrent count: %d' %
                                self._current_meta_count)
            show_content.append('  total torrent count: %d' %
                                len(self._meta_list))
            show_content.append('\n')

            # 存储运行状态到文件
            try:
                with open(self._stat_file, 'wb') as f:
                    f.write('\n'.join(show_content))
                with open(self._result_file, 'wb') as f:
                    json.dump(self._meta_list, f)
            except Exception as err:
                pass

            # 测试是否到达退出时间
            if interval >= self._exit_time:
                # stop
                break

            # 每天结束备份结果文件
            self._backup_result()

        # 销毁p2p客户端
        for session in self._sessions:
            torrents = session.get_torrents()
            for torrent in torrents:
                session.remove_torrent(torrent)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'argument err:'
        print '\tpython collector.py result.json collector.state\n'
        sys.exit(-1)

    result_file = sys.argv[1]
    stat_file = sys.argv[2]

    # 创建采集对象
    sd = Collector(session_nums=20,
                   result_file=result_file,
                   stat_file=stat_file)
    # 创建p2p客户端
    sd.create_session(32900)
    sd.start_work()
