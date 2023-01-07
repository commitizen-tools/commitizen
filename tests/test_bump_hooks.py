from commitizen import hooks


def test_format_env():
    result = hooks._format_env("TEST_", {"foo": "bar", "bar": "baz"})
    assert "TEST_FOO" in result and result["TEST_FOO"] == "bar"
    assert "TEST_BAR" in result and result["TEST_BAR"] == "baz"
