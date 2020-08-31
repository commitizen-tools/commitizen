from commitizen import cmd, factory, git, out
from commitizen.config import BaseConfig
from commitizen.exceptions import InvalidCommandArgumentError


class Undo:
    """  """

    def __init__(self, config: BaseConfig, arguments: dict):
        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments

    def _get_bump_command(self):
        created_tag = git.get_tags()[0]
        created_commit = git.get_commits()[0]

        if created_tag.rev != created_commit.rev:
            raise InvalidCommandArgumentError(
                "The revision of the latest tag is not equal to the latest commit, use git undo --commit instead\n\n"
                f"Latest Tag: {created_tag.name}, {created_tag.rev}, {created_tag.date}\n"
                f"Latest Commit: {created_commit.title}, {created_commit.rev}"
            )

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
