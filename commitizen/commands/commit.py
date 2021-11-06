import contextlib
import os
import selectors
import sys
import tempfile

from asyncio import set_event_loop_policy, get_event_loop_policy, DefaultEventLoopPolicy
from io import IOBase

import questionary

from commitizen import factory, git, out
from commitizen.config import BaseConfig
from commitizen.cz.exceptions import CzException
from commitizen.exceptions import (
    CommitError,
    CustomError,
    DryRunExit,
    NoAnswersError,
    NoCommitBackupError,
    NotAGitProjectError,
    NothingToCommitError,
)


class CZEventLoopPolicy(DefaultEventLoopPolicy):
    def get_event_loop(self):
        self.set_event_loop(self._loop_factory(selectors.SelectSelector()))
        return self._local._loop

class WrapStdx:
    def __init__(self, stdx:IOBase):
        self._fileno = stdx.fileno()
        if sys.platform == 'linux':
            if self._fileno == 0:
                fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
                tty = open(fd, "wb+", buffering=0)
            else:
                tty = open("/dev/tty", "w")
        else:
            fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
            if self._fileno == 0:
                tty = open(fd, "wb+", buffering=0)
            else:
                tty = open(fd, "rb+", buffering=0)
        self.tty = tty

    def __getattr__(self, key):
        if key == "encoding" and (sys.platform != 'linux' or self._fileno == 0) :
            return "UTF-8"
        return getattr(self.tty, key)

    def __del__(self):
        self.tty.close()


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: BaseConfig, arguments: dict):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments
        self.temp_file: str = os.path.join(
            tempfile.gettempdir(),
            "cz.commit{user}.backup".format(user=os.environ.get("USER", "")),
        )

    def read_backup_message(self) -> str:
        # Check the commit backup file exists
        if not os.path.isfile(self.temp_file):
            raise NoCommitBackupError()

        # Read commit message from backup
        with open(self.temp_file, "r") as f:
            return f.read().strip()

    def prompt_commit_questions(self) -> str:
        # Prompt user for the commit message
        cz = self.cz
        questions = cz.questions()
        for question in filter(lambda q: q["type"] == "list", questions):
            question["use_shortcuts"] = self.config.settings["use_shortcuts"]
        try:
            answers = questionary.prompt(questions, style=cz.style)
        except ValueError as err:
            root_err = err.__context__
            if isinstance(root_err, CzException):
                raise CustomError(root_err.__str__())
            raise err

        if not answers:
            raise NoAnswersError()
        return cz.message(answers)

    def __call__(self):
        dry_run: bool = self.arguments.get("dry_run")

        commit_msg_file: str = self.arguments.get("commit_msg_file")
        if commit_msg_file:
            old_stdin = sys.stdin
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            old_event_loop_policy=get_event_loop_policy()
            set_event_loop_policy(CZEventLoopPolicy())
            sys.stdin = WrapStdx(sys.stdin)
            sys.stdout = WrapStdx(sys.stdout)
            sys.stderr = WrapStdx(sys.stderr)

        if git.is_staging_clean() and not dry_run:
            raise NothingToCommitError("No files added to staging!")

        retry: bool = self.arguments.get("retry")

        if retry:
            m = self.read_backup_message()
        else:
            m = self.prompt_commit_questions()

        if commit_msg_file:
            sys.stdin.close()
            sys.stdout.close()
            sys.stderr.close()
            set_event_loop_policy(old_event_loop_policy)
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        out.info(f"\n{m}\n")

        if dry_run:
            raise DryRunExit()

        if commit_msg_file:
            defaultmesaage = ""
            with open(commit_msg_file) as f:
                defaultmesaage = f.read()
            with open(commit_msg_file, "w") as f:
                f.write(m)
                f.write(defaultmesaage)
                out.success("Commit message is successful!")
                return

        signoff: bool = self.arguments.get("signoff")

        if signoff:
            c = git.commit(m, "-s")
        else:
            c = git.commit(m)


        if c.return_code != 0:
            out.error(c.err)

            # Create commit backup
            with open(self.temp_file, "w") as f:
                f.write(m)

            raise CommitError()

        if "nothing added" in c.out or "no changes added to commit" in c.out:
            out.error(c.out)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(self.temp_file)
            out.write(c.err)
            out.write(c.out)
            out.success("Commit successful!")
