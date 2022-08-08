import logging
import os

import paramiko

from hostz.docker import DockerMixIn
from hostz.git import GitMixIn
from hostz.go import GoMixIn
from hostz.sed import SedMixIn

DEFAULT_SSH_PORT = os.getenv('DEFAULT_SSH_PORT') or 22
DEFAULT_SSH_USER = os.getenv('DEFAULT_SSH_USER') or 'root'
DEFAULT_SSH_PASSWORD = os.getenv('DEFAULT_SSH_PASSWORD') or 'passw0rd'
DEFAULT_SSH_TIMEOUT = os.getenv('DEFAULT_SSH_TIMEOUT') or 60
DEFAULT_SSH_WORKSPACE = os.getenv('DEFAULT_SSH_WORKSPACE') or None


class SftpMixIn:
    sftp: paramiko.SFTPClient

    def listdir(self, path="."):
        return self.sftp.listdir(path)

    def open(self, filename, mode="r", bufsize=-1):
        return self.sftp.open(filename, mode, bufsize)

    def remove(self, path):
        return self.sftp.remove(path)

    def rename(self, oldpath, newpath):
        return self.sftp.rename(oldpath, newpath)

    def mkdir(self, path, mode=511):
        return self.sftp.mkdir(path, mode)

    def rmdir(self, path):
        return self.sftp.rmdir(path)

    def getcwd(self):
        return self.sftp.getcwd()

    def chdir(self, path=None):
        return self.sftp.chdir(path)

    def put(self, local_file, remote_file):
        """上传文件到服务器"""
        self.sftp.put(local_file, remote_file)
        return self.exists(remote_file)

    def get(self, remote_file, local_file):
        """下载服务端文件"""
        self.sftp.get(remote_file, local_file)
        return os.path.exists(local_file)

    def get_dir(self, remote_dir, local_dir):
        if not remote_dir.startswith('/'):
            remote_dir = f'{self.sftp.getcwd()}/{remote_dir}'
            print(remote_dir)

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        for file in self.sftp.listdir(remote_dir):
            local_path = os.path.join(local_dir, file)
            remote_path = os.path.join(remote_dir, file)
            if self.is_dir(remote_path):
                if not os.path.exists(local_path):
                    print('local path', local_path)
                    os.makedirs(local_path)
                self.get_dir(remote_path, local_path)
            else:  # 文件
                self.get(remote_path, local_path)

    def is_dir(self, remote_path):
        return os.stat.S_ISDIR(self.sftp.stat(remote_path).st_mode)


class Host(SftpMixIn, GoMixIn, DockerMixIn, GitMixIn, SedMixIn):
    def __init__(self, host, port=DEFAULT_SSH_PORT, user=DEFAULT_SSH_USER, password=DEFAULT_SSH_PASSWORD,
                 timeout=DEFAULT_SSH_TIMEOUT, workspace=DEFAULT_SSH_WORKSPACE, connect=True):
        self.host = host
        self.password = password
        self.port = port
        self.user = user
        self.timeout = timeout
        self.workspace = workspace

        self.ssh = paramiko.SSHClient()
        self.ssh.banner_timeout = timeout
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp: paramiko.SFTPClient = None

        if connect is True:
            self.connect()

    def connect(self):
        self.ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)
        self.sftp = self.ssh.open_sftp()
        if self.workspace and self.exists(self.workspace):
            self.sftp.chdir(self.workspace)

    def close(self):
        self.ssh.close()

    def run(self, cmd: str, input: str = None):
        print(f' [{self.host}]执行命令: %s' % cmd)
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=20 * 60)
        if input is not None:
            stdin.channel.send(input.encode('utf-8'))
            stdin.channel.shutdown_write()
        result = stderr.read().decode('utf-8') or stdout.read().decode('utf-8')
        logging.debug(result.strip('\n'))
        print(f' 执行结果: %s' % result.strip('\n'))
        return result.strip('\n')

    def tail(self, file_path: str, keyword=None):
        cmd = f'tail -f {file_path}' if keyword is None else f'tail -f {file_path} | grep {keyword}'
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=20 * 60)
        for line in stdout.readlines():
            print(line.decode('utf-8'))

    def read(self, file_path):
        """读取文件内容"""
        return self.run(f'cat {file_path}')

    def listdir(self, path):
        return self.sftp.listdir(path)

    def exists(self, path):
        """检查远程路径是否存在"""
        # result = self.run(f'if [ -e {path} ]; then echo "{path} exists";fi')
        # return True if result else False
        try:
            self.sftp.stat(path)
        except IOError:
            return False
        return True

    def count_process(self, keyword):
        result = self.run(f'pgrep {keyword} | wc -l')
        return int(result.strip(' '))

    def check_process(self, keyword) -> bool:
        """检查进程"""
        # result = self.run(f'ps -ef | grep {keyword} | grep -v "grep"')
        result = self.run(f'pgrep {keyword}')
        return True if result else False

    def put(self, local_file, remote_file):
        """上传文件到服务器"""
        self.sftp.put(local_file, remote_file)
        return self.exists(remote_file)

    def get(self, remote_file, local_file):
        """下载服务端文件"""
        self.sftp.get(remote_file, local_file)
        return os.path.exists(local_file)

    def mkdir(self, path):
        # todo
        pass

    # def get_dir(self, remote_dir, local_dir):
    #
    #     tar_name = '%s.tar' % os.path.basename(remote_dir)
    #     cur_path = self.sftp.getcwd()
    #     cmd = f"tar -zcPf {tar_name} {remote_dir}"
    #     stdin, stdout, stderr = self.ssh.exec_command(cmd)
    #
    #     result = self.run(cmd)
    #     remote_file = '%s.tar' % remote_dir
    #
    #     local_dir_parent = os.path.dirname(local_dir)
    #     local_file = '%s.tar' % local_dir
    #     self.get(remote_file, local_file)
    #     self.run('rm -f %s' % remote_file)
    #     os.system(f'cd {local_dir_parent} && tar -zxvf {local_file} && cd -')

    def get_dir(self, remote_dir, local_dir):  # TODO ZIP压缩后下载
        print('下载目录', self.host, remote_dir)
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
        result = self.run(f'lsof -i:{port}')
        return True if result else False

    def mkdirs(self, path):
        self.run(f'mkdir -p {path}')
        result = self.exists(path)
        return result

    def cp(self, _from, _to):
        """复制"""
        return self.run(f'cp -r {_from} {_to}')

    def mv(self, _from, _to):
        """移动或重命名"""
        return self.run(f'mv {_from} {_to}')

    def kill(self, keyword):
        """根据关键字杀死进程"""
        return self.run(f'if [ `pgrep {keyword} | wc -l` -ne 0 ]; then pgrep {keyword}] | xargs kill -9; fi')

    def grep(self):
        pass

    def tar(self, path, output=None):
        """tar压缩"""
        output = output or f'{os.path.basename(path)}.tar.gz'
        return self.run(f'tar -zcf {output} {path}')

    def untar(self, tar_file, output):
        """tar解压缩"""
        return self.run(f'tar -zxvf {tar_file} -C {output}')
