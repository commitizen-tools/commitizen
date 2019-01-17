import importlib
import pkgutil
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.jira import JiraSmartCz


registry = {
    name: importlib.import_module(name).discover_this
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith("cz_")
}

registry.update(
    {"cz_conventional_commits": ConventionalCommitsCz, "cz_jira": JiraSmartCz}
)
