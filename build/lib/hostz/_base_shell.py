from logz import log


class BaseShell:
    host: str
    workspace: str
    _logger = log
    _stop_tail = None

    def info(self, message: str):
        self._logger.info('[Host] %s' % message)
        # self._logger.info('[%s] %s' % (self.host, message))
        # self._logger.info('[Host] [%s] %s' % (self.host, message))

    def debug(self, message: str):
        self._logger.debug('[Host] %s' % message)
        # self._logger.debug('[%s] %s' % (self.host, message))
        # self._logger.debug('[Host] [%s] %s' % (self.host, message))

    def execute(self, cmd: str, workspace: str = None) -> str:
        pass

    def exists(self, path) -> bool:
        pass

    def read(self, path) -> str:
        pass

    def save(self, data: str, path: str):
        pass
