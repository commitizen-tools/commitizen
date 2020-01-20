from commitizen import commands


def test_example(config, mocker):
    write_mock = mocker.patch("commitizen.out.write")
    commands.Example(config)()
    write_mock.assert_called_once()


def test_info(config, mocker):
    write_mock = mocker.patch("commitizen.out.write")
    commands.Info(config)()
    write_mock.assert_called_once()


def test_schema(config, mocker):
    write_mock = mocker.patch("commitizen.out.write")
    commands.Schema(config)()
    write_mock.assert_called_once()


def test_list_cz(config, mocker):
    write_mock = mocker.patch("commitizen.out.write")
    commands.ListCz(config)()
    write_mock.assert_called_once()
