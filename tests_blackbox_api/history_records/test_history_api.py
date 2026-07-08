# -*- coding: utf-8 -*-
"""AMCS 历史记录接口测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
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
