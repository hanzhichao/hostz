import os
import re
import stat
import zipfile
from threading import Thread

import paramiko
from logz import log
from paramiko_expect import SSHClientInteraction

from hostz._docker import _Docker
from hostz._git import _Git
from hostz._go import _Go
from hostz._sed import _Sed
from hostz._yaml import _Yaml
from hostz._zip import _Zip


class Host(_Git, _Go, _Sed, _Docker, _Yaml, _Zip):
    def __init__(self, host, port=22, user='root', password='password', workspace=None, timeout=600, **kwargs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.workspace = workspace

        self.logger = log
        self._ssh = None
        self._sftp = None
        self._interact = None

    def __repr__(self):
        return f'<Host {self.host}>'

    @classmethod
    def from_str(cls, host: str):
        _user_part, _host_part = host.split('@')
        _user, _password = _user_part.split(':')
        _host, _port, _workspace = _host_part.split(':')
        return cls(host=_host, port=int(_port), user=_user, password=_password, workspace=_workspace)

    @property
    def ssh(self) -> paramiko.SSHClient:
        if self._ssh is None:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.debug(f'connect ssh {self.host}')
            self._ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password,
                              timeout=self.timeout)
        return self._ssh

    @property
    def sftp(self) -> paramiko.SFTPClient:
        if self._sftp is None:
            self._sftp = self.ssh.open_sftp()
        return self._sftp

    @property
    def interact(self) -> SSHClientInteraction:
        if self._interact is None:
            self._interact = SSHClientInteraction(self.ssh, timeout=10, display=False)
            prompt = r'.*root@.*'
            self._interact.expect(prompt)
        return self._interact

    def scp(self, _from: str, _to: str, host: str = None, user: str = None, password: str = None, port: int = 22,
            workspace: str = None):
        file_name = os.path.basename(_from)
        if not re.match(file_name, _to):
            _to = f'{_to}/{file_name}'
        cmd = f'cd {workspace} && scp -P {port} {_from} {user}@{host}:{_to}' if workspace else f'scp -P {port} {_from} {user}@{host}:{_to}'
        self.debug(cmd)
        self.interact.send(cmd)
        self.interact.expect([r'.*Are you sure.*', r".*password:.*"])
        if self.interact.last_match == '.*Are you sure.*':
            self.interact.send('yes')
            self.interact.expect(r".*password:.*")
        if self.interact.last_match == '.*password:.*':
            self.interact.send(password)
        self.interact.expect(f'{file_name}.*')

    def execute(self, cmd: str, workspace=None, timeout: int = None):
        """不带日志输出执行"""
        if timeout is None:
            timeout = self.timeout
        workspace = workspace or self.workspace
        if workspace:
            cmd = 'cd %s && %s' % (workspace, cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
        result = stderr.read().decode('utf-8') or stdout.read().decode('utf-8').strip(' \n')
        return result

    def close(self):
        if self._ssh:
            self.debug('close ssh connection')
            self._ssh.close()

    def run(self, cmd: str, workspace=None, timeout: int = None, show_log: bool = True, tail_result=False,
            return_result=True):
        """带日志执行"""
        if workspace is not None:
            self.debug(f"cd {workspace} && {cmd}")
        else:
            self.debug(cmd)
        result = self.execute(cmd, workspace, timeout)
        if result:
            self.debug(result)
        return result

    def save(self, data, path):
        # return self.execute("echo '%s' > %s" % (data, path))
        file = self.sftp.file(path, "w", -1)
        file.write(data)
        file.flush()

    def tail(self, file_path: str, *keywords, timeout=None):
        self._stop_tail = False
        if not keywords:
            cmd = f'tail -f {file_path}'
        else:
            keyword = '\|'.join(keywords)
            cmd = f'tail -f {file_path} | grep "{keyword}"'
            print('cmd', cmd)

        self.interact.send(cmd)
        stop_callback = lambda x: True if self._stop_tail else False
        t = Thread(target=self.interact.tail, kwargs=dict(stop_callback=stop_callback, timeout=timeout))
        t.start()

    def stop_tail(self):
        """停止tail"""
        self._stop_tail = True

    def read(self, file_path):
        """读取文件内容"""
        return self.execute(f'cat {file_path}')

    def read_multi(self, *file_path, workspace=None) -> list:
        cmd = 'cat %s' % " <(echo '|') ".join(file_path)
        return self.execute(cmd, workspace=workspace).split('|')

    def listdir(self, path):
        return self.sftp.listdir(path)

    def exists(self, path):
        """检查远程路径是否存在"""
        try:
            self.sftp.stat(path)
        except IOError:
            return False
        return True

    def count_process(self, keyword) -> int:
        """根据关键字查询进程数量"""
        result = self.execute(f"pgrep '{keyword}' | wc -l").strip()
        if result:
            return int(result)
        return 0

    def count_process_by_ports(self, ports: list):
        """根据程序监听端口查询进程数量"""
        _ports = '\|'.join(ports)
        cmd = f'netstat -nltp | grep "{_ports}" | grep "LISTEN" | wc -l'
        result = self.execute(cmd).strip()
        if result:
            return int(result)
        return 0

    def check_process(self, keyword) -> bool:
        """检查进程"""
        result = self.execute(f"pgrep '{keyword}'")
        return True if result else False

    def put(self, local_file, remote_file):
        """上传文件到服务器"""
        self.sftp.put(local_file, remote_file)
        return self.exists(remote_file)

    def get(self, remote_file, local_file):
        """下载服务端文件"""
        self.sftp.get(remote_file, local_file)
        return os.path.exists(local_file)

    def get_dir_by_zip(self, remote_dir, local_dir):
        remote_dir_parent, remote_dir_base = os.path.dirname(remote_dir), os.path.basename(remote_dir)
        local_dir_parent, local_dir_base = os.path.dirname(local_dir), os.path.basename(local_dir)
        if not os.path.exists(local_dir_parent):
            os.makedirs(local_dir_parent)
        # 服务端压缩文件
        zip_file = '%s.zip' % remote_dir_base
        cmd = f"cd {remote_dir_parent} && zip -r {zip_file} {remote_dir_base}/*"
        self.execute(cmd)
        # 下载压缩文件
        remote_file = '%s.zip' % remote_dir
        local_file = '%s.zip' % local_dir
        self.get(remote_file, local_file)

        # 删除服务端压缩文件
        self.execute('rm -f %s' % remote_file)

        # 解压本地压缩文件
        # os.system(f'cd {local_dir_parent} && unzip {zip_file} && cd -')
        z = zipfile.ZipFile(local_file)
        z.extractall(path=local_dir_parent)

        # 删除本地压缩文件
        os.system(f'rm -rf {local_file}')

    def get_dir(self, remote_dir, local_dir, zip=True):
        self.debug('download dir form %s:%s->%s' % (self.host, remote_dir, local_dir))
        # 新建本地目录的上级目录
        local_dir_parent = os.path.dirname(local_dir)
        if not os.path.exists(local_dir_parent):
            os.makedirs(local_dir_parent)

        if zip is True:
            return self.get_dir_by_zip(remote_dir, local_dir)
        if not remote_dir.startswith('/'):
            remote_dir = f'{self.sftp.getcwd()}/{remote_dir}'

        for file in self.sftp.listdir(remote_dir):
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            if self.is_dir(remote_path):
                if not os.path.exists(local_path):
                    # self._logger.debug('下载到', local_path)
                    os.makedirs(local_path)
                self.get_dir(remote_path, local_path)
            else:  # 文件
                self.get(remote_path, local_path)

    def is_dir(self, remote_path):
        return stat.S_ISDIR(self.sftp.stat(remote_path).st_mode)

    def check_port(self, port):
        """检查端口号"""
        result = self.execute(f'lsof -i:{port}')
        return True if result else False

    def mkdirs(self, path):
        self.execute(f'mkdir -p {path}')
        result = self.exists(path)
        return result

    def cp(self, _from, _to):
        """复制"""
        return self.execute(f'cp -r {_from} {_to}')

    def mv(self, _from, _to):
        """移动或重命名"""
        return self.execute(f'mv {_from} {_to}')

    def kill(self, keyword):
        """根据关键字杀死进程"""
        return self.execute(f'if [ `pgrep {keyword} | wc -l` -ne 0 ]; then pgrep {keyword} | xargs kill -9; fi')

    def kill_by_pid(self, pid: int):
        return self.execute('kill -9 %s' % pid)

    def grep(self, keyword, file_path):
        return self.execute(f'grep "{keyword}" {file_path}')

    def get_pid_by_port(self, port: int) -> int:
        cmd = "lsof -n -i :%s | grep LISTEN | awk '{print $2}'" % port
        result = self.execute(cmd)
        return int(result) if result else None
