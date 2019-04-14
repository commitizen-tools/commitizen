from commitizen import factory


class Schema:
    """Show structure of the rule."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        self.cz.show_schema()
