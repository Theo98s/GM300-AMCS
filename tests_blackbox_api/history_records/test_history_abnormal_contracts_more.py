# -*- coding: utf-8 -*-
"""AMCS 历史记录异常场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
class TestHistoryAbnormalContractsMore:
    """补充校验历史分页接口对异常 rows 和 page 参数的保护行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证后续异常分页请求使用有效会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("历史分页 rows 传入文本时返回 400 转换错误")
    def test_history_rows_text_value_returns_http_400_with_conversion_error(self, auth_api, history_api, test_user):
        """校验 rows 传入非整数字符串时，后端返回 400 而不是成功 JSON。"""
        self._login(auth_api, test_user)

        response = history_api.find_monitor_link_history({"rows": "bad"})
        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert 'input string: "bad"' in response.text.lower()

    @allure.title("历史分页 rows 为 0 时回退到默认首页")
    def test_history_rows_zero_falls_back_to_default_first_page(self, auth_api, history_api, test_user):
        """校验 rows=0 不会报错，而是回退到默认分页大小和默认首页结果。"""
        self._login(auth_api, test_user)

        default_body = history_api.find_monitor_link_history().json()
        zero_body = history_api.find_monitor_link_history({"rows": 0}).json()

        assert zero_body["total"] == default_body["total"]
        assert len(zero_body["rows"]) == len(default_body["rows"]) == 10
        assert zero_body["rows"][0]["id"] == default_body["rows"][0]["id"]

    @allure.title("历史分页 rows 为负数时回退到默认首页")
    def test_history_negative_rows_falls_back_to_default_first_page(self, auth_api, history_api, test_user):
        """校验 rows=-1 不会报错，而是回退到默认分页大小和默认首页结果。"""
        self._login(auth_api, test_user)

        default_body = history_api.find_monitor_link_history().json()
        negative_body = history_api.find_monitor_link_history({"rows": -1}).json()

        assert negative_body["total"] == default_body["total"]
        assert len(negative_body["rows"]) == len(default_body["rows"]) == 10
        assert negative_body["rows"][0]["id"] == default_body["rows"][0]["id"]
