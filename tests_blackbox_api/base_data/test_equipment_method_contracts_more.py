# -*- coding: utf-8 -*-
"""基础数据设备管理接口方法兼容契约测试。"""
from __future__ import annotations

import allure


@allure.feature("设备管理")
class TestEquipmentMethodContractsMore:
    """校验首页、分页和类型树接口使用其他方法时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求进入设备管理路由。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("设备列表使用 GET 时仍返回分页数据")
    def test_equipment_page_get_keeps_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备列表兼容 GET 并遵守分页大小。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["equipment"]["page_url"],
            params={"page": 1, "rows": 2},
        )

        body = response.json()
        assert response.status_code == 200
        assert isinstance(body["total"], int)
        assert len(body["rows"]) <= 2

    @allure.title("设备列表使用 OPTIONS 时返回空成功响应")
    def test_equipment_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备分页预检请求不会执行查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("options", config["equipment"]["page_url"])

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("设备类型树使用 POST 时仍返回节点列表")
    def test_equipment_type_tree_post_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备类型树兼容 POST 并保持层级节点响应。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["equipment"]["type_tree_url"])

        assert response.status_code == 200
        assert isinstance(response.json(), list)
