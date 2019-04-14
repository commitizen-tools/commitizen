from commitizen import factory


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        self.cz.run()
