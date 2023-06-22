# hostz

Easy use for operate remote host via ssh

![Languate - Python](https://img.shields.io/badge/language-python-blue.svg)
![PyPI - License](https://img.shields.io/pypi/l/hostz)
![PyPI](https://img.shields.io/pypi/v/hostz)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hostz)

## Feature

## Install
```
pip install hostz
```

## Simple Use

```
from hostz import Host
host = Host('192.168.1.184', password='***', project_path='/home/hzc/')
print(host.getcwd())
print(host.run('echo hello'))
```

## Todo

