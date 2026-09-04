"""登录页面操作与页面跳转校验。"""
from playwright.sync_api import expect


class LoginPage:
    """通过真实控件完成登录。"""

    def __init__(self, page):
        """绑定浏览器页面及登录控件。"""
        self.page = page
        self.account = page.locator("#account + .textbox input.textbox-text")
        self.password = page.locator("#password + .textbox input.textbox-text")
        self.submit = page.locator("#btnLogin")

    def open(self):
        """打开登录页并等待输入框可见。"""
        self.page.goto("/amcs/login")
        expect(self.account).to_be_visible()

    def login(self, username, password):
        """提交账号并同时确认业务响应和登录表单消失。"""
        self.account.fill(username)
        self.password.fill(password)
        with self.page.expect_response(lambda response: "/sso/ajaxcheck" in response.url) as pending:
            self.submit.click()
        assert pending.value.status == 200
        assert pending.value.json()["status"] == 0, "页面登录未成功"
        expect(self.account).not_to_be_visible()
