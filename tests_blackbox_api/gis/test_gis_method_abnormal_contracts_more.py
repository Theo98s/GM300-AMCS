# -*- coding: utf-8 -*-
"""GIS 接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisMethodAbnormalContractsMore:
    """补充 GIS 接口对错误方法和错误请求体的兼容行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证 GIS 接口处于可访问状态。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_missing_type_prompt(response):
        """统一校验二维数据路径接口缺少地图类型时的业务提示。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "请传地图类型参数！"
        assert body["data"] is None

    @staticmethod
    def _assert_map_prop_success(response, expected_type_code: str):
        """统一校验地图属性接口仍返回指定类型配置。"""
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据修改成功!"
        assert body["data"]["typeCode"] == expected_type_code

    @allure.title("GIS 二维数据路径接口使用 GET 方法时返回缺参提示")
    def test_gis_d2_data_path_get_method_returns_missing_type_prompt(self, auth_api, request_util, config, test_user):
        """校验二维数据路径接口即使使用 GET，也保持缺少地图类型的业务提示。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["gis"]["d2_data_path_url"])

        self._assert_missing_type_prompt(response)

    @allure.title("GIS 二维数据路径接口接收文本请求体时返回缺参提示")
    def test_gis_d2_data_path_plain_text_body_returns_missing_type_prompt(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误文本请求体不会导致 GIS 二维路径接口返回 500。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["gis"]["d2_data_path_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_missing_type_prompt(response)

    @allure.title("GIS 二维地图属性接口使用 POST 方法时仍返回二维配置")
    def test_gis_d2_map_prop_post_method_keeps_config_response(self, auth_api, request_util, config, test_user):
        """校验二维地图属性接口兼容 POST 方法，并保持二维类型配置。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["gis"]["d2_map_prop_url"])

        self._assert_map_prop_success(response, "2d")

    @allure.title("GIS 三维地图属性接口使用 POST 方法时仍返回三维配置")
    def test_gis_d3_map_prop_post_method_keeps_config_response(self, auth_api, request_util, config, test_user):
        """校验三维地图属性接口兼容 POST 方法，并保持三维类型配置。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["gis"]["d3_map_prop_url"])

        self._assert_map_prop_success(response, "3d")

    @allure.title("GIS 全局配置接口使用 GET 方法时仍返回配置")
    def test_gis_config_get_method_keeps_config_response(self, auth_api, request_util, config, test_user):
        """校验 GIS 全局配置接口兼容 GET 方法，仍返回配置项集合。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["gis"]["d3_gis_config_url"])

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"].keys()) >= {"gisEnable", "gisD3PatrolEnable", "d3View", "d3Theme"}
