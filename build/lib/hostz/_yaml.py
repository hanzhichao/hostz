from typing import Union

from hostz._base_shell import BaseShell


class _Yaml(BaseShell):  # todo filez
    """远端yaml文件解析及保存"""

    def load_yaml(self, path: str) -> Union[dict, list]:
        import yaml
        yml_content = self.read(path)
        return yaml.safe_load(yml_content)

    def save_yaml(self, data: Union[dict, list], path: str):
        import yaml
        yml_content = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        return self.save(yml_content, path)
