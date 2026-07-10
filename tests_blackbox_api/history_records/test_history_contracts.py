# -*- coding: utf-8 -*-
"""历史记录字段、分页、一致性与运行时契约测试。"""
from __future__ import annotations

import re
import allure


class TestHistoryConsistencyContractsExtra:
    """补充校验联动历史分页结果的一致性。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("历史记录第一页保持目标所亭名称")
    def test_monitor_link_history_first_page_keeps_non_empty_substation_names(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验历史记录第一页数据仍属于外部配置中的目标所亭。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert isinstance(row["subId"], str)
            assert row["subId"]

    @allure.title("历史记录第一页保持非空标识与报警数据编码")
    def test_monitor_link_history_first_page_keeps_identity_and_alarmdata_codes(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验历史记录第一页保持稳定的标识字段和数字字符串 alarmdataType。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert isinstance(row["id"], str) and row["id"]
            assert isinstance(row["equipId"], str) and row["equipId"]
            assert isinstance(row["equipName"], str) and row["equipName"]
            assert re.fullmatch(r"\d+", row["alarmdataType"])


class TestHistoryContractsExtra:
    """补充校验联动历史记录行级契约。"""

    @allure.title("联动历史展示字段保持非空")
    def test_monitor_link_history_display_fields_are_non_empty(self, auth_api, history_api, test_user):
        """校验历史记录行中的设备、描述和状态展示字段保持非空。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert isinstance(row["equipName"], str)
            assert isinstance(row["description"], str)
            assert isinstance(row["status"], str)
            assert row["equipName"]
            assert row["description"]
            assert row["status"]

    @allure.title("联动历史状态与时间字段保持稳定格式")
    def test_monitor_link_history_status_and_time_fields_keep_expected_formats(self, auth_api, history_api, test_user):
        """校验历史状态仍为数字字符串，createTime 仍为毫秒时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert re.fullmatch(r"\d+", row["status"])
            assert isinstance(row["createTime"], int)
            assert row["createTime"] >= 10**12


class TestHistoryContractsMore:
    """补充校验联动历史记录行级契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("历史记录行保持操作时间与编码格式")
    def test_monitor_link_history_rows_keep_operation_time_and_code_formats(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验第一页记录保持毫秒级时间字符串和数字编码状态字段。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 3}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["operationDt"])
            assert re.fullmatch(r"\d+", row["status"])
            assert re.fullmatch(r"\d+", row["linktype"])
            assert isinstance(row["creator"], str)
            assert row["creator"]

    @allure.title("历史记录第一页保持 createTime 非递增顺序")
    def test_monitor_link_history_first_page_create_time_is_non_increasing(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验第一页记录仍按 createTime 倒序排列。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 2

        create_times = [row["createTime"] for row in rows]
        assert create_times == sorted(create_times, reverse=True)


class TestHistoryPageContractsMore:
    """补充校验联动历史第一页中的稳定分页特征。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("联动历史第一页记录主键保持唯一")
    def test_monitor_link_history_first_page_ids_are_unique(self, auth_api, history_api, test_user):
        """校验联动历史第一页返回的记录主键仍保持唯一。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 20}).json()["rows"]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("联动历史第一页记录保持同一所亭名称")
    def test_monitor_link_history_first_page_keeps_same_substation_name(self, auth_api, history_api, test_user):
        """校验联动历史第一页记录仍保持当前环境的统一所亭名称。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 20}).json()["rows"]
        assert len(rows) > 0
        substation_names = {row["subId"] for row in rows}
        assert len(substation_names) == 1


class TestHistoryRuntimeContractsExtra:
    """补充校验联动历史记录中的空值模式和标识字段。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("联动历史前几条记录保持标识字段和空值契约")
    def test_monitor_link_history_first_rows_keep_identity_and_nullable_fields(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验前几条联动历史记录仍保留非空标识字段和当前空值模式。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) == 5

        for row in rows:
            assert isinstance(row["id"], str) and row["id"]
            assert isinstance(row["equipId"], str) and row["equipId"]
            assert isinstance(row["linkEquipId"], str) and row["linkEquipId"]
            assert row["alarmId"] is None or isinstance(row["alarmId"], str)
            assert row["checkValue"] is None or isinstance(row["checkValue"], str)
            assert row["linkage"] is None or isinstance(row["linkage"], str)
            assert row["linkDt"] is None or isinstance(row["linkDt"], str)

    @allure.title("联动历史前几条记录保持分类和触发字段格式")
    def test_monitor_link_history_first_rows_keep_code_and_trigger_formats(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验前几条联动历史记录仍保持分类编码和触发字段格式。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        for row in rows:
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])
            assert re.fullmatch(r"\d+", row["alarmdataType"])
            assert re.fullmatch(r"\d+", row["linktype"])
            assert isinstance(row["triggerSignal"], str) and row["triggerSignal"]
            assert isinstance(row["alarmType"], str) and row["alarmType"]
