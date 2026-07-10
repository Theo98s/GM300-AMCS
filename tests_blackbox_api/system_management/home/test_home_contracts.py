# -*- coding: utf-8 -*-
"""首页菜单、字典、子节点与响应结构契约测试。"""
from __future__ import annotations

import allure


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


class TestHomeDictContractsExtra:
    """补充校验首页模块使用的公共字典返回契约。"""

    @allure.title("设备区域字典编码保持唯一")
    def test_equip_area_dict_codes_are_unique(self, auth_api, home_api, test_user):
        """校验 EQUIP_AREA 字典编码保持唯一，便于下拉展示和筛选。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        codes = [item["code"] for item in body]
        assert len(codes) == len(set(codes))

    @allure.title("设备区域字典项保持 text 与 name 一致且 typekey 正确")
    def test_equip_area_dict_entries_keep_text_name_and_typekey_contract(self, auth_api, home_api, test_user):
        """校验 EQUIP_AREA 字典项的展示字段和 typekey 保持一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        for item in body:
            assert item["text"] == item["name"]
            assert item["typekey"] == "EQUIP_AREA"
            assert item["name"]


class TestHomeDictReferenceContracts:
    """补充校验稳定的 EQUIP_AREA 参考数据。"""

    @allure.title("设备区域字典数量保持为十三项")
    def test_equip_area_dict_count_is_stable(self, auth_api, home_api, test_user):
        """校验当前 EQUIP_AREA 字典仍暴露十三条记录。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        assert len(body) == 13

    @allure.title("设备区域字典关键编码映射保持稳定")
    def test_equip_area_dict_core_code_mapping_is_stable(self, auth_api, home_api, test_user):
        """校验核心 EQUIP_AREA 编码仍映射到预期区域名称。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        area_map = {item["code"]: item["name"] for item in body}
        assert area_map["02"] == "主变区"
        assert area_map["04"] == "控制室"
        assert area_map["10"] == "屋顶"
        assert area_map["12"] == "其他"


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


class TestHomeMenuContractsMore:
    """补充校验首页菜单顺序与模块形态。"""

    @allure.title("首页顶层模块顺序保持稳定")
    def test_init_menu_top_module_order_is_stable(self, auth_api, home_api, test_user):
        """校验首页一级模块保持预期展示顺序。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.init_menu().json()
        top_texts = [item["text"] for item in body["data"]["hostMenuList"][0]["leaf"]]
        assert top_texts == [
            "首页",
            "视频监控",
            "实时监控",
            "巡检管理",
            "历史记录",
            "基础数据",
            "系统配置",
            "系统管理",
        ]

    @allure.title("首页顶层模块数量保持为八个")
    def test_init_menu_top_module_count_is_stable(self, auth_api, home_api, test_user):
        """校验首页菜单当前仍暴露八个一级模块。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.init_menu().json()
        top_modules = body["data"]["hostMenuList"][0]["leaf"]
        assert len(top_modules) == 8


class TestHomeMenuShapeContracts:
    """补充校验首页菜单的路由与状态模式。"""

    @allure.title("首页顶层模块路由模式保持稳定")
    def test_init_menu_top_module_url_pattern_is_stable(self, auth_api, home_api, test_user):
        """校验首页一层模块保持当前路由模式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        top_modules = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        urls = [item["url"] for item in top_modules]
        assert urls == ["/das/home", None, None, None, "", "", "", ""]

    @allure.title("首页顶层模块状态值保持全启用")
    def test_init_menu_top_module_state_pattern_is_stable(self, auth_api, home_api, test_user):
        """校验首页当前所有一层模块的启用状态值都保持为 1。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        top_modules = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        states = [item["state"] for item in top_modules]
        assert states == [1, 1, 1, 1, 1, 1, 1, 1]


class TestHomePayloadContractsMore:
    """补充校验 init-menu 返回体外层结构。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("init-menu 返回体保留稳定的外层字段")
    def test_init_menu_response_keeps_stable_envelope_fields(self, auth_api, home_api, test_user):
        """校验 init-menu 接口仍返回 status、message 以及预期的 data 子字段。"""
        self._login(auth_api, test_user)

        response = home_api.init_menu()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"].keys()) >= {"moduleMenu", "otherMenuList", "hostMenuList"}
        assert body["data"]["moduleMenu"] is None
        assert body["data"]["otherMenuList"] == []
        assert isinstance(body["data"]["hostMenuList"], list)
        assert len(body["data"]["hostMenuList"]) >= 1

    @allure.title("init-menu 主插件保持欢迎页路由与一级数量对齐")
    def test_init_menu_host_plugin_keeps_basic_identity_and_child_count_alignment(
        self,
        auth_api,
        home_api,
        menu_api,
        test_user,
    ):
        """校验 init-menu 中的主插件在 id、路由和模块数量上与用户菜单树根节点保持对齐。"""
        self._login(auth_api, test_user)

        init_body = home_api.init_menu().json()
        menu_tree = menu_api.get_user_menu_tree().json()

        host_plugin = init_body["data"]["hostMenuList"][0]
        root_node = menu_tree[0]
        assert host_plugin["id"] == "GM300-AMCS"
        assert host_plugin["pageurl"] == "/amcs/index"
        assert host_plugin["pluginKey"] == "GM300-AMCS"
        assert host_plugin["text"] == host_plugin["name"]
        assert len(host_plugin["leaf"]) == len(root_node["children"])
