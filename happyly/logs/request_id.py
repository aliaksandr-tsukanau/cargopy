from logging import Logger

from attr import attrs

from .base import BaseLogger


@attrs(auto_attribs=True)
class RequestIdLogger(BaseLogger):
    logger: Logger
    topic: str = ''
    request_id: str = ''

    def _fmt(self, message):
        return f' {self.topic:>35} | {self.request_id:>40} |> {message}'

    def info(self, message: str):
        self.logger.info(self._fmt(message))

    def debug(self, message: str):
        self.logger.debug(self._fmt(message))

    def warning(self, message: str):
        self.logger.warning(self._fmt(message))

    def exception(self, message: str):
        self.logger.exception(self._fmt(message))

    def error(self, message: str):
        self.logger.error(self._fmt(message))
