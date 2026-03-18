from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen.exceptions import CommitMessageLengthExceededError, DryRunExit

if TYPE_CHECKING:
    from pathlib import Path

    from tests.utils import UtilFixture


def _write_pyproject_with_message_length_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, message_length_limit: int
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[tool.commitizen]\n"
        'name = "cz_conventional_commits"\n'
        f"message_length_limit = {message_length_limit}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)


def _mock_commit_prompt(mocker, *, subject: str) -> None:
    mocker.patch(
        "questionary.prompt",
        return_value={
            "prefix": "feat",
            "subject": subject,
            "scope": "",
            "is_breaking_change": False,
            "body": "",
            "footer": "",
        },
    )


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_cli_check_reads_message_length_limit_from_pyproject(
    util: UtilFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    _write_pyproject_with_message_length_limit(tmp_path, monkeypatch, 10)

    long_message_file = tmp_path / "long_message.txt"
    long_message_file.write_text("feat: this is definitely too long", encoding="utf-8")

    with pytest.raises(CommitMessageLengthExceededError):
        util.run_cli("check", "--commit-msg-file", str(long_message_file))


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_cli_commit_reads_message_length_limit_from_pyproject(
    util: UtilFixture,
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    tmp_path: Path,
):
    _write_pyproject_with_message_length_limit(tmp_path, monkeypatch, 10)
    _mock_commit_prompt(mocker, subject="this is definitely too long")
    mocker.patch("commitizen.git.is_staging_clean", return_value=False)

    with pytest.raises(CommitMessageLengthExceededError):
        util.run_cli("commit", "--dry-run")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_cli_check_cli_overrides_message_length_limit_from_pyproject(
    util: UtilFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    _write_pyproject_with_message_length_limit(tmp_path, monkeypatch, 10)

    util.run_cli("check", "-l", "0", "--message", "feat: this is definitely too long")


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_cli_commit_cli_overrides_message_length_limit_from_pyproject(
    util: UtilFixture,
    monkeypatch: pytest.MonkeyPatch,
    mocker,
    tmp_path: Path,
):
    _write_pyproject_with_message_length_limit(tmp_path, monkeypatch, 10)
    _mock_commit_prompt(mocker, subject="this is definitely too long")
    mocker.patch("commitizen.git.is_staging_clean", return_value=False)

    with pytest.raises(DryRunExit):
        util.run_cli("commit", "--dry-run", "-l", "100")
