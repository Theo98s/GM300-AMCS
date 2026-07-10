# -*- coding: utf-8 -*-
"""巡检卡片与计划字段、一致性、排期和运行时契约测试。"""
from __future__ import annotations

import allure
import pytest
import numbers
import re


class TestPatrolConsistencyContractsExtra:
    """补充校验巡检计划与其嵌套详情的一致性。"""

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
    def _plans_or_skip(patrol_api):
        """返回巡检计划；如果当前环境没有数据则跳过。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("Current environment has no patrol plans.")
        return plans

    @allure.title("巡检计划 multi 字段保持卡片名称与编码对齐")
    def test_patrol_plan_multi_field_keeps_card_name_and_code_alignment(self, auth_api, patrol_api, test_user):
        """校验每条巡检计划的 multi 字段都包含卡片名称和卡片编码。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["multi"], str) and plan["multi"]
            assert plan["cardName"] in plan["multi"]
            assert plan["cardCode"] in plan["multi"]

    @allure.title("巡检计划时间字段保持可空结束时间顺序契约")
    def test_patrol_plan_times_keep_nullable_end_time_ordering_contract(self, auth_api, patrol_api, test_user):
        """校验巡检计划保持毫秒 beginTime，且 endTime 为空或不早于 beginTime。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["beginTime"], int)
            assert plan["beginTime"] > 0
            assert plan["endTime"] is None or isinstance(plan["endTime"], int)
            if plan["endTime"] is not None:
                assert plan["endTime"] >= plan["beginTime"]

    @allure.title("巡检详情行保持父级 recordId 和顺序 seq 值")
    def test_patrol_plan_details_keep_parent_recordid_and_sequential_seq(self, auth_api, patrol_api, test_user):
        """校验嵌套巡检详情保持父级 recordId 契约和顺序递增的字符串 seq。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            details = plan["details"]
            if not details:
                continue

            expected_seq = [str(index) for index in range(len(details))]
            assert [detail["seq"] for detail in details] == expected_seq
            for detail in details:
                assert detail["recordId"] == plan["recordId"]
                assert isinstance(detail["presetCode"], int)
                assert detail["presetCode"] >= 0


class TestPatrolContractsExtra:
    """补充校验巡检计划与详情契约。"""

    @allure.title("巡检计划开始时间保持毫秒时间戳")
    def test_patrol_plan_begin_time_uses_millisecond_timestamp(self, auth_api, patrol_api, test_user):
        """校验巡检计划存在时，beginTime 仍为正整数毫秒时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body:
            pytest.skip("Current environment has no patrol plans.")

        first_plan = body[0]
        assert isinstance(first_plan["beginTime"], int)
        assert first_plan["beginTime"] >= 10**12


class TestPatrolContractsMore:
    """补充校验巡检计划及详情行契约。"""

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
    def _plans_or_skip(patrol_api):
        """返回巡检计划；如果当前环境没有数据则跳过。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("Current environment has no patrol plans.")
        return plans

    @allure.title("巡检计划保留执行标记与状态契约")
    def test_patrol_plan_execution_flags_keep_expected_types(self, auth_api, patrol_api, test_user):
        """校验首条巡检计划保持字符串执行状态和布尔控制标记。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        assert isinstance(first_plan["centerType"], str) and first_plan["centerType"]
        assert isinstance(first_plan["executeType"], str) and first_plan["executeType"]
        assert first_plan["executeState"] is None or isinstance(first_plan["executeState"], str)
        assert isinstance(first_plan["canBeStarted"], bool)
        assert isinstance(first_plan["movable"], bool)
        assert isinstance(first_plan["receivedFirstPointResult"], bool)

    @allure.title("巡检详情行保留可空结果字段契约")
    def test_patrol_plan_detail_result_fields_keep_nullable_text_contracts(self, auth_api, patrol_api, test_user):
        """校验首条巡检详情保持可空结果字段和数值温度契约。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        if not first_plan["details"]:
            pytest.skip("Current environment has no patrol plan details.")

        first_detail = first_plan["details"][0]
        assert first_detail["result"] is None or isinstance(first_detail["result"], str)
        assert first_detail["valueResult"] is None or isinstance(first_detail["valueResult"], str)
        assert first_detail["standResult"] is None or isinstance(first_detail["standResult"], str)
        assert first_detail["valueStatus"] is None or isinstance(first_detail["valueStatus"], str)
        assert first_detail["pointTemperature"] is None or isinstance(first_detail["pointTemperature"], numbers.Real)
        assert isinstance(first_detail["ext"], dict)


