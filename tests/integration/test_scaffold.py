from __future__ import annotations

import os
import tomllib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import scaffold


TYPE_EXPECTATIONS = {
    "cli": ("app/cli", "app/adapters/input/cli/commands"),
    "web": ("app/web", "app/adapters/input/rest"),
    "telegram": ("app/telegram", "app/adapters/input/telegram"),
    "airflow": ("app/airflow", "app/adapters/input/airflow"),
    "lib": ("app/lib", "app/adapters/input/lib"),
}


@pytest.mark.parametrize("project_type", tuple(TYPE_EXPECTATIONS))
def test_scaffold_main_local_template(project_type: str, tmp_path: Path) -> None:
    project_name = f"{project_type}_demo"
    inputs = [project_name, project_type, "none", ""]
    template_root = Path(__file__).resolve().parents[2]

    def fake_run(command: list[str], cwd: Path, check: bool) -> Mock:
        assert check is True
        assert cwd == tmp_path / project_name
        return Mock()

    with (
        patch.dict(os.environ, {scaffold.TEMPLATE_DIR_ENV: str(template_root)}, clear=False),
        patch("scaffold.Path.cwd", return_value=tmp_path),
        patch("scaffold.shutil.which", return_value="/usr/bin/uv"),
        patch("scaffold._tty_input", side_effect=inputs),
        patch("scaffold.subprocess.run", side_effect=fake_run) as run_mock,
    ):
        assert scaffold.main() == 0

    package_root = tmp_path / project_name / project_name
    main_subtree, adapter_subtree = TYPE_EXPECTATIONS[project_type]

    assert (package_root / "core/domain").exists()
    assert (package_root / "infrastructure").exists()
    assert (package_root / main_subtree).exists()
    assert (package_root / adapter_subtree).exists()
    pyproject = tomllib.loads((tmp_path / project_name / "pyproject.toml").read_text(encoding="utf-8"))
    if project_type == "cli":
        assert (package_root / "app/adapters/input/cli/args.py").exists()
        assert pyproject["project"]["scripts"][project_name] == (
            f"{project_name}.app.adapters.input.cli:app"
        )
    assert (tmp_path / project_name / "main.py").exists()

    commands = [call.args[0] for call in run_mock.call_args_list]
    assert commands == [["git", "init"], ["git", "add", "-A"], ["uv", "sync"]]
