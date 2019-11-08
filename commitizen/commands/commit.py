import contextlib
import os
import tempfile

import questionary

from commitizen import factory, git, out

NO_ANSWERS = 5
COMMIT_ERROR = 6
NO_COMMIT_BACKUP = 7


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: dict, arguments: dict):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments
        self.temp_file: str = os.path.join(tempfile.gettempdir(), "cz.commit.backup")

    def __call__(self):
        retry: bool = self.arguments.get("retry")

        if retry:
            # Check the commit backup file exists
            if not os.path.isfile(self.temp_file):
                out.error("No commit backup found")
                raise SystemExit(NO_COMMIT_BACKUP)

            # Read commit message from backup
            with open(self.temp_file, "r") as f:
                m = f.read().strip()
        else:
            # Prompt user for the commit message
            cz = self.cz
            questions = cz.questions()
            answers = questionary.prompt(questions, style=cz.style)
            if not answers:
                raise SystemExit(NO_ANSWERS)
            m = cz.message(answers)

        out.info(f"\n{m}\n")
        c = git.commit(m)

        if c.err:
            out.error(c.err)

            # Create commit backup
            with open(self.temp_file, "w") as f:
                f.write(m)

            raise SystemExit(COMMIT_ERROR)

        if "nothing added" in c.out or "no changes added to commit" in c.out:
            out.error(c.out)
        elif c.err:
            out.error(c.err)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(self.temp_file)
            out.write(c.out)
            out.success("Commit successful!")
