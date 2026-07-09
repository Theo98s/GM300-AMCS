# -*- coding: utf-8 -*-
"""AMCS 首页子菜单补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeChildContractsExtra:
    """补充校验首页子菜单和设备区域字典的细节字段。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("设备区域字典保持完整编码顺序和默认展示字段")
    def test_equip_area_dict_keeps_full_code_order_and_display_defaults(self, auth_api, home_api, test_user):
        """校验设备区域字典仍保留 00 到 12 的完整编码顺序和默认展示字段。"""
        self._login(auth_api, test_user)

        rows = home_api.list_dict_no_root("EQUIP_AREA").json()
        assert [row["code"] for row in rows] == [f"{index:02d}" for index in range(13)]

        for row in rows:
            assert row["url"] == ""
            assert row["openClosed"] == "open"
            assert row["checked"] is False
            assert row["text"] == row["name"]

    @allure.title("首页视频子菜单保持 pageurl 与 url 对齐")
    def test_init_menu_video_children_keep_pageurl_alignment(self, auth_api, home_api, test_user):
        """校验视频子菜单仍保留 pageurl、url、类型和默认状态对齐关系。"""
        self._login(auth_api, test_user)

        host_leaf = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        video_children = next(item for item in host_leaf if item["id"] == "GM300-AMCS:video")["leaf"]
        assert len(video_children) == 3

        for row in video_children:
            assert row["pageurl"] == row["url"]
            assert row["type"] == 1
            assert row["displayFlag"] == 0
            assert row["leaf"] == []
            assert row["checked"] is False
            assert row["pluginKey"] == "GM300-AMCS"

    @allure.title("首页实时监控与巡检管理子菜单保持稳定数量")
    def test_init_menu_realtime_and_patrol_children_keep_expected_counts(self, auth_api, home_api, test_user):
        """校验实时监控和巡检管理模块仍保留当前稳定子菜单数量。"""
        self._login(auth_api, test_user)

        host_leaf = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        realtime_children = next(item for item in host_leaf if item["id"] == "GM300-AMCS:amcs_das")["leaf"]
        patrol_children = next(item for item in host_leaf if item["id"] == "GM300-AMCS:amcs_patrol")["leaf"]

        assert len(realtime_children) == 4
        assert len(patrol_children) == 3
