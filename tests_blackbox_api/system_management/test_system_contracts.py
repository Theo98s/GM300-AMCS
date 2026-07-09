# -*- coding: utf-8 -*-
"""AMCS 系统接口契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemContracts:
    """校验公共接口与登录保护接口的系统契约。"""

    @allure.title("系统 logo 公共接口返回标准 Result 结构")
    def test_sys_logo_public_contract(self, system_api):
        """校验公共 logo 接口保持标准 Result 返回结构。"""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert set(body.keys()) >= {"status", "message", "data"}
        assert body["status"] == 0
        assert isinstance(body["message"], str)
        assert isinstance(body["data"], dict)
        assert set(body["data"].keys()) >= {"sys_logo_a", "sys_logo_b"}

    @allure.title("时间戳接口未登录时跳转登录页")
    def test_timestamp_requires_login(self, system_api):
        """校验未登录时，时间戳接口受登录保护。"""
        response = system_api.get_timestamp()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("实时报警数量接口未登录时跳转登录页")
    def test_alarm_count_requires_login_contract(self, system_api):
        """校验未登录时，告警数量接口受登录保护。"""
        response = system_api.get_alarm_count()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("健康检查公共接口返回列表结构")
    def test_health_check_public_contract(self, system_api):
        """校验健康检查接口保持公共可访问，并返回列表载荷。"""
        response = system_api.get_health()
        assert response.status_code == 200

        body = response.json()
        assert set(body.keys()) >= {"status", "message", "data"}
        assert body["status"] == 0
        assert isinstance(body["message"], str)
        assert isinstance(body["data"], list)
        if body["data"]:
            assert set(body["data"][0].keys()) >= {"name", "serviceUp", "deviceList"}

    @allure.title("系统 logo 公共接口返回字符串类型字段")
    def test_sys_logo_public_data_uses_string_fields(self, system_api):
        """校验 logo 字段即使为空，也仍保持字符串类型。"""
        response = system_api.get_sys_logo()
        body = response.json()

        assert isinstance(body["data"]["sys_logo_a"], str)
        assert isinstance(body["data"]["sys_logo_b"], str)

    @allure.title("健康检查首项服务结构包含设备列表布尔状态")
    def test_health_check_first_service_contains_device_list_and_flag(self, system_api):
        """校验首个健康检查服务项保持布尔服务标记和列表载荷。"""
        response = system_api.get_health()
        body = response.json()

        if not body["data"]:
            return

        first_service = body["data"][0]
        assert isinstance(first_service["serviceUp"], bool)
        assert isinstance(first_service["deviceList"], list)
        assert first_service["name"]

    @allure.title("健康检查所有服务项使用统一字段结构")
    def test_health_check_all_services_share_same_keys(self, system_api):
        """校验每条健康检查服务记录都保持相同的字段结构。"""
        response = system_api.get_health()
        body = response.json()

        if not body["data"]:
            return

        expected_keys = set(body["data"][0].keys())
        for item in body["data"]:
            assert set(item.keys()) == expected_keys
            assert isinstance(item["serviceUp"], bool)

    @allure.title("健康检查服务名称非空且不重复")
    def test_health_check_service_names_are_non_empty_and_unique(self, system_api):
        """校验健康检查服务名称在返回列表中保持非空且唯一。"""
        response = system_api.get_health()
        body = response.json()

        names = [item["name"] for item in body["data"]]
        assert all(names)
        assert len(names) == len(set(names))

    @allure.title("健康检查包含核心摄像机和流媒体服务")
    def test_health_check_contains_expected_core_services(self, system_api):
        """校验健康检查列表仍暴露核心摄像机和流媒体服务名称。"""
        response = system_api.get_health()
        body = response.json()

        names = {item["name"] for item in body["data"]}
        assert "cameras" in names
        assert "流媒体服务" in names
