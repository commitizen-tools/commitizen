from commitizen import BaseCommitizen, out
from commitizen.config import BaseConfig
from commitizen.cz import registry
from commitizen.error_codes import NO_COMMITIZEN_FOUND


def commiter_factory(config: BaseConfig) -> BaseCommitizen:
    """Return the correct commitizen existing in the registry."""
    name: str = config.settings["name"]
    try:
        _cz = registry[name](config)
    except KeyError:
        msg_error = (
            "The commiter has not been found in the system.\n\n"
            f"Try running 'pip install {name}'\n"
        )
        out.error(msg_error)
        raise SystemExit(NO_COMMITIZEN_FOUND)
    else:
        return _cz
