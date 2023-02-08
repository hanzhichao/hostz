import os

from hostz._base_shell import BaseShell


class _Zip(BaseShell):
    def tar(self, path, output=None):
        """tar压缩"""
        output = output or f'{os.path.basename(path)}.tar.gz'
        return self.execute(f'tar -zcf {output} {path}')

    def untar(self, tar_file, output):
        """tar解压缩"""
        return self.execute(f'tar -zxvf {tar_file} -C {output}')

    def zip(self):
        pass

    def unzip(self):
        pass
