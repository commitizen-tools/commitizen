import logging
from typing import Optional
from commitizen.cz import registry
from commitizen.__version__ import __version__

logger = logging.getLogger(__name__)


class Application:
    name: Optional[str] = None

    def __init__(self, name: str):
        self.name = name

    @property
    def cz(self):
        try:
            _cz = registry[self.name]()
        except KeyError:
            msg_error = (
                "The commiter has not been found in the system.\n\n"
                "Try running 'pip install {name}'\n"
            )
            logger.info(msg_error.format(name=self.name))
            raise SystemExit(1)
        else:
            return _cz

    @property
    def version(self):
        return __version__

    def detected_cz(*args, **kwargs):
        print("\n".join(registry.keys()))
