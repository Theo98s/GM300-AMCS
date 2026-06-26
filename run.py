from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORTS_ROOT = ROOT / "reports"
ALLURE_RESULTS = REPORTS_ROOT / "allure-results"
ALLURE_REPORT = REPORTS_ROOT / "allure-report"


def remove_workspace_dir(path: Path):
    resolved = path.resolve()
    if ROOT != resolved and ROOT not in resolved.parents:
        raise RuntimeError(f"Refuse to remove path outside workspace: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


if __name__ == "__main__":
    REPORTS_ROOT.mkdir(exist_ok=True)
    remove_workspace_dir(ALLURE_RESULTS)
    subprocess.run(
        ["pytest", f"--alluredir={ALLURE_RESULTS}"],
        cwd=ROOT,
        check=True,
    )

    if shutil.which("allure") is None:
        print(f"Allure CLI not found. Raw results are available at: {ALLURE_RESULTS}")
        raise SystemExit(0)

    remove_workspace_dir(ALLURE_REPORT)
    try:
        subprocess.run(
            ["allure", "generate", str(ALLURE_RESULTS), "-o", str(ALLURE_REPORT)],
            cwd=ROOT,
            check=True,
        )
    except FileNotFoundError:
        print(f"Allure CLI not found. Raw results are available at: {ALLURE_RESULTS}")
        raise SystemExit(0)
