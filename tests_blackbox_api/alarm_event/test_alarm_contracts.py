# -*- coding: utf-8 -*-
"""报警事件字段、显示、排序与运行时契约测试。"""
from __future__ import annotations

import re
import allure
import pytest


class TestAlarmContractsExtra:
    """补充校验报警记录列表返回结构。"""

    @allure.title("报警记录展示字段保持非空字符串")
    def test_alarm_record_display_fields_are_non_empty(self, auth_api, alarm_api, test_user):
        """校验报警列表中的设备名称和告警内容显示字段保持非空。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("Current environment has no alarm records.")

        for row in body[:3]:
            assert isinstance(row["equipName"], str)
            assert isinstance(row["warnContent"], str)
            assert row["equipName"]
            assert row["warnContent"]

    @allure.title("报警记录码值字段保持数字字符串格式")
    def test_alarm_record_code_fields_match_digit_patterns(self, auth_api, alarm_api, test_user):
        """校验报警编码字段保持前端期望的数字字符串格式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("Current environment has no alarm records.")

        for row in body[:3]:
            assert re.fullmatch(r"\d{2}", row["alarmLevel"])
            assert re.fullmatch(r"\d{2}", row["alarmSource"])
            assert re.fullmatch(r"\d+", row["status"])
            assert row["hasLink"] in {"0", "1"}
            assert row["isPatrol"] in {"0", "1"}


class TestAlarmContractsMore:
    """补充校验报警记录列表行级契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境无数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("Current environment has no alarm records.")
        return rows

    @allure.title("报警记录行保持 alarmDt 与 alarmDtStr 镜像字段")
    def test_alarm_record_time_fields_keep_mirrored_display_values(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录中的原始时间与展示时间字段保持一致。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["alarmDt"])
            assert row["alarmDtStr"] == row["alarmDt"]

    @allure.title("报警记录行保持稳定的编码与可空字段契约")
    def test_alarm_record_first_rows_keep_code_and_nullable_field_contracts(
        self,
        auth_api,
        alarm_api,
        test_user,
    ):
        """校验报警编码字段保持数字字符串，可空展示字段仍保持可空字符串契约。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert row["deleted"] == 0
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])
            assert re.fullmatch(r"\d{2}", row["alarmType"])
            assert re.fullmatch(r"\d{2}", row["alarmSource"])
            assert row["subName"] is None or isinstance(row["subName"], str)
            assert row["alarmClass"] is None or isinstance(row["alarmClass"], str)


class TestAlarmDisplayContractsMore:
    """补充校验报警记录中的展示字段和值模式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境没有数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("温度报警展示值保持摄氏度格式")
    def test_temperature_alarm_records_keep_temperature_display_pattern(self, auth_api, alarm_api, test_user):
        """校验温度报警支持单值及温度区间两种摄氏度展示格式。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)
        temperature_contents = [row["warnContent"] for row in rows if "℃" in row["warnContent"]]
        if not temperature_contents:
            pytest.skip("当前环境没有温度报警记录。")

        pattern = r"-?\d+(?:\.\d+)?℃(?:->-?\d+(?:\.\d+)?℃)?"
        assert all(re.fullmatch(pattern, content) for content in temperature_contents)

    @allure.title("报警记录前几条保持默认空关联字段")
    def test_alarm_record_first_rows_keep_nullable_relation_fields(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录仍保持默认空关联字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            assert row["dealUser"] is None
            assert row["dealUserName"] is None
            assert row["recoverDt"] is None
            assert row["monitorId"] is None
            assert row["conditionId"] is None


class TestAlarmOrderContractsExtra:
    """补充校验报警记录列表的顺序与可空字段契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境无数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("报警记录保持按等级和时间复合倒序排列")
    def test_alarm_record_rows_keep_descending_level_and_time_order(self, auth_api, alarm_api, test_user):
        """校验报警记录先按等级倒序，同一等级内再按报警时间倒序。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)
        order_keys = [(row["alarmLevel"], row["alarmDt"]) for row in rows]
        assert order_keys == sorted(order_keys, reverse=True)

    @allure.title("报警记录可空处理字段保持可空字符串契约")
    def test_alarm_record_rows_keep_nullable_deal_fields_contract(self, auth_api, alarm_api, test_user):
        """校验处理人、处理时间等可空字段仍保持可空字符串契约。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:5]:
            assert row["dealTime"] is None or isinstance(row["dealTime"], str)
            assert row["dealUser"] is None or isinstance(row["dealUser"], str)
            assert row["dealUserName"] is None or isinstance(row["dealUserName"], str)
            assert row["recoverDt"] is None or isinstance(row["recoverDt"], str)
            assert row["monitorId"] is None or isinstance(row["monitorId"], str)
            assert row["conditionId"] is None or isinstance(row["conditionId"], str)


class TestAlarmRuntimeContractsExtra:
    """补充校验报警记录当前未处理场景中的运行时默认值。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境没有数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("报警记录第一页主键保持唯一")
    def test_alarm_record_first_page_ids_are_unique(self, auth_api, alarm_api, test_user):
        """校验报警记录第一页返回的主键仍保持唯一。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:10]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("报警记录前几条未处理数据保持空处理字段")
    def test_alarm_record_first_rows_keep_null_processing_fields_when_status_is_open(self, auth_api, alarm_api, test_user):
        """校验未处理报警记录仍保持空处理字段和空联动结果字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            if row["status"] == "0":
                assert row["dealUser"] is None
                assert row.get("dealDt") is None or row.get("dealTime") is None
                assert row.get("dealContent") is None
                assert row.get("linkageStatus") is None

    @allure.title("报警记录前几条保持未删除与默认空站点字段")
    def test_alarm_record_first_rows_keep_default_deleted_and_station_fields(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录仍保持未删除标记和默认空站点字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            assert row["deleted"] == 0
            assert row["subName"] is None or isinstance(row["subName"], str)
            assert row["alarmClass"] is None or isinstance(row["alarmClass"], str)
