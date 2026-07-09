# -*- coding: utf-8 -*-
"""AMCS 业务模块访问控制异常场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestBusinessAccessControlAbnormalMore:
    """补充校验匿名访问各业务模块接口时的统一拦截行为。"""

    @staticmethod
    def _assert_redirects_to_login(response):
        """断言受保护接口会把匿名请求重定向到登录页。"""
        assert response.status_code == 302
        assert response.headers["Location"] == "/amcs/login"

    @allure.title("匿名访问视频接口会统一跳转登录页")
    def test_anonymous_video_endpoints_redirect_to_login(self, request_util, config):
        """校验视频树和预置位摄像机接口在匿名访问时都会被登录态保护。"""
        tree_response = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            json={},
            allow_redirects=False,
        )
        preset_response = request_util.send_request(
            "get",
            config["video"]["preset_cameras_url"],
            allow_redirects=False,
        )

        self._assert_redirects_to_login(tree_response)
        self._assert_redirects_to_login(preset_response)

    @allure.title("匿名访问巡检和历史接口会统一跳转登录页")
    def test_anonymous_patrol_and_history_endpoints_redirect_to_login(self, request_util, config):
        """校验巡检卡片、巡检计划和联动历史接口在匿名访问时都会被登录态保护。"""
        patrol_cards_response = request_util.send_request(
            "post",
            config["patrol"]["patrol_card_list_url"],
            data={},
            allow_redirects=False,
        )
        patrol_plans_response = request_util.send_request(
            "get",
            config["patrol"]["patrol_plan_list_url"],
            allow_redirects=False,
        )
        history_response = request_util.send_request(
            "post",
            config["history"]["monitor_link_history_url"],
            data={},
            allow_redirects=False,
        )

        self._assert_redirects_to_login(patrol_cards_response)
        self._assert_redirects_to_login(patrol_plans_response)
        self._assert_redirects_to_login(history_response)

    @allure.title("匿名访问 GIS 和 RDAC 接口会统一跳转登录页")
    def test_anonymous_gis_and_rdac_endpoints_redirect_to_login(self, request_util, config):
        """校验 GIS 二三维配置和 RDAC 站点列表接口在匿名访问时都会被登录态保护。"""
        d2_response = request_util.send_request(
            "get",
            config["gis"]["d2_map_prop_url"],
            allow_redirects=False,
        )
        d3_response = request_util.send_request(
            "get",
            config["gis"]["d3_map_prop_url"],
            allow_redirects=False,
        )
        gis_config_response = request_util.send_request(
            "post",
            config["gis"]["d3_gis_config_url"],
            json={},
            allow_redirects=False,
        )
        rdac_response = request_util.send_request(
            "post",
            config["rdac"]["station_list_url"],
            json={},
            allow_redirects=False,
        )

        self._assert_redirects_to_login(d2_response)
        self._assert_redirects_to_login(d3_response)
        self._assert_redirects_to_login(gis_config_response)
        self._assert_redirects_to_login(rdac_response)
