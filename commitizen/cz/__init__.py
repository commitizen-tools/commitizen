import importlib
import logging
import pkgutil
from typing import Dict, Type

from commitizen.cz.base import BaseCommitizen
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.cz.jira import JiraSmartCz

logger = logging.getLogger(__name__)


def discover_plugins():
    plugins = {}
    for finder, name, ispkg in pkgutil.iter_modules():
        try:
            if name.startswith("cz_"):
                plugins[name] = importlib.import_module(name).discover_this
        except AttributeError as e:
            logger.warning(e.args[0])
            continue
    return plugins


registry: Dict[str, Type[BaseCommitizen]] = {
    "cz_conventional_commits": ConventionalCommitsCz,
    "cz_jira": JiraSmartCz,
    "cz_customize": CustomizeCommitsCz,
}

registry.update(discover_plugins())
