# -*- coding: utf-8 -*-
"""AMCS 登录接口测试。

这一组用例先覆盖最基础的认证链路，后续其他模块接口都依赖它稳定可用。
"""
from __future__ import annotations

import allure


@allure.feature("认证")
class TestAuthLogin:
    """登录相关 smoke 用例。"""

    @allure.title("AMCS 登录成功")
    def test_login_success(self, auth_api, test_user):
        """校验正确账号密码可以成功登录。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "登录成功"
        assert body["data"] == "/"

    @allure.title("AMCS 错误密码登录失败")
    def test_login_fail_with_wrong_password(self, auth_api, test_user):
        """校验错误密码不会误判成登录成功。"""
        response = auth_api.login(
            account=test_user["username"],
            password=f"{test_user['password']}_bad",
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] != 0
        assert "成功" not in body["message"]

    @allure.title("AMCS 登录页可提取 CSRFToken")
    def test_login_page_contains_csrf_token(self, auth_api):
        """校验登录页确实包含后续登录必需的 CSRFToken。"""
        response = auth_api.get_login_page()

        assert response.status_code == 200
        csrf_token = auth_api.extract_csrf_token(response.text)
        assert csrf_token
