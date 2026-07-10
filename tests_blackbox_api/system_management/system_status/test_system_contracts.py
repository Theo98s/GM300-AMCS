# -*- coding: utf-8 -*-
"""系统公共接口与健康状态数据结构契约测试。"""
from __future__ import annotations

import allure
import re

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

class TestHealthCameraRuntimeContractsMore:
    """补充校验健康检查中摄像机设备明细的稳定字段。"""

    @staticmethod
    def _camera_rows(system_api) -> list[dict]:
        """返回健康检查中的 cameras 明细列表。"""
        rows = system_api.get_health().json()["data"]
        cameras = next(row for row in rows if row["name"] == "cameras")
        assert isinstance(cameras["deviceList"], list)
        return cameras["deviceList"]

    @allure.title("健康检查 cameras 前十条记录保持实时视频设备契约")
    def test_health_camera_rows_keep_live_video_contract(self, system_api):
        """校验前十条摄像机记录仍保持在线视频设备的字段模式。"""
        rows = self._camera_rows(system_api)
        assert len(rows) >= 10

        for row in rows[:10]:
            assert isinstance(row["name"], str) and row["name"]
            assert row["serviceUp"] is True
            assert row["value"] == "1"
            assert row["signalTypeCode"] == "3"
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["desc"] == ""
            assert row.get("alarmClass") is None

    @allure.title("健康检查 cameras 前十条记录保持区域和视频厂家字段")
    def test_health_camera_rows_keep_area_and_nvr_fields(self, system_api):
        """校验前十条摄像机记录仍保留区域编码和视频厂家字段。"""
        rows = self._camera_rows(system_api)
        assert len(rows) >= 10

        for row in rows[:10]:
            assert row["areaCode"] == "00"
            assert row["areaName"] is None
            assert isinstance(row["customCode"], str) and row["customCode"].startswith("GM300_CAMS_")
            assert row["nvr"] in {"DH", "HIK"}
            assert row["parentName"] is None

class TestHealthContractsMore:
    """补充校验健康检查服务组成。"""

    @allure.title("健康检查服务名集合保持稳定")
    def test_health_check_service_name_set_is_stable(self, system_api):
        """校验当前环境仍暴露预期的六个健康检查服务名称。"""
        body = system_api.get_health().json()
        names = {item["name"] for item in body["data"]}
        assert names == {
            "移动巡检设备",
            "cameras",
            "局级主站",
            "段级主站",
            "流媒体服务",
            "device",
        }

    @allure.title("健康检查不同服务的 deviceList 可空模式保持稳定")
    def test_health_check_device_list_nullability_pattern_is_stable(self, system_api):
        """校验列表型和空值型服务仍保持当前 deviceList 可空模式。"""
        body = system_api.get_health().json()["data"]
        service_map = {item["name"]: item["deviceList"] for item in body}

        assert isinstance(service_map["移动巡检设备"], list)
        assert isinstance(service_map["cameras"], list)
        assert isinstance(service_map["device"], list)
        assert service_map["局级主站"] is None
        assert service_map["段级主站"] is None
        assert service_map["流媒体服务"] is None

class TestHealthDeviceContractsExtra:
    """补充校验健康检查返回中嵌套设备行的契约。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查条目，便于针对嵌套记录做断言。"""
        body = system_api.get_health().json()["data"]
        return {item["name"]: item for item in body}

    @allure.title("健康检查 cameras 列表保留稳定的嵌套设备行契约")
    def test_health_camera_device_rows_keep_expected_nested_contracts(self, system_api):
        """校验摄像机设备行保持稳定的标记、编码和 IP 字段契约。"""
        cameras = self._health_map(system_api)["cameras"]
        assert isinstance(cameras["deviceList"], list)
        assert len(cameras["deviceList"]) > 0

        for row in cameras["deviceList"][:5]:
            assert isinstance(row["name"], str) and row["name"]
            assert isinstance(row["serviceUp"], bool)
            assert row["value"] in {"1", "异常"}
            assert re.fullmatch(r"\d+", row["signalTypeCode"])
            assert row["ip"] is None or re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["customCode"] is None or isinstance(row["customCode"], str)

    @allure.title("健康检查 device 列表保留预期的 NVR 与通信设备契约")
    def test_health_device_group_keeps_expected_device_row_contracts(self, system_api):
        """校验 device 健康分组仍保留基于 IP 的 NVR 和通信设备记录。"""
        device_group = self._health_map(system_api)["device"]
        assert isinstance(device_group["deviceList"], list)
        assert len(device_group["deviceList"]) >= 4

        names = [row["name"] for row in device_group["deviceList"]]
        assert "NVR" in names
        assert "通信管理机" in names
        for row in device_group["deviceList"]:
            assert isinstance(row["serviceUp"], bool)
            assert row["value"] in {"1", "异常"}
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["signalTypeCode"] is None or re.fullmatch(r"\d+", row["signalTypeCode"])

