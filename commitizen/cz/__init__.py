import importlib
import pkgutil
from commitizen.cz.cz_conventional_changelog import ConventionalChangelogCz
from commitizen.cz.cz_jira import JiraSmartCz


registry = {
    name: importlib.import_module(name).discover_this
    for finder, name, ispkg
    in pkgutil.iter_modules()
    if name.startswith('cz_')
}

registry.update({
    'cz_conventional_changelog': ConventionalChangelogCz,
    'cz_jira': JiraSmartCz
})
