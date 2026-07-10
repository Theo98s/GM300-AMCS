# -*- coding: utf-8 -*-
"""首页与字典接口异常访问契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理-首页")
class TestHomeAbnormalContractsMore:
    """补充首页菜单和字典接口在异常参数下的稳定性校验。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证校验的是业务接口返回。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_init_menu_success(response):
        """统一校验首页菜单初始化接口的成功结构。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"].keys()) >= {"moduleMenu", "otherMenuList", "hostMenuList"}

    @allure.title("首页菜单初始化接口使用 GET 方法时仍返回菜单结构")
    def test_init_menu_get_method_keeps_success_contract(self, auth_api, request_util, config, test_user):
        """校验首页菜单接口对 GET 方式保持兼容，避免前端调用方式变化导致失败。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["home"]["init_menu_url"])

        self._assert_init_menu_success(response)

    @allure.title("首页菜单初始化接口接收无关 JSON 时仍返回菜单结构")
    def test_init_menu_unknown_json_keeps_success_contract(self, auth_api, request_util, config, test_user):
        """校验无关 JSON 字段不会影响首页菜单初始化结果。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            json={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_init_menu_success(response)

    @allure.title("字典接口查询不存在类型时返回空列表")
    def test_dict_unknown_type_returns_empty_list(self, auth_api, request_util, config, test_user):
        """校验不存在的字典类型不会报错，而是返回空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/NO_SUCH_DICT_001",
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == []

    @allure.title("字典接口缺少类型路径时返回 404")
    def test_dict_missing_type_path_returns_404(self, auth_api, request_util, config, test_user):
        """校验缺少字典类型路径时服务端明确返回 404。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/",
            allow_redirects=False,
        )

        assert response.status_code == 404
        assert "No message available" in response.text
