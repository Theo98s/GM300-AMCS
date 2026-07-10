# -*- coding: utf-8 -*-
"""报警事件与历史看板跨接口功能流程测试。"""
from __future__ import annotations

import re
import allure


class TestEventBoardFunctionalFlowsMore:
    """补充覆盖告警看板与历史看板的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证告警与历史接口共享同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("同一登录会话可连续加载告警看板和历史看板")
    def test_single_login_session_can_load_alarm_and_history_boards(
        self,
        auth_api,
        alarm_api,
        history_api,
        test_user,
    ):
        """登录一次后，连续访问告警记录和联动历史两块看板。"""
        self._login(auth_api, test_user)

        alarm_rows = alarm_api.get_alarm_record_page().json()
        history_body = history_api.find_monitor_link_history({"rows": 5}).json()

        assert isinstance(alarm_rows, list)
        assert isinstance(history_body["rows"], list)
        assert isinstance(history_body["total"], int)
        assert history_body["total"] >= len(history_body["rows"])

    @allure.title("告警与历史看板在同一会话内保持核心展示字段可用")
    def test_alarm_and_history_boards_keep_core_display_fields_in_same_session(
        self,
        auth_api,
        alarm_api,
        history_api,
        test_user,
    ):
        """连续加载告警与历史记录后，校验两边核心展示字段仍可直接用于页面渲染。"""
        self._login(auth_api, test_user)

        alarm_rows = alarm_api.get_alarm_record_page().json()
        history_rows = history_api.find_monitor_link_history({"rows": 3}).json()["rows"]

        if alarm_rows:
            first_alarm = alarm_rows[0]
            assert first_alarm["equipName"]
            assert first_alarm["warnContent"]
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", first_alarm["alarmDt"])

        assert len(history_rows) > 0
        first_history = history_rows[0]
        assert first_history["equipName"]
        assert first_history["description"]
        assert isinstance(first_history["createTime"], int)
        assert isinstance(first_history["status"], str)

    @allure.title("加载告警看板后历史看板仍可按分页参数切换")
    def test_history_board_can_still_page_after_alarm_board_is_loaded(
        self,
        auth_api,
        alarm_api,
        history_api,
        test_user,
    ):
        """先加载告警看板，再校验历史看板仍可按不同 rows 参数切换分页。"""
        self._login(auth_api, test_user)

        alarm_rows = alarm_api.get_alarm_record_page().json()
        one_row_body = history_api.find_monitor_link_history({"rows": 1}).json()
        three_row_body = history_api.find_monitor_link_history({"rows": 3}).json()

        assert isinstance(alarm_rows, list)
        assert one_row_body["total"] >= 1
        assert len(one_row_body["rows"]) == 1
        assert three_row_body["total"] >= 3
        assert len(three_row_body["rows"]) == 3
