import os
import re

from commitizen import out

PATTERN = (
    r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert)"
    r"(\([\w\-]+\))?:\s.*"
)
NO_COMMIT_MSG = 3
INVALID_COMMIT_MSG = 5


class Check:
    """Check if the current commit msg is a conventional commit."""

    def __init__(self, config: dict, arguments: dict, cwd=os.getcwd()):
        """Init method.

        Parameters
        ----------
        config : dict
            the config object required for the command to perform its action
        arguments : dict
            the arguments object that contains all
            the flags provided by the user

        """
        self.config: dict = config
        self.arguments: dict = arguments

    def __call__(self):
        """Validate if a commit message follows the conventional pattern.

        Raises
        ------
        SystemExit
            if the commit provided not follows the conventional pattern

        """
        commit_msg_content = self._get_commit_msg()
        if self._is_conventional(PATTERN, commit_msg_content) is not None:
            out.success("Conventional commit validation: successful!")
        else:
            out.error("conventional commit validation: failed!")
            out.error("please enter a commit message in the conventional format.")
            raise SystemExit(INVALID_COMMIT_MSG)

    def _get_commit_msg(self):
        temp_filename: str = self.arguments.get("commit_msg_file")
        return open(temp_filename, "r").read()

    def _is_conventional(self, pattern, commit_msg):
        return re.match(PATTERN, commit_msg)
