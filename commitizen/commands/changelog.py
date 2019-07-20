from commitizen import factory, out, changelog


class Changelog:
    """Generate a changelog based on the commit history."""

    def __init__(self, config: dict, *args):
        self.config: dict = config
        self.cz = factory.commiter_factory(self.config)

    def __call__(self):
        self.config
        out.write("changelog")
        changelog
