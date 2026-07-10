# -*- coding: utf-8 -*-
"""AMCS 业务接口匿名默认访问异常场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestBusinessAccessDefaultAbnormalMore:
    """补充校验匿名访问受保护接口且默认跟随重定向时会落到登录页 HTML。"""

    @staticmethod
    def _assert_login_html(response):
        """断言匿名默认请求最终落到登录页 HTML。"""
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "/sso/ajaxcheck" in response.text
        assert "window.top" in response.text

    @allure.title("匿名默认访问视频接口最终落到登录页 HTML")
    def test_anonymous_video_default_requests_resolve_to_login_html(self, request_util, config):
        """校验视频树和预置位摄像机接口在默认重定向行为下都会落到登录页。"""
        tree_response = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            json={},
        )
        preset_response = request_util.send_request(
            "get",
            config["video"]["preset_cameras_url"],
        )

        self._assert_login_html(tree_response)
        self._assert_login_html(preset_response)

    @allure.title("匿名默认访问巡检和历史接口最终落到登录页 HTML")
    def test_anonymous_patrol_and_history_default_requests_resolve_to_login_html(self, request_util, config):
        """校验巡检卡片、巡检计划和联动历史接口默认访问时都会落到登录页。"""
        patrol_cards_response = request_util.send_request(
            "post",
            config["patrol"]["patrol_card_list_url"],
            data={},
        )
        patrol_plans_response = request_util.send_request(
            "get",
            config["patrol"]["patrol_plan_list_url"],
        )
        history_response = request_util.send_request(
            "post",
            config["history"]["monitor_link_history_url"],
            data={},
        )

        self._assert_login_html(patrol_cards_response)
        self._assert_login_html(patrol_plans_response)
        self._assert_login_html(history_response)

    @allure.title("匿名默认访问 GIS 和 RDAC 接口最终落到登录页 HTML")
    def test_anonymous_gis_and_rdac_default_requests_resolve_to_login_html(self, request_util, config):
        """校验 GIS 配置和 RDAC 站点接口默认访问时都会落到登录页。"""
        gis_config_response = request_util.send_request(
            "post",
            config["gis"]["d3_gis_config_url"],
            json={},
        )
        rdac_response = request_util.send_request(
            "post",
            config["rdac"]["station_list_url"],
            json={},
        )

        self._assert_login_html(gis_config_response)
        self._assert_login_html(rdac_response)
