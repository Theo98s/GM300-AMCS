# -*- coding: utf-8 -*-
"""Additional AMCS system public-interface contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemLogoContracts:
    """Extra contract checks for public system endpoints."""

    @allure.title("系统 logo 公共接口返回标准成功消息")
    def test_sys_logo_public_message_is_success_text(self, system_api):
        """Verify the public logo endpoint keeps the standard success message text."""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"

