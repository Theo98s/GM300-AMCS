# -*- coding: utf-8 -*-
"""AMCS 自动化公共 fixture。

职责包括：
1. 读取环境配置和测试账号。
2. 组装公共 API Client。
3. 给 Allure 自动补充统一的用例编号。
"""
from __future__ import annotations

from pathlib import Path

import allure
import pytest
import yaml

from api.auth_api import AuthApi
from api.system_api import SystemApi
from common.request_util import RequestUtil


CASE_INDEX_PREFIX = {
    "test_auth_login.py": "AUTH-LOGIN",
    "test_system_smoke.py": "SYSTEM-SMOKE",
}


def _case_index_prefix(item) -> str:
    """根据测试文件名生成 Allure 用例编号前缀。"""
    file_name = Path(str(item.fspath)).name
    if file_name in CASE_INDEX_PREFIX:
        return CASE_INDEX_PREFIX[file_name]
    return Path(str(item.fspath)).stem.replace("test_", "").replace("_", "-").upper()


def pytest_collection_modifyitems(items):
    """在收集阶段为每条用例分配稳定编号。"""
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
    """把收集阶段生成的编号同步到 Allure 标题和标签。"""
    case_index = getattr(request.node, "_amcs_case_index", None)
    if not case_index:
        return

    case_title = getattr(request.node, "_amcs_case_title", request.node.name)
    allure.dynamic.title(case_title)
    allure.dynamic.label("case_index", case_index)
    allure.dynamic.tag(case_index)
    allure.dynamic.tag(case_index.rsplit("-", 1)[0])


def load_yaml(path: str):
    """按 UTF-8 读取 YAML 配置文件。"""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def config():
    """提供系统级运行配置。"""
    return load_yaml("config/config.yaml")


@pytest.fixture(scope="session")
def test_config():
    """提供测试账号和环境配置。"""
    return load_yaml("config/test.yaml")


@pytest.fixture(scope="session")
def test_user(test_config):
    """返回测试账号，供登录类用例复用。"""
    return {
        "username": test_config["username"],
        "password": test_config["password"],
    }


@pytest.fixture
def request_util(config):
    """为每条用例创建独立的 RequestUtil，避免会话互相污染。"""
    return RequestUtil(config)


@pytest.fixture
def auth_api(request_util, config):
    """提供认证接口客户端。"""
    return AuthApi(request_util, config)


@pytest.fixture
def system_api(request_util, config):
    """提供系统类接口客户端。"""
    return SystemApi(request_util, config)
