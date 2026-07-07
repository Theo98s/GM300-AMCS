# -*- coding: utf-8 -*-
"""AMCS black-box API test fixtures.

Responsibilities:
1. Load environment and account configuration.
2. Build shared API clients.
3. Add stable Allure case numbers during collection.
"""
from __future__ import annotations

import sys
from pathlib import Path

import allure
import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from amcs.api.core.auth_api import AuthApi
from amcs.api.modules.alarm_api import AlarmApi
from amcs.api.modules.database_api import DatabaseApi
from amcs.api.modules.history_api import HistoryApi
from amcs.api.modules.patrol_api import PatrolApi
from amcs.api.modules.rdac_api import RdacApi
from amcs.api.modules.video_api import VideoApi
from amcs.api.platform.gis_api import GisApi
from amcs.api.platform.home_api import HomeApi
from amcs.api.platform.menu_api import MenuApi
from amcs.api.platform.plugin_api import PluginApi
from amcs.api.platform.system_api import SystemApi
from amcs.common.request_util import RequestUtil


CASE_INDEX_PREFIX = {
    "test_alarm_api.py": "ALARM",
    "test_auth_login.py": "AUTH-LOGIN",
    "test_database_api.py": "DATABASE",
    "test_gis_api.py": "GIS",
    "test_home_api.py": "HOME",
    "test_history_api.py": "HISTORY",
    "test_patrol_api.py": "PATROL",
    "test_rdac_api.py": "RDAC",
    "test_menu_plugin_api.py": "MENU-PLUGIN",
    "test_system_smoke.py": "SYSTEM-SMOKE",
    "test_video_api.py": "VIDEO",
}


def _case_index_prefix(item) -> str:
    """Build the Allure case-number prefix from the test file name."""
    file_name = Path(str(item.fspath)).name
    if file_name in CASE_INDEX_PREFIX:
        return CASE_INDEX_PREFIX[file_name]
    return Path(str(item.fspath)).stem.replace("test_", "").replace("_", "-").upper()


def pytest_collection_modifyitems(items):
    """Attach a stable AMCS case number to every collected test item."""
    counters = {}
    for item in items:
        prefix = _case_index_prefix(item)
        counters[prefix] = counters.get(prefix, 0) + 1
        case_index = f"AMCS-{prefix}-{counters[prefix]:03d}"
        case_title = getattr(item.obj, "__allure_display_name__", item.name)
        indexed_title = f"[{case_index}] {case_title}"

        item._amcs_case_index = case_index
        item._amcs_case_title = indexed_title
        item.user_properties.append(("case_index", case_index))

        target = getattr(item.obj, "__func__", item.obj)
        setattr(target, "__allure_display_name__", indexed_title)


@pytest.fixture(autouse=True)
def allure_case_index(request):
    """Sync the collected AMCS case number into Allure metadata."""
    case_index = getattr(request.node, "_amcs_case_index", None)
    if not case_index:
        return

    case_title = getattr(request.node, "_amcs_case_title", request.node.name)
    allure.dynamic.title(case_title)
    allure.dynamic.label("case_index", case_index)
    allure.dynamic.tag(case_index)
    allure.dynamic.tag(case_index.rsplit("-", 1)[0])


def load_yaml(path: str):
    """Read a YAML file relative to the project root."""
    with open(PROJECT_ROOT / path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def config():
    """Provide system runtime configuration."""
    return load_yaml("config/config.yaml")


@pytest.fixture(scope="session")
def test_config():
    """Provide test account and environment configuration."""
    return load_yaml("config/test.yaml")


@pytest.fixture(scope="session")
def test_user(test_config):
    """Return the default test account."""
    return {
        "username": test_config["username"],
        "password": test_config["password"],
    }


@pytest.fixture
def request_util(config):
    """Create an isolated RequestUtil per test to avoid session leakage."""
    return RequestUtil(config)


@pytest.fixture
def auth_api(request_util, config):
    """Provide the authentication API client."""
    return AuthApi(request_util, config)


@pytest.fixture
def system_api(request_util, config):
    """Provide the system API client."""
    return SystemApi(request_util, config)


@pytest.fixture
def home_api(request_util, config):
    """Provide the home and dictionary API client."""
    return HomeApi(request_util, config)


@pytest.fixture
def menu_api(request_util, config):
    """Provide the menu API client."""
    return MenuApi(request_util, config)


@pytest.fixture
def plugin_api(request_util, config):
    """Provide the plugin API client."""
    return PluginApi(request_util, config)


@pytest.fixture
def patrol_api(request_util, config):
    """Provide the patrol-management API client."""
    return PatrolApi(request_util, config)


@pytest.fixture
def history_api(request_util, config):
    """Provide the history-record API client."""
    return HistoryApi(request_util, config)


@pytest.fixture
def rdac_api(request_util, config):
    """Provide the RDAC API client."""
    return RdacApi(request_util, config)


@pytest.fixture
def video_api(request_util, config):
    """Provide the video-monitoring API client."""
    return VideoApi(request_util, config)


@pytest.fixture
def alarm_api(request_util, config):
    """Provide the alarm API client."""
    return AlarmApi(request_util, config)


@pytest.fixture
def gis_api(request_util, config):
    """Provide the GIS API client."""
    return GisApi(request_util, config)


@pytest.fixture
def database_api(request_util, config):
    """Provide the base-data API client."""
    return DatabaseApi(request_util, config)
