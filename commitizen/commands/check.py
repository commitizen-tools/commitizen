import os
import re

from commitizen import factory, out
from commitizen.config import BaseConfig


NO_COMMIT_MSG = 3
INVALID_COMMIT_MSG = 5


class Check:
    """Check if the current commit msg matches the commitizen format."""

    def __init__(self, config: BaseConfig, arguments: dict, cwd=os.getcwd()):
        """Init method.

        Parameters
        ----------
        config : BaseConfig
            the config object required for the command to perform its action
        arguments : dict
            the arguments object that contains all
            the flags provided by the user

        """
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments: dict = arguments

    def __call__(self):
        """Validate if a commit message follows the conventional pattern.

        Raises
        ------
        SystemExit
            if the commit provided not follows the conventional pattern

        """
        commit_msg_content = self._get_commit_msg()
        pattern = self.cz.schema_pattern()
        if self._has_proper_format(pattern, commit_msg_content) is not None:
            out.success("Commit validation: successful!")
        else:
            out.error("commit validation: failed!")
            out.error("please enter a commit message in the commitizen format.")
            raise SystemExit(INVALID_COMMIT_MSG)

    def _get_commit_msg(self):
        temp_filename: str = self.arguments.get("commit_msg_file")
        return open(temp_filename, "r").read()

    def _has_proper_format(self, pattern, commit_msg):
        return re.match(pattern, commit_msg)
