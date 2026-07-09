# -*- coding: utf-8 -*-
"""AMCS 监控点列表补充契约测试。"""
from __future__ import annotations

import json

import allure


@allure.feature("基础数据库")
class TestMonitorListContractsExtra:
    """补充校验监控点列表返回结构。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表顶层结构保持 total 与 rows 契约")
    def test_monitor_list_top_level_contract_is_stable(self, auth_api, database_api, test_user):
        """校验监控点列表仍返回整数 total 和列表 rows 字段。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(rows=3)
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert body["total"] >= len(body["rows"])

    @allure.title("监控点列表首行基础标识字段保持字符串类型")
    def test_monitor_list_first_row_identity_fields_use_expected_types(self, auth_api, database_api, test_user):
        """校验首条监控点记录保持稳定的字符串标识和编码字段。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(rows=1)
        body = response.json()
        assert len(body["rows"]) == 1

        first_row = body["rows"][0]
        assert isinstance(first_row["id"], str) and first_row["id"]
        assert isinstance(first_row["equipId"], str) and first_row["equipId"]
        assert isinstance(first_row["alarmDatatype"], str) and first_row["alarmDatatype"]
        assert isinstance(first_row["alarmClass"], str) and first_row["alarmClass"]
        assert isinstance(first_row["securityequiptype"], str) and first_row["securityequiptype"]
        assert first_row["isStored"] in {"0", "1"}
        assert isinstance(first_row["scadaAddr10"], str)

    @allure.title("监控点列表首行 yx 字段保持可解析 JSON")
    def test_monitor_list_first_row_yx_is_parseable_json(self, auth_api, database_api, test_user):
        """校验首条监控点记录中的 yx 字段仍是包含真假标签的 JSON 文本。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(rows=1)
        body = response.json()
        assert len(body["rows"]) == 1

        first_row = body["rows"][0]
        yx_config = json.loads(first_row["yx"])
        assert set(yx_config.keys()) >= {"TRUE_LABEL", "FALSE_LABEL"}
        assert isinstance(yx_config["TRUE_LABEL"], str)
        assert isinstance(yx_config["FALSE_LABEL"], str)
