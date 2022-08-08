import os
import platform
import subprocess

from hostz.docker import DockerMixIn
from hostz.git import GitMixIn


class Local(GitMixIn, DockerMixIn):
    def __init__(self, workspace=None, **kwargs):
        self.workspace = self.workspace = workspace
        self.host = 'localhost'
        self.platform = platform.platform()
        if self.workspace:
            if not self.exists(self.workspace):
                self.mkdirs(self.workspace)
            os.chdir(self.workspace)


    def check_process(self, keyword):
        result = self.run(f'pgrep {keyword}')
        return True if result else False

    def exists(self, path):
        return os.path.exists(path)

    def close(self):
        pass

    def mkdirs(self, path):
        os.makedirs(path)

    def run(self, cmd, input=None):
        print(f' [{self.host}]执行命令：%s' % cmd)
        if input is None:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        elif isinstance(input, str):
            p = subprocess.run(cmd, stdout=subprocess.PIPE, input=input.encode(), shell=True)
        else:
            raise TypeError('input must be str')
        result = p.stdout.decode('utf-8').strip()
        print(f' [{self.host}]执行结果：%s' % result)
        return result
