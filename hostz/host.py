import logging
import os

import paramiko


from hostz._docker import _Docker
from hostz._git import _Git
from hostz._go import _Go
from hostz._sed import _Sed


class Host(_Git, _Go, _Sed, _Docker):
    def __init__(self, host, port=22, user='root', password='passw0rd', workspace=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.workspace = workspace

        self.logger = logging.getLogger(__name__)
        self._ssh = None
        self._sftp = None

    @property
    def ssh(self) -> paramiko.SSHClient:
        if self._ssh is None:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.debug('建立[%s]ssh连接' % self.host)
            self._ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)
        return self._ssh

    @property
    def sftp(self) -> paramiko.SFTPClient:
        if self._sftp is None:
            self._sftp = self.ssh.open_sftp()
        return self._sftp

    def execute(self, cmd: str, workspace=None, timeout=60):
        workspace = workspace or self.workspace
        if workspace:
            cmd = 'cd %s && %s' % (workspace, cmd)
        self.debug(cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)

        result = stderr.read().decode('utf-8') or stdout.read().decode('utf-8').strip(' \n')
        if result:
            self.debug(result)
        return result

    def close(self):
        if self._ssh:
            self.debug('关闭[%s]ssh连接' % self.host)
            self._ssh.close()

    def run(self, cmd: str, input: str = None):
        return self.execute(cmd)

    def tail(self, file_path: str, keyword=None):
        cmd = f'tail -f {file_path}' if keyword is None else f'tail -f {file_path} | grep {keyword}'
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=20 * 60)
        for line in stdout.readlines():
            print(line.decode('utf-8'))

    def read(self, file_path):
        """读取文件内容"""
        return self.execute(f'cat {file_path}')

    def listdir(self, path):
        return self.sftp.listdir(path)

    def exists(self, path):
        """检查远程路径是否存在"""
        try:
            self.sftp.stat(path)
        except IOError:
            return False
        return True

    def count_process(self, keyword):
        result = self.execute(f'pgrep {keyword} | wc -l')
        return int(result.strip(' '))

    def check_process(self, keyword) -> bool:
        """检查进程"""
        result = self.execute(f'pgrep {keyword}')
        return True if result else False

    def put(self, local_file, remote_file):
        """上传文件到服务器"""
        self.sftp.put(local_file, remote_file)
        return self.exists(remote_file)

    def get(self, remote_file, local_file):
        """下载服务端文件"""
        self.sftp.get(remote_file, local_file)
        return os.path.exists(local_file)


    def get_dir(self, remote_dir, local_dir):  # TODO ZIP压缩后下载
        self.logger.debug('下载目录', self.host, remote_dir)
        if not remote_dir.startswith('/'):
            remote_dir = f'{self.sftp.getcwd()}/{remote_dir}'

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        for file in self.sftp.listdir(remote_dir):
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            if self.is_dir(remote_path):
                if not os.path.exists(local_path):
                    # print('下载到', local_path)
                    os.makedirs(local_path)
                self.get_dir(remote_path, local_path)
            else:  # 文件
                self.get(remote_path, local_path)

    def is_dir(self, remote_path):
        return os.stat.S_ISDIR(self.sftp.stat(remote_path).st_mode)

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
        return self.execute(f'if [ `pgrep {keyword} | wc -l` -ne 0 ]; then pgrep {keyword}] | xargs kill -9; fi')

    def grep(self):
        pass

    def tar(self, path, output=None):
        """tar压缩"""
        output = output or f'{os.path.basename(path)}.tar.gz'
        return self.execute(f'tar -zcf {output} {path}')

    def untar(self, tar_file, output):
        """tar解压缩"""
        return self.execute(f'tar -zxvf {tar_file} -C {output}')
