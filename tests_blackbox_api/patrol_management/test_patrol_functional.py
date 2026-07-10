# -*- coding: utf-8 -*-
"""巡检卡片、计划与巡检记录跨接口功能流程测试。"""
from __future__ import annotations

import pytest
import allure


class TestPatrolFunctionalFlowsMore:
    """补充覆盖巡检卡片、计划和详情之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证巡检卡片和计划查询复用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _plans_or_skip(patrol_api) -> list[dict]:
        """返回巡检计划；如果当前环境没有计划，则跳过计划相关功能流。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("当前环境没有巡检计划，跳过巡检计划功能流校验。")
        return plans

    @staticmethod
    def _first_detail_or_skip(plan: dict) -> dict:
        """返回首个巡检点位详情；如果当前计划没有详情，则跳过明细相关校验。"""
        details = plan["details"]
        if not details:
            pytest.skip("当前巡检计划没有点位详情，跳过详情功能流校验。")
        return details[0]

    @allure.title("同一登录会话可连续加载巡检卡片和巡检计划")
    def test_single_login_session_can_load_patrol_cards_and_plans(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """登录一次后，连续访问巡检卡片列表和巡检计划列表。"""
        self._login(auth_api, test_user)

        card_rows = patrol_api.list_patrol_cards().json()
        plan_rows = patrol_api.list_patrol_plans().json()

        assert isinstance(card_rows, list)
        assert len(card_rows) > 0
        assert isinstance(plan_rows, list)

    @allure.title("巡检计划中的卡片名称可在巡检卡片列表中回查到")
    def test_patrol_plan_card_name_can_be_resolved_from_patrol_card_list(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """如果当前环境存在巡检计划，则校验计划关联的卡片名称能在卡片列表中找到。"""
        self._login(auth_api, test_user)

        card_rows = patrol_api.list_patrol_cards().json()
        plan_rows = self._plans_or_skip(patrol_api)
        card_names = {row["text"] for row in card_rows}
        first_plan = plan_rows[0]

        assert first_plan["cardName"] in card_names
        assert first_plan["subName"]
        assert isinstance(first_plan["canBeStarted"], bool)

    @allure.title("巡检计划详情可在同一会话内完成明细初始化")
    def test_patrol_plan_detail_can_bootstrap_in_same_session(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """如果当前环境存在巡检详情，则校验首个点位详情可直接用于页面初始化。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        first_detail = self._first_detail_or_skip(first_plan)

        assert first_plan["cardName"]
        assert isinstance(first_plan["details"], list)
        assert first_detail["monitorName"]
        assert isinstance(first_detail["residenceTime"], int)
        assert isinstance(first_detail["pictureCount"], int)
        assert isinstance(first_detail["seq"], str)
        assert isinstance(first_detail["ext"], dict)


class TestPatrolRecordFunctional:
    """覆盖记录主信息、点位明细、附件和报告导出入口的完整链路。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保功能链路复用同一权限。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _first_record(patrol_record_api):
        """获取首条巡检记录作为只读流程样本。"""
        rows = patrol_record_api.list_records(rows=1).json()["rows"]
        if not rows:
            pytest.skip("当前环境没有巡检记录。")
        return rows[0]

    @allure.title("巡检记录主信息包含可读时间和完成情况说明")
    def test_patrol_record_summary_strings(self, auth_api, patrol_record_api, test_user):
        """校验主信息将时间、点位数量和完成率转换为可读文本。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        detail = patrol_record_api.get_record(row["id"]).json()

        assert str(row["patrolCount"]) in detail["finishRatioStr"]
        assert str(row["finishRatio"]).rstrip(".0") in detail["finishRatioStr"]
        assert detail["beginTimeStr"] in detail["timeStr"]
        assert isinstance(detail["recordstateName"], str) and detail["recordstateName"]

    @allure.title("巡检明细序号按升序排列且标识唯一")
    def test_patrol_record_detail_sequence_and_ids(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验同一记录的点位明细顺序稳定且不会重复。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        details = patrol_record_api.list_record_details(row["id"], rows=200).json()["rows"]
        sequences = [int(item["seq"]) for item in details]
        ids = [item["id"] for item in details]

        assert sequences == sorted(sequences)
        assert len(ids) == len(set(ids))
        assert all(item["recordId"] == row["id"] for item in details)

    @allure.title("巡检明细图片数量与显示字段保持一致")
    def test_patrol_record_picture_count_display_alignment(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验每条点位明细的图片数量数值和显示文本一致。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        details = patrol_record_api.list_record_details(row["id"], rows=200).json()["rows"]

        assert details
        assert all(item["pictureCountStr"] == str(item["pictureCount"]) for item in details)

    @allure.title("巡检明细附件接口返回标准业务包装")
    def test_patrol_record_attachment_contract(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """选择首条明细查询附件，兼容现场有图和无图两种响应。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)
        details = patrol_record_api.list_record_details(row["id"], rows=200).json()["rows"]
        if not details:
            pytest.skip("当前巡检记录没有点位明细。")

        response = patrol_record_api.get_attaches(details[0]["id"])
        body = response.json()

        assert response.status_code == 200
        assert body["status"] in {0, 1}
        assert set(body) == {"status", "message", "data"}

    @allure.title("巡检记录允许打开三种报告下载方式")
    def test_patrol_record_export_dialog_contract(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验导出弹窗包含仅 Excel、缩略图和原图三种下载动作。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        response = patrol_record_api.get_export_dialog(
            row["id"],
            row["subName"],
            row["cardName"],
            "2026-07-10 00:00:00",
        )

        assert response.status_code == 200
        assert "<title>导出巡检报告</title>" in response.text
        assert "exportRecordExcel" in response.text
        assert "exportExcelAndImg" in response.text
        assert "downLoadZip" in response.text

    @allure.title("巡检记录导出校验和执行页面均可访问")
    def test_patrol_record_export_entry_flow(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验已有记录允许导出，并可打开报告生成执行页面。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        can_export = patrol_record_api.can_export(row["id"])
        assert can_export.status_code == 200
        assert can_export.json() == {"status": 0, "message": "", "data": None}

        export_page = patrol_record_api.get_export_page()
        assert export_page.status_code == 200
        assert "exportRecord" in export_page.text
        assert "getRecordDetail" in export_page.text
