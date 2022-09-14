import os
import time

import paramiko
from paramiko_expect import SSHClientInteraction

from hostz import Host

host_config = dict(host='9.134.217.247', port=36000, user='root', password=os.getenv('HOST247_PWD'),
                          )


class TestRemoteLinux:

    def test_tail_log(self):
        host = Host(**host_config)
        host.info('hello')
        host.info('hello')
        host.tail('tail -f /home/hzc/chainmaker-go/build/release/chainmaker-v2.3.0_alpha-wx-org1.chainmaker.org/log/system.log',
                  keyword='Consensus')
        host.info('hello')
        host.info('hello')
        host.info('hello')
        host.info('hello')
        host.info('hello')
        time.sleep(5)
        host.stop_tail()

