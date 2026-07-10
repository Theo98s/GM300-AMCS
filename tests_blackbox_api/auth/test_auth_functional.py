# -*- coding: utf-8 -*-
"""登录会话与平台接口功能流程测试。"""
from __future__ import annotations

import allure


class TestAuthFunctionalFlowsMore:
    """补充覆盖登录成功后跨模块初始化的功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行成功登录，减少各条功能流里的重复样板。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "登录成功"
        return body

    @allure.title("登录成功后可连续完成首页菜单和用户菜单树初始化")
    def test_login_success_can_bootstrap_home_menu_and_user_menu_tree(
        self,
        auth_api,
        home_api,
        menu_api,
        test_user,
    ):
        """登录成功后连续访问首页菜单和用户菜单树，校验导航初始化链路可用。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        menu_tree_body = menu_api.get_user_menu_tree().json()

        assert init_menu_body["status"] == 0
        assert init_menu_body["data"]["hostMenuList"][0]["leaf"][0]["url"] == "/das/home"
        assert menu_tree_body[0]["id"] == "GM300-AMCS"
        assert menu_tree_body[0]["children"][0]["url"] == "/das/home"

    @allure.title("重复成功登录后会话仍可访问告警数和时间戳接口")
    def test_repeated_successful_login_keeps_session_available_for_system_queries(
        self,
        auth_api,
        system_api,
        test_user,
    ):
        """连续执行两次成功登录后，校验同一会话仍可访问系统查询接口。"""
        first_login_body = self._login(auth_api, test_user)
        second_login_body = self._login(auth_api, test_user)

        alarm_count_body = system_api.get_alarm_count().json()
        timestamp_value = system_api.get_timestamp().json()

        assert first_login_body["data"] == "/"
        assert second_login_body["data"] == "/"
        assert alarm_count_body["status"] == 0
        assert isinstance(alarm_count_body["data"], int)
        assert alarm_count_body["data"] >= 0
        assert isinstance(timestamp_value, int)
        assert timestamp_value >= 10**12

    @allure.title("先访问登录页再登录可完成字典初始化")
    def test_visit_login_page_before_login_does_not_block_dictionary_bootstrap(
        self,
        auth_api,
        home_api,
        test_user,
    ):
        """先打开登录页，再执行登录并查询区域字典，校验认证前置页不会破坏后续初始化流程。"""
        login_page_response = auth_api.get_login_page()
        assert login_page_response.status_code == 200
        assert "text/html" in login_page_response.headers.get("Content-Type", "")

        # 这里显式走一遍登录页到登录提交的顺序，贴近真实用户打开系统后的操作路径。
        self._login(auth_api, test_user)

        equip_area_rows = home_api.list_dict_no_root("EQUIP_AREA").json()
        area_map = {item["code"]: item["name"] for item in equip_area_rows}

        assert area_map["00"] == "全区"
        assert area_map["01"] == "进线区"
