# -*- coding: utf-8 -*-
"""AMCS 登录认证接口封装。

AMCS 当前登录链路不是常见的 JSON token 登录，而是：
1. 先打开登录页，拿到页面里的 CSRFToken 和会话 cookie。
2. 再向 /sso/ajaxcheck 提交表单，完成登录。
"""
from __future__ import annotations

import re
from typing import Any


class AuthApi:
    """处理 CSRF + session 登录链路。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化登录页地址和登录提交地址。"""
        self.request_util = request_util
        self.config = config
        self.login_page_url = config["auth"]["login_page_url"]
        self.login_submit_url = config["auth"]["login_submit_url"]

    def get_login_page(self):
        """获取登录页 HTML，用于提取 CSRFToken。"""
        return self.request_util.send_request("get", self.login_page_url)

    @staticmethod
    def extract_csrf_token(html: str) -> str:
        """从登录页脚本中提取 csrftoken 变量。"""
        match = re.search(r'var csrftoken = "([^"]+)"', html)
        assert match, "登录页未找到 csrftoken"
        return match.group(1)

    def login(self, account: str, password: str):
        """执行登录。

        注意这里提交的是前端表单风格的 account/password/CSRFToken，
        登录成功后会话保存在 RequestUtil 的 Session 里，后续接口可以直接复用。
        """
        login_page = self.get_login_page()
        assert login_page.status_code == 200
        csrf_token = self.extract_csrf_token(login_page.text)

        # 这里沿用系统前端的表单字段命名，避免和实际登录链路不一致。
        payload = {
            "account": account,
            "password": password,
            "CSRFToken": csrf_token,
        }
        return self.request_util.send_request("post", self.login_submit_url, data=payload)
