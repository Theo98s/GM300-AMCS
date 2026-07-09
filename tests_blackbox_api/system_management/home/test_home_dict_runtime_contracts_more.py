# -*- coding: utf-8 -*-
"""AMCS 首页区域字典运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeDictRuntimeContractsMore:
    """补充校验设备区域字典中的默认值和编码分布。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("设备区域字典各项保持默认分类与状态字段")
    def test_equip_area_dict_rows_keep_default_category_and_state_fields(self, auth_api, home_api, test_user):
        """校验设备区域字典各项仍保持默认分类标记和空状态字段。"""
        self._login(auth_api, test_user)

        rows = home_api.list_dict_no_root("EQUIP_AREA").json()
        for row in rows:
            assert row["isCategory"] == 0
            assert row["state"] is None
            assert row["pluginId"] is None
            assert row["sysId"] is None

    @allure.title("设备区域字典保持完整区域名称集合")
    def test_equip_area_dict_keeps_expected_area_name_set(self, auth_api, home_api, test_user):
        """校验设备区域字典仍暴露当前环境的完整区域名称集合。"""
        self._login(auth_api, test_user)

        rows = home_api.list_dict_no_root("EQUIP_AREA").json()
        names = {row["name"] for row in rows}
        assert names == {
            "全区",
            "进线区",
            "主变区",
            "进线高压室",
            "控制室",
            "馈线区",
            "所用变室",
            "电缆夹层",
            "通信机械室",
            "周界围墙",
            "屋顶",
            "27.5kV高压室",
            "其他",
        }
