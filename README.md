# hostz

Easy use for operate remote host via ssh

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

