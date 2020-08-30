from commitizen import factory, out, cmd, git
from commitizen.config import BaseConfig
from commitizen.exceptions import (
    InvalidCommandArgumentError
)


class Undo:
    """  """

    def __init__(self, config: BaseConfig, arguments: dict):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments

    def _get_bump_command(self):
        latest_tag = git.get_tags()[0]
        latest_commit = git.get_commits()[0]

        if latest_tag.rev != latest_commit.rev:
            raise InvalidCommandArgumentError(
                "The revision of the latest tag is not equal to the latest commit, use git undo --commit instead\n\n"
                f"Latest Tag: {latest_tag.name}, {latest_tag.rev}, {latest_tag.date}\n"
                f"Latest Commit: {latest_commit.title}, {latest_commit.rev}"
            )

        created_tag = git.get_latest_tag_name()
        command = f"git tag --delete {created_tag} && git reset HEAD~ && git reset --hard HEAD"

        return command

    def __call__(self):
        bump: bool = self.arguments.get("bump")
        commit: bool = self.arguments.get("commit")

        if bump:
            command = self._get_bump_command()
        elif commit:
            command = "git reset HEAD~"
        else:
            raise InvalidCommandArgumentError(
                (
                    "One and only one argument is required for check command! "
                    "See 'cz undo -h' for more information"
                )
            )

        c = cmd.run(command)
        if c.err:
            return None
        return c.out.strip()
