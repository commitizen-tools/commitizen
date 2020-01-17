from commitizen import commands


def test_init_when_config_already_exists(config, capsys):
    # Set config path
    path = "tests/pyproject.toml"
    config.add_path(path)

    commands.Init(config)()
    captured = capsys.readouterr()
    assert captured.out == f"Config file {path} already exists\n"
