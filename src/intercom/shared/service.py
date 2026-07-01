"""Base class for every long-running component in the project.

Receiver, Sender, and any future component (REST server, MQTT bridge,
etc.) must inherit from this so lifecycle management stays consistent
and predictable across the codebase.
"""

from abc import ABC, abstractmethod

from intercom.shared.exceptions import ServiceError
from intercom.shared.logger import logger


class Service(ABC):
    """Defines the start/stop/restart/is_running contract.

    Subclasses implement `_do_start` and `_do_stop` with their actual
    logic; this base class takes care of idempotency and logging so
    every service behaves the same way when called twice or out of order.
    """

    def __init__(self) -> None:
        self._running = False

    @abstractmethod
    def _do_start(self) -> None:
        """Perform the actual startup work."""

    @abstractmethod
    def _do_stop(self) -> None:
        """Perform the actual shutdown work."""

    def start(self) -> None:
        if self._running:
            logger.warning("%s already running, ignoring start()", self._name)
            return

        try:
            self._do_start()
        except Exception as exc:
            raise ServiceError(f"{self._name} failed to start: {exc}") from exc

        self._running = True
        logger.info("%s started", self._name)

    def stop(self) -> None:
        if not self._running:
            logger.warning("%s not running, ignoring stop()", self._name)
            return

        try:
            self._do_stop()
        except Exception as exc:
            raise ServiceError(f"{self._name} failed to stop: {exc}") from exc

        self._running = False
        logger.info("%s stopped", self._name)

    def restart(self) -> None:
        logger.info("%s restarting", self._name)
        self.stop()
        self.start()

    def is_running(self) -> bool:
        return self._running

    @property
    def _name(self) -> str:
        return type(self).__name__
