"""登录页面基础功能，不执行可能锁定现场账号的错误密码重试。"""
import allure
import re
from playwright.sync_api import expect
from tests_blackbox_ui.pages.login_page import LoginPage


@allure.title("UI 登录表单展示及密码遮蔽")
def test_login_form(page):
    """检查账号、密码和登录按钮可见，密码类型保持遮蔽。"""
    login = LoginPage(page)
    login.open()
    expect(login.password).to_be_visible()
    # EasyUI 密码控件使用文本框显示掩码字符，而非原生密码类型。
    login.password.fill("ui-mask-check")
    login.account.click()
    expect(login.password).to_have_value(re.compile(r"[●•*]{13}"))
    expect(login.submit).to_be_visible()


@allure.title("UI 正确账号登录并在刷新后保持会话")
def test_login_session_survives_reload(logged_in_page):
    """刷新登录后的页面，不应再次出现登录表单。"""
    logged_in_page.reload()
    expect(LoginPage(logged_in_page).account).not_to_be_visible()
    assert "/amcs/login" not in logged_in_page.url
