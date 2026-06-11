from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ALLURE_RESULTS = ROOT / "allure-results"
ALLURE_REPORT = ROOT / "allure-report"


def remove_workspace_dir(path: Path):
    resolved = path.resolve()
    if ROOT != resolved and ROOT not in resolved.parents:
        raise RuntimeError(f"Refuse to remove path outside workspace: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


if __name__ == "__main__":
    remove_workspace_dir(ALLURE_RESULTS)
    subprocess.run(
        ["pytest", f"--alluredir={ALLURE_RESULTS}"],
        cwd=ROOT,
        check=True,
    )

    remove_workspace_dir(ALLURE_REPORT)
    subprocess.run(
        ["allure", "generate", str(ALLURE_RESULTS), "-o", str(ALLURE_REPORT)],
        cwd=ROOT,
        check=True,
    )
