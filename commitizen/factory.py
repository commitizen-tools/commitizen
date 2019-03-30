from commitizen import BaseCommitizen, out
from commitizen.cz import registry


NO_COMMITIZEN_FOUND = 2


def commiter_factory(config: dict) -> BaseCommitizen:
    """Return the correct commitizen existing in the registry."""
    name: str = config["name"]
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
