from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.dart_provider import DartProvider

DART_YAML = """\
name: my_super_package
description: A new Flutter project.

# Bla, bla, bla
publish_to: "none" # Remove this line if you wish to publish to pub.dev

version: 0.1.0+1

environment:
  sdk: ^3.7.2
  # note that this only enforces that the Flutter version is at least the value specified. It does not
  # force it to this specific version
  flutter: 3.29.2

# Bla, bla, bla
dependencies:
  flutter:
    sdk: flutter

  # Some package dependencies
  # network
  dio: ^5.8.0+1

# The following section is specific to Flutter packages.
flutter:
  # The following line ensures that the Material Icons font is
  # included with your application, so that you can use the icons in
  # the material Icons class.
  uses-material-design: true

  # To add assets to your application, add an assets section, like this:
  assets:
    - assets/images/
"""

DART_YAML_FLOAT_PARSEABLE_EXPECTED = """\
name: my_super_package
description: A new Flutter project.

# Bla, bla, bla
publish_to: "none" # Remove this line if you wish to publish to pub.dev

version: 42.1

environment:
  sdk: ^3.7.2
  # note that this only enforces that the Flutter version is at least the value specified. It does not
  # force it to this specific version
  flutter: 3.29.2

# Bla, bla, bla
dependencies:
  flutter:
    sdk: flutter

  # Some package dependencies
  # network
  dio: ^5.8.0+1

# The following section is specific to Flutter packages.
flutter:
  # The following line ensures that the Material Icons font is
  # included with your application, so that you can use the icons in
  # the material Icons class.
  uses-material-design: true

  # To add assets to your application, add an assets section, like this:
  assets:
    - assets/images/
"""

DART_YAML_SEMVER_EXPECTED = """\
name: my_super_package
description: A new Flutter project.

# Bla, bla, bla
publish_to: "none" # Remove this line if you wish to publish to pub.dev

version: 2.3.4

environment:
  sdk: ^3.7.2
  # note that this only enforces that the Flutter version is at least the value specified. It does not
  # force it to this specific version
  flutter: 3.29.2

# Bla, bla, bla
dependencies:
  flutter:
    sdk: flutter

  # Some package dependencies
  # network
  dio: ^5.8.0+1

# The following section is specific to Flutter packages.
flutter:
  # The following line ensures that the Material Icons font is
  # included with your application, so that you can use the icons in
  # the material Icons class.
  uses-material-design: true

  # To add assets to your application, add an assets section, like this:
  assets:
    - assets/images/
"""


@pytest.mark.parametrize(
    "content, expected",
    ((DART_YAML, DART_YAML_FLOAT_PARSEABLE_EXPECTED),),
)
def test_dart_provider_with_float_parseable_new_version(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = DartProvider.package_filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "dart"

    provider = get_provider(config)
    assert isinstance(provider, DartProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)


@pytest.mark.parametrize(
    "content, expected",
    ((DART_YAML, DART_YAML_SEMVER_EXPECTED),),
)
def test_dart_provider_with_semver_new_version(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = DartProvider.package_filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "dart"

    provider = get_provider(config)
    assert isinstance(provider, DartProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("2.3.4")
    assert file.read_text() == dedent(expected)
