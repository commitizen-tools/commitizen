from commitizen import BaseCommitizen
from commitizen.config import BaseConfig
from commitizen.cz import registry
from commitizen.exceptions import NoCommitizenFoundException


def commiter_factory(config: BaseConfig) -> BaseCommitizen:
    """Return the correct commitizen existing in the registry."""
    name: str = config.settings["name"]
    try:
        _cz = registry[name](config)
    except KeyError:
        msg_error = (
            "The committer has not been found in the system.\n\n"
            f"Try running 'pip install {name}'\n"
        )
        raise NoCommitizenFoundException(msg_error)
    else:
        return _cz
