# -*- coding: utf-8 -*-
"""历史趋势跨接口功能流程测试。"""
from __future__ import annotations

import time

import allure
import pytest


@allure.feature("历史趋势")
class TestHistoryTrendFunctional:
    """覆盖设备树、监控属性、时序数据和缩放增量查询链路。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保功能链路复用同一权限。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _flatten(nodes):
        """递归展开设备树节点。"""
        for node in nodes:
            yield node
            yield from TestHistoryTrendFunctional._flatten(node.get("children") or [])

    @classmethod
    def _sample(cls, history_trend_api):
        """获取具有趋势属性的设备和首个属性。"""
        tree = history_trend_api.get_tree().json()["data"]
        for equipment in cls._flatten(tree):
            if equipment.get("type") != "equip":
                continue
            attributes = history_trend_api.list_attributes(equipment["id"]).json()["data"]
            if attributes:
                return equipment, attributes[0]
        pytest.skip("当前环境没有可查询历史趋势的设备属性。")

    @allure.title("设备树与趋势属性保持设备身份一致")
    def test_history_trend_tree_to_attribute_consistency(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """校验设备树选中设备与属性接口返回的设备标识和名称一致。"""
        self._login(auth_api, test_user)
        equipment, attribute = self._sample(history_trend_api)

        assert attribute["equipId"] == equipment["id"]
        assert attribute["equipName"] == equipment["text"]

    @allure.title("最近一小时趋势查询返回数据类型和数据列表")
    def test_history_trend_last_hour_data_contract(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """以首个监控属性查询最近一小时，并校验时序数据包装。"""
        self._login(auth_api, test_user)
        equipment, attribute = self._sample(history_trend_api)
        end_time = int(time.time() * 1000)

        body = history_trend_api.query_condition_data(
            {
                "alarmTypeId": attribute["alarmTypeId"],
                "startTime": end_time - 3_600_000,
                "endTime": end_time,
                "timeInterval": "1m",
            }
        ).json()

        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert isinstance(body["data"]["data"], list)
        assert isinstance(body["data"]["attrList"], list)
        data_type = body["data"]["dataType"]
        assert data_type["monitorId"] == attribute["alarmTypeId"]
        assert data_type["equipId"] == equipment["id"]
        assert data_type["attrName"] == attribute["attr"]

    @allure.title("最近一天趋势查询保持时间点升序")
    def test_history_trend_last_day_data_is_time_ordered(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """查询最近一天趋势，有数据时校验时间戳按升序排列。"""
        self._login(auth_api, test_user)
        _, attribute = self._sample(history_trend_api)
        end_time = int(time.time() * 1000)

        rows = history_trend_api.query_condition_data(
            {
                "alarmTypeId": attribute["alarmTypeId"],
                "startTime": end_time - 86_400_000,
                "endTime": end_time,
                "timeInterval": "10m",
            }
        ).json()["data"]["data"]

        times = [item["time"] for item in rows]
        assert times == sorted(times)

    @allure.title("趋势图缩放后可查询增量监控数据")
    def test_history_trend_online_zoom_data_contract(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """按设备名称和属性查询最近一小时增量数据，并校验列表响应。"""
        self._login(auth_api, test_user)
        equipment, attribute = self._sample(history_trend_api)
        end_time = int(time.time() * 1000)

        body = history_trend_api.query_online_data(
            {
                "subName": "青花牵引变电所",
                "equipName": equipment["text"],
                "attrName": attribute["attr"],
                "startTime": end_time - 3_600_000,
                "endTime": end_time,
                "timeInterval": "1m",
            }
        ).json()

        assert body["status"] == 0
        assert body["message"] == "操作成功!"
        assert isinstance(body["data"], list)

    @allure.title("历史趋势设备树所有节点标识在同类型内唯一")
    def test_history_trend_tree_ids_are_unique_by_type(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """校验设备类型和设备节点不会分别出现重复标识。"""
        self._login(auth_api, test_user)

        nodes = list(self._flatten(history_trend_api.get_tree().json()["data"]))
        for node_type in ("equipType", "equip"):
            ids = [node["id"] for node in nodes if node["type"] == node_type]
            assert len(ids) == len(set(ids))
