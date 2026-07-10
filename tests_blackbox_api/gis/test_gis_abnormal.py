# -*- coding: utf-8 -*-
"""GIS 异常参数、损坏请求体与方法边界测试。"""
from __future__ import annotations

import allure
import pytest


class TestGisAbnormalContractsMore:
    """补充校验 GIS 数据路径接口对缺参和非法字段的保护行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证 GIS 异常参数测试在已登录状态下进行。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_missing_type_prompt(body: dict):
        """断言 GIS 二维数据路径接口继续返回当前缺参提示。"""
        assert body["status"] == 0
        assert body["message"] == "请传地图类型参数！"
        assert body["data"] is None

    @allure.title("GIS 二维数据路径接口在空请求体下返回缺参提示")
    def test_gis_d2_data_path_empty_payload_returns_missing_type_prompt(self, auth_api, gis_api, test_user):
        """校验 GIS 二维数据路径接口在未传参数时返回明确的业务提示。"""
        self._login(auth_api, test_user)

        body = gis_api.get_d2_data_path().json()
        self._assert_missing_type_prompt(body)

    @allure.title("GIS 二维数据路径接口在传错字段名时返回缺参提示")
    def test_gis_d2_data_path_wrong_field_name_returns_missing_type_prompt(self, auth_api, gis_api, test_user):
        """校验即便传入 type 或 typeCode 等错误字段名，后端仍按缺参处理。"""
        self._login(auth_api, test_user)

        wrong_type_body = gis_api.get_d2_data_path({"type": "2d"}).json()
        wrong_type_code_body = gis_api.get_d2_data_path({"typeCode": "2d"}).json()

        self._assert_missing_type_prompt(wrong_type_body)
        self._assert_missing_type_prompt(wrong_type_code_body)


class TestGisMalformedPayloadContractsMore:
    """校验二维地图路径接口收到损坏 JSON 时的参数保护行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求进入 GIS 业务处理。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("二维地图路径接口收到损坏 JSON 时返回缺少地图类型提示")
    def test_d2_data_path_malformed_json_returns_missing_type_prompt(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 被视为缺少参数，接口返回可识别的业务提示。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["gis"]["d2_data_path_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == {
            "status": 0,
            "message": "请传地图类型参数！",
            "data": None,
        }


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


class TestGisOptionsContractsMore:
    """校验二维、三维地图属性和全局配置接口的预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入 GIS 路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("d2_data_path_url", "二维地图路径", id="d2-data-path"),
            pytest.param("d2_map_prop_url", "二维地图属性", id="d2-map-prop"),
            pytest.param("d3_map_prop_url", "三维地图属性", id="d3-map-prop"),
            pytest.param("d3_gis_config_url", "三维地图配置", id="d3-config"),
        ],
    )
    @allure.title("GIS 接口使用 OPTIONS 时返回空成功响应")
    def test_gis_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验 GIS 预检请求不会返回地图路径或配置业务数据。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["gis"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""
