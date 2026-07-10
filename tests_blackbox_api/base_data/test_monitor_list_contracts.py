# -*- coding: utf-8 -*-
"""监控点列表字段、分页、格式、空值与运行时契约测试。"""
from __future__ import annotations

import json
import allure
import re


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


class TestMonitorListPageContractsExtra:
    """补充校验监控点列表第一页记录。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 id 保持唯一")
    def test_monitor_list_first_page_ids_are_unique(self, auth_api, database_api, test_user):
        """校验监控点列表第一页记录的 id 保持唯一。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("监控点列表 yx 标签值保持非空")
    def test_monitor_list_yx_labels_are_non_empty(self, auth_api, database_api, test_user):
        """校验首条监控点记录中解析出的 yx 标签保持非空字符串。"""
        self._login(auth_api, test_user)

        first_row = database_api.list_monitors(rows=1).json()["rows"][0]
        yx_config = json.loads(first_row["yx"])
        assert yx_config["TRUE_LABEL"]
        assert yx_config["FALSE_LABEL"]


class TestMonitorListFormatContractsMore:
    """补充校验监控点列表表格中的行级格式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行分类字段保持数字字符串")
    def test_monitor_list_first_rows_keep_code_field_patterns(self, auth_api, database_api, test_user):
        """校验前几条记录中的 alarmClass 和 securityequiptype 保持数字字符串格式。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert re.fullmatch(r"\d{2}", row["alarmClass"])
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])

    @allure.title("监控点列表前几行 yx 配置键集合保持一致")
    def test_monitor_list_first_rows_keep_consistent_yx_keys(self, auth_api, database_api, test_user):
        """校验前几条监控点记录解析后的 yx 键集合保持一致。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        key_sets = [set(json.loads(row["yx"]).keys()) for row in rows]
        assert all(keys == {"TRUE_LABEL", "FALSE_LABEL"} for keys in key_sets)


class TestMonitorListNullableContractsMore:
    """补充校验监控点列表前几条记录的可空字段和默认空值。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几条记录保持空十六进制地址字段")
    def test_monitor_list_first_rows_keep_nullable_scada_addr16(self, auth_api, database_api, test_user):
        """校验前几条监控点记录仍保持空 scadaAddr16 字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["scadaAddr16"] is None

    @allure.title("监控点列表前几条遥信记录保持空量测控制字段")
    def test_monitor_list_first_rows_keep_empty_yc_yk_yt_fields(self, auth_api, database_api, test_user):
        """校验前几条遥信记录仍未填充 yc、yk、yt 扩展字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["yc"] is None
            assert row["yk"] is None
            assert row["yt"] is None

    @allure.title("监控点列表前几条记录保持空偏移与变化阈值字段")
    def test_monitor_list_first_rows_keep_empty_offset_threshold_fields(self, auth_api, database_api, test_user):
        """校验前几条记录在当前环境下仍未配置偏移和变化阈值字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["offset"] == ""
            assert row["changeRatio"] == ""
            assert row["changeThreshold"] == ""


class TestMonitorListRuntimeContractsMore:
    """补充校验监控点列表前几条记录中的默认值与审计字段。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几条记录保持默认状态标记字段契约")
    def test_monitor_list_first_rows_keep_default_flag_fields(self, auth_api, database_api, test_user):
        """校验前几条监控点记录的默认状态标记仍保持当前类型和值域。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        assert len(rows) == 5

        for row in rows:
            assert row["deleted"] in {0, 1}
            assert row["isOffset"] in {"0", "1"}
            assert row["isRatio"] in {"0", "1"}
            assert row["isVirtual"] in {"0", "1"}
            assert row["isrelease"] in {"0", "1"}

    @allure.title("监控点列表前几条遥信记录保持空趋势配置字段")
    def test_monitor_list_first_rows_keep_empty_trend_fields(self, auth_api, database_api, test_user):
        """校验前几条记录在当前环境下仍未配置趋势告警相关字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["trendAlarmEnable"] == ""
            assert row["trendAlarmLevel"] == ""
            assert row["trendChangeThreshold"] == ""
            assert row["trendInterval"] == ""
            assert row["linkageStatus"] is None

    @allure.title("监控点列表前几条记录保持审计时间和站点字段格式")
    def test_monitor_list_first_rows_keep_audit_and_station_field_formats(self, auth_api, database_api, test_user):
        """校验前几条记录仍保留站点标识、创建人和创建时间格式。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert isinstance(row["subId"], str) and row["subId"]
            assert isinstance(row["creator"], str) and row["creator"]
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", row["createTime"])
            assert row["updateTime"] is None or re.fullmatch(
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
                row["updateTime"],
            )


class TestMonitorListValueContractsMore:
    """补充校验监控点列表第一页字段值稳定性。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 isStored 字段保持 0/1 字符串")
    def test_monitor_list_first_rows_keep_is_stored_string_flags(self, auth_api, database_api, test_user):
        """校验前几条监控点记录中的 isStored 仍使用字符串标记值。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["isStored"] in {"0", "1"}

    @allure.title("监控点列表前几行告警数据类型字段保持非空")
    def test_monitor_list_first_rows_keep_non_empty_alarm_datatype(self, auth_api, database_api, test_user):
        """校验前几条监控点记录中的 alarmDatatype 保持非空。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert isinstance(row["alarmDatatype"], str)
            assert row["alarmDatatype"]
