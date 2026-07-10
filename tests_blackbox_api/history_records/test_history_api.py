# -*- coding: utf-8 -*-
"""历史记录与历史趋势基础接口测试。"""
from __future__ import annotations

import allure
import json
import pytest


class TestHistoryApi:
    """联动历史查询 smoke 用例。"""

    @allure.title("联动历史分页接口返回总数与列表")
    def test_monitor_link_history_returns_total_and_rows(self, auth_api, history_api, test_user):
        """校验联动历史分页结构完整。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert body["total"] >= len(body["rows"])

    @allure.title("联动历史首条记录包含关键业务字段")
    def test_monitor_link_history_first_row_contains_expected_fields(self, auth_api, history_api, test_user, target_config):
        """校验联动历史记录包含站点、联动描述和状态等关键字段。

        历史记录会随环境业务数据变化，这里不再写死某个所亭名称；
        目标所亭只从外部配置读取并用于失败信息，方便定位当前测试环境。
        """
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history()
        body = response.json()
        assert len(body["rows"]) > 0

        first_row = body["rows"][0]
        assert set(first_row.keys()) >= {
            "subId",
            "equipName",
            "alarmType",
            "linkage",
            "description",
            "status",
        }
        assert first_row["subId"], f"联动历史记录应返回所属所亭；当前目标所亭：{target_config.get('substation_name', '')}"

    @allure.title("联动历史 rows 参数可限制返回条数")
    def test_monitor_link_history_respects_rows_parameter(self, auth_api, history_api, test_user):
        """校验联动历史分页接口会按 rows 参数限制返回记录数量。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        assert response.status_code == 200

        body = response.json()
        assert body["total"] >= 3
        assert len(body["rows"]) == 3

    @allure.title("联动历史首条记录包含主键与设备标识")
    def test_monitor_link_history_first_row_contains_identity_fields(self, auth_api, history_api, test_user):
        """校验联动历史首条记录包含主键、设备 ID 和联动时间等标识字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 1})
        body = response.json()
        assert len(body["rows"]) == 1

        first_row = body["rows"][0]
        assert first_row["id"]
        assert first_row["equipId"]
        assert first_row["createTime"]
        assert "linkDt" in first_row

    @allure.title("联动历史创建时间字段使用毫秒时间戳")
    def test_monitor_link_history_create_time_is_millisecond_timestamp(self, auth_api, history_api, test_user):
        """校验联动历史记录中的 createTime 字段使用正整数毫秒时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 1})
        body = response.json()
        assert len(body["rows"]) == 1

        create_time = body["rows"][0]["createTime"]
        assert isinstance(create_time, int)
        assert create_time > 0

    @allure.title("联动历史状态字段保持字符串类型")
    def test_monitor_link_history_status_uses_string_type(self, auth_api, history_api, test_user):
        """校验联动历史记录中的 status 字段保持字符串类型。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 2})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert isinstance(row["status"], str)

    @allure.title("历史记录可空联动字段保持允许的类型")
    def test_monitor_link_history_nullable_fields_keep_expected_types(self, auth_api, history_api, test_user):
        """校验可空联动字段仍允许为空，同时核心文本字段保持有值。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert isinstance(row["alarmType"], str)
            assert isinstance(row["description"], str)
            assert row["description"]
            assert row["linkage"] is None or isinstance(row["linkage"], str)
            assert row["linkDt"] is None or isinstance(row["linkDt"], str)


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