class TestPatrolRuntimeContractsExtra:
    """补充校验巡检计划和卡片中的运行时稳定字段。"""

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
    def _plans_or_skip(patrol_api):
        """返回巡检计划；如果当前环境没有数据则跳过。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("当前环境没有巡检计划。")
        return plans

    @allure.title("巡检计划前几条记录保持 cron 与 weeks 调度字段格式")
    def test_patrol_plan_first_rows_keep_schedule_field_formats(self, auth_api, patrol_api, test_user):
        """校验前几条巡检计划仍保留调度表达式和周配置格式。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            assert isinstance(plan["cron"], str) and plan["cron"]
            assert plan["weeks"] is None or re.fullmatch(r"\d+(,\d+)*", plan["weeks"])
            assert isinstance(plan["residenceTime"], int)
            assert plan["residenceTime"] >= 0

    @allure.title("巡检计划前几条详情记录保持预置位与抓拍字段契约")
    def test_patrol_plan_first_details_keep_preset_and_capture_contracts(self, auth_api, patrol_api, test_user):
        """校验前几条巡检详情记录仍保持预置位、抓拍和空扩展字段模式。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:2]:
            details = plan["details"]
            if not details:
                continue

            for detail in details[:5]:
                assert isinstance(detail["monitorName"], str) and detail["monitorName"]
                assert isinstance(detail["presetCode"], int)
                assert detail["presetCode"] >= 0
                assert isinstance(detail["pictureCount"], int)
                assert detail["pictureCount"] >= 0
                assert detail["captureTime"] is None or isinstance(detail["captureTime"], int)
                assert detail["picsPath"] is None or isinstance(detail["picsPath"], str)
                assert detail["ext"] == {}

    @allure.title("巡检卡片列表保持非空名称和不为零的点位数量")
    def test_patrol_cards_keep_non_empty_names_and_positive_point_counts(self, auth_api, patrol_api, test_user):
        """校验巡检卡片仍保留非空名称，且每张卡片至少包含一个点位。"""
        self._login(auth_api, test_user)

        rows = patrol_api.list_patrol_cards().json()
        assert len(rows) > 0
        for row in rows:
            assert isinstance(row["text"], str) and row["text"]
            assert isinstance(row["pointamount"], int)
            assert row["pointamount"] > 0
            assert isinstance(row["equipamount"], int)
            assert row["equipamount"] > 0


class TestPatrolScheduleContractsMore:
    """补充校验巡检计划状态、调度和详情时间对齐关系。"""

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
    def _plans_or_skip(patrol_api):
        """返回巡检计划；如果当前环境没有数据则跳过。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("当前环境没有巡检计划。")
        return plans

    @allure.title("巡检计划保持段级中心和固定可启动标记")
    def test_patrol_plan_rows_keep_center_type_and_start_flag(self, auth_api, patrol_api, test_user):
        """校验当前巡检计划仍使用段级中心类型，并保持可启动布尔标记。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:5]:
            assert plan["centerType"] == "DUAN"
            assert plan["executeType"] == "0"
            assert plan["canBeStarted"] is True
            assert plan["movable"] is False

    @allure.title("巡检计划状态与调度字段保持当前空值分支")
    def test_patrol_plan_rows_keep_schedule_nullability_by_execute_state(self, auth_api, patrol_api, test_user):
        """校验运行中计划和结束计划仍保持当前调度字段空值分支。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:5]:
            if plan["executeState"] is None:
                assert isinstance(plan["cron"], str) and plan["cron"]
                assert isinstance(plan["weeks"], str) and plan["weeks"]
                assert plan["recordId"] is None
            else:
                assert plan["executeState"] == "END"
                assert plan["cron"] is None
                assert plan["weeks"] is None
                assert isinstance(plan["recordId"], str) and plan["recordId"]

    @allure.title("巡检详情前几条记录保持与计划停留时长对齐")
    def test_patrol_plan_details_keep_residence_time_aligned_with_plan(self, auth_api, patrol_api, test_user):
        """校验巡检详情前几条记录仍与父计划保持相同停留时长。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            details = plan["details"]
            if not details:
                continue
            for detail in details[:5]:
                assert detail["residenceTime"] == plan["residenceTime"]
                assert detail["channelNum"] is None
                assert detail["visibleChannelNum"] is None
                assert detail["nvrSerialNum"] is None
                assert detail["visibleNvrSerialNum"] is None
