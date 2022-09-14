import logging


class BaseShell:
    host: str
    workspace: str
    logger = logging.getLogger(__name__)

    def info(self, message: str):
        self.logger.info('[%s] %s' % (self.host, message))

    def debug(self, message: str):
        self.logger.debug('[%s] %s' % (self.host, message))

    def execute(self, cmd: str, workspace: str=None) -> str:
        pass

    def exists(self, path) -> bool:
        pass

    def read(self, path)->str:
        pass

    def save(self, data: str, path: str):
        pass
