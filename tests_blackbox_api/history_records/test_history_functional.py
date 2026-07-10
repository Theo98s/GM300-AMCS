# -*- coding: utf-8 -*-
"""历史记录跨接口功能流程测试。"""
from __future__ import annotations

import pytest
import allure


class TestHistoryFunctionalFlowsMore:
    """补充覆盖历史记录分页切换和首行稳定性的功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证多次历史查询都落在同一会话下。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(history_api, payload: dict | None = None) -> tuple[int, list[dict]]:
        """返回历史分页结果；没有历史数据时跳过功能流校验。"""
        body = history_api.find_monitor_link_history(payload).json()
        rows = body["rows"]
        if not rows:
            pytest.skip("当前环境没有联动历史记录，跳过历史功能流校验。")
        return body["total"], rows

    @allure.title("同一登录会话可连续切换历史记录分页大小")
    def test_single_login_session_can_switch_history_page_sizes(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """登录后连续以不同 rows 参数查询历史记录，校验分页切换可用。"""
        self._login(auth_api, test_user)

        total_one, rows_one = self._rows_or_skip(history_api, {"rows": 1})
        total_three, rows_three = self._rows_or_skip(history_api, {"rows": 3})

        assert total_one >= 1
        assert len(rows_one) == 1
        assert total_three >= len(rows_three)
        assert len(rows_three) >= 1

    @allure.title("历史记录首条结果在小分页和大分页查询中保持一致")
    def test_history_first_row_stays_stable_across_small_and_large_page_sizes(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """连续查询 rows=1 和 rows=3 时，首条历史记录应保持一致。"""
        self._login(auth_api, test_user)

        _, rows_one = self._rows_or_skip(history_api, {"rows": 1})
        _, rows_three = self._rows_or_skip(history_api, {"rows": 3})

        assert rows_one[0]["id"] == rows_three[0]["id"]
        assert rows_one[0]["equipId"] == rows_three[0]["equipId"]
        assert rows_one[0]["createTime"] == rows_three[0]["createTime"]

    @allure.title("历史记录默认查询后仍可切换到自定义分页查询")
    def test_default_history_query_does_not_block_follow_up_paged_query(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """先执行默认历史查询，再切换到自定义 rows 查询，校验后续分页仍正常。"""
        self._login(auth_api, test_user)

        default_total, default_rows = self._rows_or_skip(history_api)
        paged_total, paged_rows = self._rows_or_skip(history_api, {"rows": 2})

        assert default_total >= len(default_rows)
        assert paged_total >= len(paged_rows)
        assert len(paged_rows) >= 1
        assert paged_rows[0]["description"]
        assert isinstance(paged_rows[0]["status"], str)
