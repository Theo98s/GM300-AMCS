# -*- coding: utf-8 -*-
"""AMCS 黑盒接口测试夹具。

职责说明：
1. 加载环境与账号配置。
2. 构建共享的接口客户端。
3. 在收集阶段为用例补充稳定的 Allure 编号。
"""
from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path

import allure
import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
DEFAULT_TEST_CONFIG_PATH = PROJECT_ROOT / "config" / "test_config.example.yaml"
TEST_CONFIG_ENV = "AMCS_CONFIG_FILE"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from amcs.api.core.auth_api import AuthApi
from amcs.api.modules.alarm_api import AlarmApi
from amcs.api.modules.database_api import DatabaseApi
from amcs.api.modules.equipment_api import EquipmentApi
from amcs.api.modules.history_api import HistoryApi
from amcs.api.modules.image_recognition_api import ImageRecognitionApi
from amcs.api.modules.patrol_api import PatrolApi
from amcs.api.modules.patrol_point_api import PatrolPointApi
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
    """根据测试文件名生成 Allure 用例编号前缀。"""
    file_name = Path(str(item.fspath)).name
    if file_name in CASE_INDEX_PREFIX:
        return CASE_INDEX_PREFIX[file_name]
    return Path(str(item.fspath)).stem.replace("test_", "").replace("_", "-").upper()


def pytest_collection_modifyitems(items):
    """为每个收集到的测试项挂载稳定的 AMCS 用例编号。"""
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
    """把收集阶段生成的 AMCS 用例编号同步到 Allure 元数据。"""
    case_index = getattr(request.node, "_amcs_case_index", None)
    if not case_index:
        return

    case_title = getattr(request.node, "_amcs_case_title", request.node.name)
    allure.dynamic.title(case_title)
    allure.dynamic.label("case_index", case_index)
    allure.dynamic.tag(case_index)
    allure.dynamic.tag(case_index.rsplit("-", 1)[0])


def _resolve_external_config_path() -> Path:
    """解析当前环境要使用的 AMCS 配置文件。

    项目默认使用 config/test_config.example.yaml，因此当前环境开箱即用。
    如果要切换到其他环境，可通过设置 AMCS_CONFIG_FILE 指向本地 YAML 文件，
    无需修改测试代码。
    """
    override_path = os.environ.get(TEST_CONFIG_ENV)
    if override_path:
        return Path(override_path).expanduser().resolve()
    return DEFAULT_TEST_CONFIG_PATH


def load_yaml(path: Path):
    """读取 YAML 文件，并始终返回字典对象。"""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


@pytest.fixture(scope="session")
def test_config():
    """提供可由外部配置切换的账号、地址、线路和所亭参数。"""
    return load_yaml(_resolve_external_config_path())


@pytest.fixture(scope="session")
def config(test_config):
    """把稳定接口路径与外部环境运行参数合并成最终配置。"""
    merged_config = deepcopy(load_yaml(PROJECT_ROOT / "config" / "config.yaml"))
    for key in ("env", "base_url", "timeout", "verify_ssl"):
        if key in test_config:
            merged_config[key] = test_config[key]
    return merged_config


@pytest.fixture(scope="session")
def test_user(test_config):
    """返回默认测试账号。"""
    return {
        "username": test_config["username"],
        "password": test_config["password"],
    }


@pytest.fixture(scope="session")
def target_config(test_config):
    """返回供环境敏感用例使用的线路、所亭和协议配置。"""
    return test_config.get("targets", {})


@pytest.fixture
def request_util(config):
    """为每条用例创建独立的 RequestUtil，避免会话串用。"""
    return RequestUtil(config)


@pytest.fixture
def auth_api(request_util, config):
    """提供认证接口客户端。"""
    return AuthApi(request_util, config)


@pytest.fixture
def system_api(request_util, config):
    """提供系统接口客户端。"""
    return SystemApi(request_util, config)


@pytest.fixture
def home_api(request_util, config):
    """提供首页与字典接口客户端。"""
    return HomeApi(request_util, config)


@pytest.fixture
def menu_api(request_util, config):
    """提供菜单接口客户端。"""
    return MenuApi(request_util, config)


@pytest.fixture
def plugin_api(request_util, config):
    """提供插件接口客户端。"""
    return PluginApi(request_util, config)


@pytest.fixture
def patrol_api(request_util, config):
    """提供巡检管理接口客户端。"""
    return PatrolApi(request_util, config)


@pytest.fixture
def patrol_point_api(request_util, config):
    """提供巡检点位管理接口客户端。"""
    return PatrolPointApi(request_util, config)


@pytest.fixture
def image_recognition_api(request_util, config):
    """提供图像识别配置接口客户端。"""
    return ImageRecognitionApi(request_util, config)


@pytest.fixture
def history_api(request_util, config):
    """提供历史记录接口客户端。"""
    return HistoryApi(request_util, config)


@pytest.fixture
def rdac_api(request_util, config):
    """提供 RDAC 接口客户端。"""
    return RdacApi(request_util, config)


@pytest.fixture
def video_api(request_util, config):
    """提供视频监控接口客户端。"""
    return VideoApi(request_util, config)


@pytest.fixture
def alarm_api(request_util, config):
    """提供报警接口客户端。"""
    return AlarmApi(request_util, config)


@pytest.fixture
def gis_api(request_util, config):
    """提供 GIS 接口客户端。"""
    return GisApi(request_util, config)


@pytest.fixture
def database_api(request_util, config):
    """提供基础数据库接口客户端。"""
    return DatabaseApi(request_util, config)


@pytest.fixture
def equipment_api(request_util, config):
    """提供基础数据设备管理接口客户端。"""
    return EquipmentApi(request_util, config)
