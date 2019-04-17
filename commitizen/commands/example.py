from commitizen import factory, out


class Example:
    """Show an example so people understands the rules."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        out.write(self.cz.example())
