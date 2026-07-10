# -*- coding: utf-8 -*-
"""监控点查询及联动辅助接口的异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestMonitorQueryAbnormalContractsMore:
    """校验监控点查询接口在错误分页、缺参和方法切换时的实际响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保请求命中业务接口而非登录页。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_monitor_page(response):
        """统一校验监控点列表的分页结果结构。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert isinstance(body, dict)
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @allure.title("监控点列表的 rows 传入非整数时返回参数转换错误")
    def test_monitor_page_rejects_non_integer_rows(self, auth_api, request_util, config, test_user):
        """校验错误的 rows 参数被明确拒绝，避免服务端静默返回错误分页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert '"bad"' in response.text

    @allure.title("监控点列表的 page 传入非整数时返回参数转换错误")
    def test_monitor_page_rejects_non_integer_page(self, auth_api, request_util, config, test_user):
        """校验错误的 page 参数不会被解析为不可预期的页码。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert '"bad"' in response.text

    @allure.title("监控点列表使用 GET 访问时仍返回默认分页数据")
    def test_monitor_page_get_method_keeps_default_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录服务端对 GET 的兼容行为，防止路由改造造成前端列表不可用。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["database"]["monitor_page_url"])

        self._assert_monitor_page(response)

    @allure.title("联动关联设备接口使用 POST 访问时仍返回设备列表")
    def test_related_equip_list_post_method_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验关联设备只读接口对 POST 的兼容响应，列表结构保持稳定。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_related_equip_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("联动摄像机接口缺少设备参数时返回默认数据包装")
    def test_camera_list_without_equip_id_returns_default_data_wrapper(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少 equipId 时接口返回标准业务包装，而不是服务端异常。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_camera_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "成功"
        assert isinstance(body["data"], list)
        if body["data"]:
            assert set(body["data"][0]) >= {"equipId", "cameraName", "channelNo"}

    @allure.title("联动预置位接口缺少参数时返回空列表")
    def test_preset_list_without_query_params_returns_empty_list(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少摄像机和关联设备标识时预置位查询可安全退化为空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == []
