from __future__ import annotations

import subprocess

from commitizen.providers.base_provider import VersionProvider


class MavenProvider(VersionProvider):
    """
    Maven version management

    ref: https://octopus.com/blog/maven-versioning-explained

    Major.Minor.Patch-BuildNumber-Qualifier

    Precedence:
     - alpha or a
     - beta or b
     - milestone or m
     - rc or cr
     - snapshot
     - (the empty string) or ga or final or release
     - sp
    """

    FULL_VERSION_REGEX = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)[\.-]?(?P<buildnumber>\d+)?[\.-]?(?P<qualifier>\w+)?"

    TAG_FORMAT_REGEXS = {
        "$version": r"(?P<version>.+)",
        "$major": r"(?P<major>\d+)",
        "$minor": r"(?P<minor>\d+)",
        "$patch": r"(?P<patch>\d+)",
        "$buildnumber": r"(?P<buildnumber>\d+)?",
        "$qualifier": r"(?P<qualifier>\w+)?",
    }

    filename = "./pom.xml"

    def __run_cmd(self, cmd) -> str:
        return (
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            .stdout.read()  # type: ignore
            .decode("utf-8")
            .strip()
        )

    def get_version(self, file: str = filename) -> str:
        return self.__run_cmd(
            f"mvn help:evaluate -Dexpression=project.version -q -DforceStdout -f {file}"
        )

    def set_version(self, version: str, file: str = filename) -> None:
        self.__run_cmd(f"mvn versions:set -DnewVersion={version} -f {file}")
