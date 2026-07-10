# -*- coding: utf-8 -*-
"""巡检点位管理接口方法兼容契约测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检点位管理")
class TestPatrolPointMethodContractsMore:
    """校验首页、分页、设备和预置位接口使用非默认方法时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求进入巡检点位路由。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("巡检点位首页使用 POST 时仍返回完整页面")
    def test_patrol_point_index_post_keeps_html_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验首页兼容 POST 访问并保留列表初始化脚本。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["patrol_point"]["index_url"])

        assert response.status_code == 200
        assert "<title>巡检点位管理</title>" in response.text
        assert "/amcs/monitorArea/findPage" in response.text

    @allure.title("巡检点位分页接口使用 OPTIONS 时返回空成功响应")
    def test_patrol_point_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验分页预检请求不会执行查询或返回业务数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("options", config["patrol_point"]["page_url"])

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("巡检点位设备接口使用 POST 时仍返回设备列表")
    def test_patrol_point_equipment_post_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备级联接口兼容 POST 并保持列表响应。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["patrol_point"]["equip_list_url"])

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @allure.title("已用预置位接口使用 POST 且设备无效时返回空列表")
    def test_patrol_point_existing_preset_post_unknown_returns_empty(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验预置位级联接口兼容 POST，且无效设备不会命中数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_point"]["existing_preset_url"],
            data={"equipId": "NO_SUCH_EQUIP_ID"},
        )

        assert response.status_code == 200
        assert response.json() == {"status": 0, "message": "", "data": []}
