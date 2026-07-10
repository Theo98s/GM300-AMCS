# -*- coding: utf-8 -*-
"""巡检点位管理接口异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检点位管理")
class TestPatrolPointAbnormalContracts:
    """覆盖错误分页和删除前校验缺少请求体场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("巡检点位 rows 传入非整数时返回参数错误")
    def test_patrol_point_page_rejects_invalid_rows(self, auth_api, request_util, config, test_user):
        """校验错误分页大小不会触发服务端查询异常。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_point"]["page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("巡检点位 page 传入非整数时返回参数错误")
    def test_patrol_point_page_rejects_invalid_page(self, auth_api, request_util, config, test_user):
        """校验错误页码被明确拒绝并返回参数转换信息。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_point"]["page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("巡检点位删除前校验缺少请求体时返回 400")
    def test_patrol_point_can_delete_requires_body(self, auth_api, request_util, config, test_user):
        """校验空请求不会误进入删除依赖检查流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_point"]["can_delete_url"],
        )

        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "couldDelete" in response.text
