# -*- coding: utf-8 -*-
"""历史趋势接口基础查询测试。"""
from __future__ import annotations

import json

import allure
import pytest


@allure.feature("历史趋势")
class TestHistoryTrendApi:
    """覆盖趋势首页、设备树、监控属性、条件和趋势页面。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保访问历史趋势业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _flatten(nodes):
        """递归展开设备树节点。"""
        for node in nodes:
            yield node
            yield from TestHistoryTrendApi._flatten(node.get("children") or [])

    @classmethod
    def _first_equipment_with_attribute(cls, history_trend_api):
        """获取第一台具有遥测趋势属性的设备。"""
        tree = history_trend_api.get_tree().json()["data"]
        for node in cls._flatten(tree):
            if node.get("type") != "equip":
                continue
            attributes = history_trend_api.list_attributes(node["id"]).json()["data"]
            if attributes:
                return node, attributes
        pytest.skip("当前环境没有可查询历史趋势的设备属性。")

    @allure.title("历史趋势首页包含设备树和趋势页面入口")
    def test_history_trend_index_page(self, auth_api, history_trend_api, test_user):
        """校验首页标题、设备树和设备趋势页面地址均存在。"""
        self._login(auth_api, test_user)

        response = history_trend_api.get_index_page()

        assert response.status_code == 200
        assert "<title>历史趋势</title>" in response.text
        assert "/amcs/trend/getTree" in response.text
        assert "/amcs/trend/historicalTrend" in response.text

    @allure.title("历史趋势设备树返回标准业务包装")
    def test_history_trend_tree_contract(self, auth_api, history_trend_api, test_user):
        """校验设备树返回成功状态和非空节点列表。"""
        self._login(auth_api, test_user)

        body = history_trend_api.get_tree().json()

        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert isinstance(body["data"], list) and body["data"]

    @allure.title("历史趋势设备树保持类型与设备两级结构")
    def test_history_trend_tree_node_shape(self, auth_api, history_trend_api, test_user):
        """校验根节点为设备类型，子节点为具体设备。"""
        self._login(auth_api, test_user)

        root = history_trend_api.get_tree().json()["data"][0]

        assert set(root) >= {"id", "text", "name", "state", "type", "children"}
        assert root["type"] == "equipType"
        assert isinstance(root["children"], list)
        if root["children"]:
            assert root["children"][0]["type"] == "equip"
            assert root["children"][0]["pid"] == root["id"]

    @allure.title("设备历史趋势页面包含属性和数据查询接口")
    def test_history_trend_equipment_page(self, auth_api, history_trend_api, test_user):
        """校验设备趋势页面正确写入设备标识和两个数据接口。"""
        self._login(auth_api, test_user)
        equipment, _ = self._first_equipment_with_attribute(history_trend_api)

        response = history_trend_api.get_trend_page(equipment["id"], equipment["text"])

        assert response.status_code == 200
        assert "<title>历史趋势</title>" in response.text
        assert equipment["id"] in response.text
        assert "/amcs/trend/ycDataTypeAttrConditionAndData" in response.text
        assert "/amcs/trend/onlineMonitorData" in response.text

    @allure.title("历史趋势设备属性返回标准成功列表")
    def test_history_trend_attribute_list(self, auth_api, history_trend_api, test_user):
        """校验属性行包含设备、监控点、数据类型和属性名称。"""
        self._login(auth_api, test_user)
        equipment, attributes = self._first_equipment_with_attribute(history_trend_api)

        first = attributes[0]
        assert set(first) >= {"equipId", "equipName", "alarmTypeId", "alarmClass", "yc", "attr"}
        assert first["equipId"] == equipment["id"]
        assert first["equipName"] == equipment["text"]

    @allure.title("历史趋势遥测属性配置保持可解析 JSON")
    def test_history_trend_attribute_yc_is_parseable(self, auth_api, history_trend_api, test_user):
        """校验遥测格式和单位配置可被趋势页面解析。"""
        self._login(auth_api, test_user)
        _, attributes = self._first_equipment_with_attribute(history_trend_api)

        yc = json.loads(attributes[0]["yc"])

        assert set(yc) >= {"FORMAT", "UNIT_NAME"}
        assert isinstance(yc["FORMAT"], str)

    @allure.title("历史趋势设备对比页面可正常打开")
    def test_history_trend_compare_equipment_page(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """校验已有设备可进入对比设备选择页面。"""
        self._login(auth_api, test_user)
        equipment, _ = self._first_equipment_with_attribute(history_trend_api)

        response = history_trend_api.get_compare_equipment_page(equipment["id"])

        assert response.status_code == 200
        assert "<title>选择对比设备</title>" in response.text

    @allure.title("历史趋势越限条件接口返回标准成功包装")
    def test_history_trend_condition_list(self, auth_api, history_trend_api, test_user):
        """校验监控属性即使未配置越限条件也返回列表结构。"""
        self._login(auth_api, test_user)
        _, attributes = self._first_equipment_with_attribute(history_trend_api)

        body = history_trend_api.list_conditions(attributes[0]["alarmTypeId"]).json()

        assert body["status"] == 0
        assert body["message"] == "操作成功!"
        assert isinstance(body["data"], list)
