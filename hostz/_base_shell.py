from logz import log


class BaseShell:
    host: str
    workspace: str
    logger = log

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