class TestHealthOrderContracts:
    """补充校验健康检查服务顺序。"""

    @allure.title("健康检查服务顺序保持稳定")
    def test_health_check_service_order_is_stable(self, system_api):
        """校验当前健康检查服务顺序保持稳定，避免影响首页看板渲染。"""
        body = system_api.get_health().json()["data"]
        names = [item["name"] for item in body]
        assert names == [
            "移动巡检设备",
            "cameras",
            "局级主站",
            "段级主站",
            "流媒体服务",
            "device",
        ]

class TestHealthRuntimeStatusContractsMore:
    """补充校验健康检查各服务当前运行状态模式。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查服务，便于逐项断言。"""
        rows = system_api.get_health().json()["data"]
        return {row["name"]: row for row in rows}

    @allure.title("健康检查各服务保持当前 serviceUp 分布模式")
    def test_health_check_keeps_current_service_up_pattern(self, system_api):
        """校验当前环境各服务仍保持稳定的 serviceUp 分布模式。"""
        health_map = self._health_map(system_api)

        assert health_map["移动巡检设备"]["serviceUp"] is True
        assert health_map["cameras"]["serviceUp"] is False
        assert health_map["局级主站"]["serviceUp"] is True
        assert health_map["段级主站"]["serviceUp"] is True
        assert health_map["流媒体服务"]["serviceUp"] is True
        assert health_map["device"]["serviceUp"] is False

    @allure.title("健康检查顶层服务保持空 signalTypeCode 模式")
    def test_health_check_top_level_services_keep_null_signal_type_code(self, system_api):
        """校验健康检查顶层服务仍统一保持空 signalTypeCode。"""
        health_map = self._health_map(system_api)

        for row in health_map.values():
            assert row["signalTypeCode"] is None

class TestHealthTopologyContractsExtra:
    """补充校验健康检查分组类型、主机信息和设备行默认值。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查分组，便于分别断言不同服务类型。"""
        rows = system_api.get_health().json()["data"]
        return {row["name"]: row for row in rows}

    @allure.title("健康检查主机型服务保持非空 IP 和类型字段")
    def test_health_host_services_keep_ip_and_type_fields(self, system_api):
        """校验主机型服务仍使用非空 IP 和明确类型字段。"""
        health_map = self._health_map(system_api)

        for service_name in ("局级主站", "段级主站", "流媒体服务"):
            row = health_map[service_name]
            assert row["deviceList"] is None
            assert isinstance(row["type"], str) and row["type"]
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert isinstance(row["serviceUp"], bool)

    @allure.title("健康检查列表型服务保持空主机信息字段")
    def test_health_list_services_keep_null_host_fields(self, system_api):
        """校验列表型服务仍把 IP 和类型放空，并通过 deviceList 承载明细。"""
        health_map = self._health_map(system_api)

        for service_name in ("移动巡检设备", "cameras", "device"):
            row = health_map[service_name]
            assert row["type"] is None
            assert row["ip"] is None
            assert isinstance(row["deviceList"], list)
            assert isinstance(row["serviceUp"], bool)

    @allure.title("健康检查 device 分组前几条记录保持网关类默认空业务字段")
    def test_health_device_group_rows_keep_null_business_fields(self, system_api):
        """校验 device 分组前几条记录仍保持空业务编码字段和合法 IP 格式。"""
        device_rows = self._health_map(system_api)["device"]["deviceList"]
        assert len(device_rows) > 0

        for row in device_rows[:4]:
            assert isinstance(row["name"], str) and row["name"]
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["customCode"] is None
            assert row["areaCode"] is None
            assert row["areaName"] is None
            assert row["nvr"] is None
