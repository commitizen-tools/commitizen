from commitizen import factory, out


class Schema:
    """Show structure of the rule."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        out.write(self.cz.schema())
