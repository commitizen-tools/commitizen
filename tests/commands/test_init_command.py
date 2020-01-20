from commitizen import commands


class FakeQuestion:
    def __init__(self, expected_return):
        self.expected_return = expected_return

    def ask(self):
        return self.expected_return


def test_init(tmpdir, mocker, config):
    mocker.patch(
        "questionary.select",
        side_effect=[
            FakeQuestion("pyproject.toml"),
            FakeQuestion("cz_conventional_commits"),
        ],
    )
    mocker.patch("questionary.confirm", return_value=FakeQuestion("y"))
    mocker.patch("questionary.text", return_value=FakeQuestion("y"))
    expected_config = (
        "[tool.commitizen]\n"
        'name = "cz_conventional_commits"\n'
        'version = "0.0.1"\n'
        'tag_format = "y"\n'
    )

    with tmpdir.as_cwd():
        commands.Init(config)()

        with open("pyproject.toml", "r") as toml_file:
            config_data = toml_file.read()

        assert config_data == expected_config


def test_init_when_config_already_exists(config, capsys):
    # Set config path
    path = "tests/pyproject.toml"
    config.add_path(path)

    commands.Init(config)()
    captured = capsys.readouterr()
    assert captured.out == f"Config file {path} already exists\n"
