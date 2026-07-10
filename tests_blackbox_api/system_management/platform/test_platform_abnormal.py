# -*- coding: utf-8 -*-
"""平台与业务接口的访问控制、损坏请求体和请求方法异常测试。"""
from __future__ import annotations

import allure
import pytest

class TestAccessControlContracts:
    """校验匿名用户应被重定向的接口契约。"""

    @staticmethod
    def _assert_redirects_to_login(response):
        """断言受保护接口会把匿名用户重定向到登录页。"""
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("首页菜单初始化接口未登录时跳转登录页")
    def test_init_menu_requires_login(self, request_util, config):
        """校验首页菜单初始化接口受登录保护。"""
        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("用户菜单树接口未登录时跳转登录页")
    def test_user_menu_tree_requires_login(self, request_util, config):
        """校验用户菜单树接口受登录保护。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("通用字典接口未登录时跳转登录页")
    def test_dict_list_requires_login(self, request_util, config):
        """校验字典接口在未登录前受保护。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("首页菜单初始化接口默认行为会落到登录页 HTML")
    def test_init_menu_default_request_returns_login_html(self, request_util, config):
        """校验未控制 allow_redirects 时，initMenu 最终会落到登录页 HTML。"""
        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text

    @allure.title("匿名访问受保护接口时仍暴露登录提交地址")
    def test_default_anonymous_request_login_html_contains_submit_route(self, request_util, config):
        """校验解析后的登录页 HTML 仍包含 ajax 登录提交地址，便于用户恢复登录。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "/sso/ajaxcheck" in response.text
        assert 'name="password"' in response.text

    @allure.title("用户菜单树接口默认行为会落到登录页 HTML")
    def test_user_menu_tree_default_request_returns_login_html(self, request_util, config):
        """校验未登录访问 getUserMenuTree 时会落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text

    @allure.title("设备区域字典接口默认行为会落到登录页 HTML")
    def test_dict_list_default_request_returns_login_html(self, request_util, config):
        """校验未登录访问字典接口时会落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text

class TestAccessControlContractsExtra:
    """补充校验匿名请求落到登录页时的契约。"""

    @allure.title("匿名菜单树请求落地登录页标题")
    def test_anonymous_menu_tree_request_resolves_to_login_page_title(self, request_util, config):
        """校验匿名菜单树请求会落到带标题标签的登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "<title>" in response.text.lower()
        assert "/sso/ajaxcheck" in response.text

    @allure.title("匿名字典请求返回登录页表单字段")
    def test_anonymous_dict_request_resolves_to_login_form_fields(self, request_util, config):
        """校验匿名字典请求会落到仍包含账号和密码输入框的登录页 HTML。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
        )

        assert response.status_code == 200
        assert 'name="account"' in response.text
        assert 'name="password"' in response.text

class TestAccessExceptionContractsMore:
    """补充校验需要登录和无需登录接口之间的当前差异化行为。"""

    @allure.title("匿名访问报警记录接口会跳转登录页")
    def test_anonymous_alarm_record_request_redirects_to_login(self, request_util, config):
        """校验报警记录接口仍受登录态保护。"""
        response = request_util.send_request(
            "post",
            config["alarm"]["alarm_record_page_url"],
            json={},
            allow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/amcs/login"

    @allure.title("匿名访问监控点列表接口仍可返回公开 JSON")
    def test_anonymous_monitor_page_request_still_returns_public_json(self, request_util, config):
        """校验监控点列表接口当前仍允许匿名访问，并返回标准分页 JSON。"""
        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": 1, "rows": 5},
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")

        body = response.json()
        assert isinstance(body["rows"], list)
        assert body["total"] >= len(body["rows"])
        assert len(body["rows"]) > 0

    @allure.title("匿名访问监控点导入页仍可返回公开 HTML")
    def test_anonymous_monitor_import_page_still_returns_public_html(self, request_util, config):
        """校验监控点导入页当前仍允许匿名访问，并返回标准导入页 HTML。"""
        response = request_util.send_request(
            "get",
            config["database"]["monitor_import_page_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>导入页面</title>" in response.text
        assert "monitorImport.xls" in response.text

    @allure.title("匿名访问非法监控点编辑页仍可返回公开 HTML 壳")
    def test_anonymous_monitor_edit_page_with_invalid_id_still_returns_public_html_shell(self, request_util, config):
        """校验监控点编辑页在匿名且非法 ID 下当前仍返回标准编辑页 HTML 壳。"""
        response = request_util.send_request(
            "get",
            config["database"]["monitor_edit_page_url"],
            params={"id": "bad-id"},
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert 'function appendToken()' in response.text

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

class TestPlatformMalformedPayloadContractsMore:
    """校验平台初始化、菜单和插件查询对损坏 JSON 的兼容行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求命中平台业务接口。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _malformed_json_request(request_util, url):
        """发送声明为 JSON 但内容无法解析的请求。"""
        return request_util.send_request(
            "post",
            url,
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

    @allure.title("首页初始化接口收到损坏 JSON 时仍返回菜单数据")
    def test_home_init_menu_malformed_json_keeps_success_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏请求体不会阻断首页菜单的默认初始化流程。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["home"]["init_menu_url"],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"]) == {"moduleMenu", "otherMenuList", "hostMenuList"}

    @allure.title("用户菜单树接口收到损坏 JSON 时仍返回菜单列表")
    def test_user_menu_tree_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验用户菜单树忽略损坏请求体并保持列表响应。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("插件查询接口收到损坏 JSON 时仍返回插件列表")
    def test_plugin_find_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验插件查询不会因无法解析的附加请求体产生服务端错误。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["plugin"]["find_plugin_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

class TestPlatformOptionsContractsMore:
    """校验首页、字典、菜单和插件接口的浏览器预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入平台业务路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("url_factory", "case_name"),
        [
            pytest.param(lambda config: config["home"]["init_menu_url"], "首页初始化", id="home"),
            pytest.param(
                lambda config: f'{config["home"]["dict_list_url_prefix"]}/equipArea',
                "设备区域字典",
                id="dict",
            ),
            pytest.param(lambda config: config["menu"]["user_menu_tree_url"], "用户菜单树", id="menu"),
            pytest.param(lambda config: config["plugin"]["find_plugin_url"], "插件查询", id="plugin"),
        ],
    )
    @allure.title("平台查询接口使用 OPTIONS 时返回空成功响应")
    def test_platform_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        url_factory,
        case_name,
    ):
        """逐项校验平台查询预检请求不会返回菜单或字典业务数据。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request("options", url_factory(config))

        assert response.status_code == 200
        assert response.content == b""
