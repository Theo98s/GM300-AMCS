# -*- coding: utf-8 -*-
"""巡检记录接口基础查询测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检记录")
class TestPatrolRecordApi:
    """覆盖巡检记录首页、分页、筛选、主信息和明细接口。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保访问巡检记录业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _first_record(patrol_record_api):
        """获取首条巡检记录作为详情与筛选样本。"""
        rows = patrol_record_api.list_records(rows=1).json()["rows"]
        if not rows:
            pytest.skip("当前环境没有巡检记录。")
        return rows[0]

    @allure.title("巡检记录首页包含列表、详情和下载入口")
    def test_patrol_record_index_page(self, auth_api, patrol_record_api, test_user):
        """校验首页标题及三个核心业务地址均存在。"""
        self._login(auth_api, test_user)

        response = patrol_record_api.get_index_page()

        assert response.status_code == 200
        assert "<title>巡检记录</title>" in response.text
        assert "/amcs/patrol/record/findPatrolRecordList" in response.text
        assert "/amcs/patrol/record/detail" in response.text
        assert "/amcs/patrol/exportDialog" in response.text

    @allure.title("巡检记录列表返回标准分页结构")
    def test_patrol_record_page_contract(self, auth_api, patrol_record_api, test_user):
        """校验记录总数和数据行使用稳定分页字段。"""
        self._login(auth_api, test_user)

        body = patrol_record_api.list_records(rows=5).json()

        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) <= 5

    @allure.title("巡检记录列表遵守 rows 分页大小")
    def test_patrol_record_page_respects_rows(self, auth_api, patrol_record_api, test_user):
        """校验请求一条记录时接口不会返回额外数据。"""
        self._login(auth_api, test_user)

        body = patrol_record_api.list_records(rows=1).json()

        assert len(body["rows"]) == min(body["total"], 1)

    @allure.title("巡检记录行包含进度、成功率和失败点位字段")
    def test_patrol_record_row_contains_core_fields(self, auth_api, patrol_record_api, test_user):
        """校验首条记录具备列表展示和详情查询所需字段。"""
        self._login(auth_api, test_user)

        row = self._first_record(patrol_record_api)

        assert set(row) >= {
            "id",
            "cardCode",
            "cardName",
            "subName",
            "beginTime",
            "endTime",
            "timeLen",
            "patrolCount",
            "recordState",
            "failureCount",
            "finishRatio",
            "successRatio",
        }
        assert isinstance(row["id"], str) and row["id"]
        assert isinstance(row["beginTime"], int)
        assert isinstance(row["endTime"], int)

    @allure.title("巡检卡片名称筛选可回查原记录")
    def test_patrol_record_filter_by_card_name(self, auth_api, patrol_record_api, test_user):
        """校验列表中的卡片名称可作为筛选条件命中自身。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        body = patrol_record_api.list_records({"cardName": row["cardName"]}, rows=50).json()

        assert body["rows"]
        assert any(item["id"] == row["id"] for item in body["rows"])

    @allure.title("不存在的巡检卡片名称返回空分页")
    def test_patrol_record_unknown_card_returns_empty_page(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验唯一无效卡片名称不会命中现场记录。"""
        self._login(auth_api, test_user)

        body = patrol_record_api.list_records({"cardName": "NO_SUCH_CARD_8D7F"}).json()

        assert body == {"total": 0, "rows": []}

    @allure.title("已有巡检记录可打开详情页面")
    def test_patrol_record_list_to_detail_page(self, auth_api, patrol_record_api, test_user):
        """校验记录标识可进入详情页并加载主信息和明细地址。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        response = patrol_record_api.get_detail_page(row["id"])

        assert response.status_code == 200
        assert "<title>巡检记录详情</title>" in response.text
        assert row["id"] in response.text
        assert "/amcs/patrol/record/findPatrolRecordById" in response.text
        assert "/amcs/patrol/record/findRecordDetailList" in response.text

    @allure.title("巡检记录列表与主信息核心字段一致")
    def test_patrol_record_list_to_record_consistency(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验列表记录可查询主信息，卡片、时间和统计字段一致。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        detail = patrol_record_api.get_record(row["id"]).json()

        for field in (
            "id",
            "cardCode",
            "cardName",
            "subName",
            "beginTime",
            "endTime",
            "patrolCount",
            "failureCount",
            "finishRatio",
            "successRatio",
        ):
            assert detail[field] == row[field]

    @allure.title("巡检记录明细返回标准分页和点位字段")
    def test_patrol_record_detail_page_contract(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验点位明细包含状态、结果、测温和图片数量字段。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        body = patrol_record_api.list_record_details(row["id"], rows=5).json()

        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) <= 5
        if body["rows"]:
            assert set(body["rows"][0]) >= {
                "id",
                "recordId",
                "seq",
                "monitorName",
                "presetCode",
                "pictureCount",
                "status",
                "result",
                "remarks",
                "pointTemperature",
                "refTemperature",
                "diffTemperature",
            }

    @allure.title("巡检记录明细总数与主记录巡检点数一致")
    def test_patrol_record_detail_total_matches_patrol_count(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验详情分页总数能够反映主记录中的巡检点位数量。"""
        self._login(auth_api, test_user)
        row = self._first_record(patrol_record_api)

        body = patrol_record_api.list_record_details(row["id"], rows=1).json()

        assert body["total"] == row["patrolCount"]
