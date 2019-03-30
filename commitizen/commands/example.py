from commitizen import factory


class Example:
    """Show an example so people understands the rules."""

    def __init__(self, config: dict):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self, *args, **kwargs):
        self.cz.show_example()
