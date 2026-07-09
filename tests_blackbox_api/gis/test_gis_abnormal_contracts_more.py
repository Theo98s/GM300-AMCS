# -*- coding: utf-8 -*-
"""AMCS GIS 异常场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
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
