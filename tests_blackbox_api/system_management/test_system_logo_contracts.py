# -*- coding: utf-8 -*-
"""AMCS 系统公共接口补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemLogoContracts:
    """补充校验系统公共接口契约。"""

    @allure.title("系统 logo 公共接口返回标准成功消息")
    def test_sys_logo_public_message_is_success_text(self, system_api):
        """校验公共 logo 接口保持标准成功提示文案。"""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
