import questionary
from commitizen import factory, out, git


NO_ANSWERS = 5
COMMIT_ERROR = 6


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        cz = self.cz
        questions = cz.questions()
        answers = questionary.prompt(questions)
        if not answers:
            raise SystemExit(NO_ANSWERS)
        m = cz.message(answers)
        out.info(f"\n{m}\n")
        c = git.commit(m)

        if c.err:
            out.error(c.err)
            raise SystemExit(COMMIT_ERROR)

        if "nothing added" in c.out or "no changes added to commit" in c.out:
            out.error(c.out)
        elif c.err:
            out.error(c.err)
        else:
            out.write(c.out)
            out.success("Commit successful!")
