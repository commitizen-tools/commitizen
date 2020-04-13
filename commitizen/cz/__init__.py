import importlib
import pkgutil
from typing import Dict, Type

from commitizen.cz.base import BaseCommitizen
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.cz.jira import JiraSmartCz

registry: Dict[str, Type[BaseCommitizen]] = {
    "cz_conventional_commits": ConventionalCommitsCz,
    "cz_jira": JiraSmartCz,
    "cz_customize": CustomizeCommitsCz,
}
plugins = {
    name: importlib.import_module(name).discover_this  # type: ignore
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith("cz_")
}

registry.update(plugins)
