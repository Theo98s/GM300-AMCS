# -*- coding: utf-8 -*-
"""巡检卡片、计划与巡检记录基础接口测试。"""
from __future__ import annotations

import allure
import pytest


class TestPatrolApi:
    """巡检卡片和巡检计划查询用例。"""

    @allure.title("巡检卡片列表可正常返回")
    def test_patrol_card_list_returns_cards(self, auth_api, patrol_api, test_user):
        """校验巡检卡片列表至少能返回一条卡片数据。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        assert len(body) > 0
        first_item = body[0]
        assert set(first_item.keys()) >= {"id", "text", "equipamount", "pointamount"}

    @allure.title("巡检卡片列表数量字段为非负整数")
    def test_patrol_card_list_count_fields_are_non_negative(self, auth_api, patrol_api, test_user):
        """校验巡检卡片中的设备数和点位数格式正确。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        body = response.json()

        for item in body:
            assert isinstance(item["equipamount"], int)
            assert isinstance(item["pointamount"], int)
            assert item["equipamount"] >= 0
            assert item["pointamount"] >= 0

    @allure.title("巡检计划列表接口可访问")
    def test_patrol_plan_list_accessible(self, auth_api, patrol_api, test_user):
        """校验巡检计划列表接口可正常访问，即使当前没有计划数据。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)

    @allure.title("巡检计划列表项包含计划基础字段")
    def test_patrol_plan_list_items_contain_plan_fields(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验首条记录包含计划名称、所亭和时间字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body:
            pytest.skip("当前环境没有巡检计划，跳过计划字段校验")

        first_plan = body[0]
        assert set(first_plan.keys()) >= {"cardName", "subName", "beginTime", "canBeStarted", "details", "weeks"}
        assert isinstance(first_plan["beginTime"], int)
        assert isinstance(first_plan["canBeStarted"], bool)
        assert isinstance(first_plan["details"], list)

    @allure.title("巡检计划详情项包含点位与停留时长字段")
    def test_patrol_plan_details_contain_point_fields(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验详情点位包含监控点名称、预置位和停留时长字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body or not body[0]["details"]:
            pytest.skip("当前环境没有巡检计划详情，跳过详情字段校验")

        first_detail = body[0]["details"][0]
        assert set(first_detail.keys()) >= {"monitorName", "presetName", "residenceTime", "pictureCount", "seq"}
        assert first_detail["monitorName"]
        assert first_detail["presetName"] is None or isinstance(first_detail["presetName"], str)
        assert first_detail["residenceTime"] >= 0
        assert first_detail["pictureCount"] >= 0

    @allure.title("巡检计划详情扩展字段保持字典结构")
    def test_patrol_plan_details_ext_field_is_dict(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验详情 ext 字段仍是对象结构。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body or not body[0]["details"]:
            pytest.skip("当前环境没有巡检计划详情，跳过 ext 字段校验")

        first_detail = body[0]["details"][0]
        assert isinstance(first_detail["ext"], dict)
        assert isinstance(first_detail["seq"], str)

    @allure.title("巡检卡片列表主键唯一且名称非空")
    def test_patrol_card_ids_are_unique_and_names_non_empty(self, auth_api, patrol_api, test_user):
        """校验巡检卡片列表中的卡片主键唯一，且名称字段非空。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        body = response.json()

        card_ids = [item["id"] for item in body]
        card_names = [item["text"] for item in body]
        assert len(card_ids) == len(set(card_ids))
        assert all(card_names)

    @allure.title("巡检计划周期字段保持预期类型")
    def test_patrol_plan_cycle_fields_use_expected_types(self, auth_api, patrol_api, test_user):
        """校验计划周期字段存在，并保持允许为空的字符串契约。"""
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
        assert "weeks" in first_plan
        assert first_plan["weeks"] is None or isinstance(first_plan["weeks"], str)
        assert isinstance(first_plan["canBeStarted"], bool)

    @allure.title("巡检计划基础展示字段保持非空")
    def test_patrol_plan_primary_display_fields_are_non_empty(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验卡片名和所属所亭等核心展示字段保持非空。"""
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
        assert first_plan["cardName"]
        assert first_plan["subName"]
        assert isinstance(first_plan["details"], list)

    @allure.title("巡检计划详情字段保持整数与数字字符串约定")
    def test_patrol_plan_detail_numeric_fields_keep_expected_types(self, auth_api, patrol_api, test_user):
        """有巡检计划详情时校验停留时长、抓拍数量和序号字段类型稳定。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body or not body[0]["details"]:
            pytest.skip("Current environment has no patrol plan details.")

        first_detail = body[0]["details"][0]
        assert isinstance(first_detail["residenceTime"], int)
        assert isinstance(first_detail["pictureCount"], int)
        assert isinstance(first_detail["seq"], str)
        assert first_detail["seq"].isdigit()


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
