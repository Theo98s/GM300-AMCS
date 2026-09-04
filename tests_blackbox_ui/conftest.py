# -*- coding: utf-8 -*-
"""UI 测试独立会话、外部环境配置与失败截图。"""
import os
from pathlib import Path

import allure
import pytest
import yaml
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def ui_config():
    """复用外部环境配置，浏览器选项通过 ui 节点覆盖。"""
    root = Path(__file__).resolve().parents[1]
    path = Path(os.environ.get("AMCS_CONFIG_FILE", root / "config/test_config.example.yaml"))
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def pytest_addoption(parser):
    """允许临时指定已安装的浏览器，不修改环境配置。"""
    parser.addoption("--ui-channel", default=None, help="浏览器通道，例如 msedge")


@pytest.fixture(scope="session")
def browser(ui_config, pytestconfig):
    """启动独立浏览器，允许使用本机浏览器通道。"""
    options = ui_config.get("ui", {})
    with sync_playwright() as engine:
        instance = engine.chromium.launch(headless=options.get("headless", True),
                                           channel=pytestconfig.getoption("--ui-channel") or options.get("channel"))
        yield instance
        instance.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """记录执行结果，在页面关闭前判断是否需要截图。"""
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


@pytest.fixture
def page(browser, ui_config, request):
    """每条用例使用全新浏览器会话，失败时附加截图。"""
    context = browser.new_context(base_url=ui_config["base_url"],
                                  ignore_https_errors=not ui_config.get("verify_ssl", False),
                                  viewport={"width": 1440, "height": 1000})
    current = context.new_page()
    current.set_default_timeout(ui_config.get("ui", {}).get("timeout_ms", 15000))
    try:
        yield current
    finally:
        failed = any(getattr(request.node, f"rep_{stage}", None) and
                     getattr(request.node, f"rep_{stage}").failed for stage in ("setup", "call"))
        if failed and not current.is_closed():
            try:
                allure.attach(current.screenshot(full_page=True), name="失败页面", attachment_type=allure.attachment_type.PNG)
            except Exception as error:
                allure.attach(str(error), name="截图失败原因", attachment_type=allure.attachment_type.TEXT)
        context.close()


@pytest.fixture
def logged_in_page(page, ui_config):
    """通过页面输入和点击登录，不使用接口注入会话。"""
    from tests_blackbox_ui.pages.login_page import LoginPage
    login = LoginPage(page)
    login.open()
    login.login(ui_config["username"], ui_config["password"])
    return page
