import os
import platform
import subprocess

from hostz._docker import _Docker
from hostz._git import _Git
from hostz._go import _Go
from hostz._sed import _Sed


class Local(_Git, _Go, _Sed, _Docker):
    def __init__(self, workspace=None, **kwargs):
        self.workspace = self.workspace = workspace
        self.host = 'localhost'
        self.platform = platform.platform()
        if self.workspace:
            if not self.exists(self.workspace):
                self.mkdirs(self.workspace)
            os.chdir(self.workspace)

    def check_process(self, keyword):
        result = self.execute(f'pgrep {keyword}')
        return True if result else False

    def exists(self, path):
        return os.path.exists(path)

    def close(self):
        pass

    def mkdirs(self, path):
        os.makedirs(path)

    def execute(self, cmd: str, workspace=None):
        workspace = workspace or self.workspace
        if workspace:
            cmd = 'cd %s && %s' % (workspace, cmd)
        p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        result = p.stdout.decode('utf-8').strip()
        return result

    def run(self, cmd, input=None):
        # print(f' [{self.host}]执行命令：%s' % cmd)
        if input is None:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        elif isinstance(input, str):
            p = subprocess.run(cmd, stdout=subprocess.PIPE, input=input.encode(), shell=True)
        else:
            raise TypeError('input must be str')
        result = p.stdout.decode('utf-8').strip()
        # print(f' [{self.host}]执行结果：%s' % result)
        return result
