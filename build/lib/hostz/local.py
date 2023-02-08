import os
import platform
import subprocess
from typing import Union

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

    def __repr__(self):
        return '<LocalHost>'

    def check_process(self, keyword):
        result = self.execute(f'pgrep {keyword}')
        return True if result else False

    def exists(self, path):
        return os.path.exists(path)

    def close(self):
        pass

    def mkdirs(self, path):
        os.makedirs(path)

    def execute(self, cmd: str, input: str = None, workspace=None):
        self.debug(cmd)
        workspace = workspace or self.workspace
        if workspace:
            cmd = 'cd %s && %s' % (workspace, cmd)
        if input is None:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
        else:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, input=input.encode(), shell=True)
        result = p.stdout.decode('utf-8').strip()
        self.debug(result)
        return result

    def run(self, cmd, input: str = None, workspace=None):
        return self.execute(cmd, input, workspace)

    def listdir(self, path: str):
        return os.listdir(path)

    def load_yaml(self, path: str):
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)

    def save_yaml(self, data: Union[dict, list], path: str):
        import yaml
        with open(path, 'w') as f:
            yaml.safe_dump(data, f)

    def read(self, path) ->str:
        with open(path) as f:
            return f.read()

    def count_process(self, keyword: str):
        result = self.execute(f"pgrep '{keyword}' | wc -l")
        return int(result.strip(' '))

    def kill(self, keyword):
        return self.execute(f'if [ `pgrep {keyword} | wc -l` -ne 0 ]; then pgrep {keyword} | xargs kill -9; fi')

    def get_dir(self, remote_dir, local_dir, zip=True):
        return self.execute(f'cp -R {remote_dir} {local_dir}')
