# -*- coding: utf-8 -*-
"""系统公共接口、告警数量、时间戳和健康状态运行测试。"""
from __future__ import annotations

import allure

@allure.feature("系统接口")
class TestSystemSmoke:
    """首页公共接口和健康接口的 smoke 校验。"""

    @allure.title("系统 logo 接口可匿名访问")
    def test_sys_logo_public(self, system_api):
        """校验系统 logo 接口未登录也能正常返回配置。"""
        response = system_api.get_sys_logo()

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert "data" in body
        assert set(body["data"].keys()) >= {"sys_logo_a", "sys_logo_b"}

    @allure.title("告警数量接口登录后可访问")
    def test_alarm_count_after_login(self, auth_api, system_api, test_user):
        """校验告警数量接口在已登录会话下可正常访问。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_alarm_count()
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert isinstance(body["data"], int)
        assert body["data"] >= 0

    @allure.title("告警数量接口登录后返回标准成功消息")
    def test_alarm_count_after_login_returns_success_message(self, auth_api, system_api, test_user):
        """校验告警数量接口登录后返回固定成功消息，便于前端统一处理。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_alarm_count()
        body = response.json()

        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"

    @allure.title("告警数量接口未登录时会被拦截")
    def test_alarm_count_requires_login(self, system_api):
        """校验告警数量接口具备登录态保护。"""
        response = system_api.get_alarm_count()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("时间戳接口登录后可访问")
    def test_timestamp_after_login(self, auth_api, system_api, test_user):
        """校验时间戳接口返回正整数时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_timestamp()
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, int)
        assert body > 0

    @allure.title("时间戳接口登录后返回毫秒级时间戳")
    def test_timestamp_after_login_returns_millisecond_precision(self, auth_api, system_api, test_user):
        """校验时间戳接口返回 13 位毫秒级时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_timestamp()
        body = response.json()

        assert isinstance(body, int)
        assert body >= 10**12

    @allure.title("系统健康检查接口返回设备列表")
    def test_health_check_returns_service_data(self, system_api):
        """校验健康检查接口返回基础服务列表结构。"""
        response = system_api.get_health()

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert isinstance(body["data"], list)
        if body["data"]:
            first_item = body["data"][0]
            assert set(first_item.keys()) >= {"name", "serviceUp", "deviceList"}

    @allure.title("时间戳接口连续请求保持非递减")
    def test_timestamp_after_login_is_monotonic(self, auth_api, system_api, test_user):
        """校验同一会话下连续两次获取时间戳时，后一次结果不小于前一次。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        first_response = system_api.get_timestamp()
        second_response = system_api.get_timestamp()

        first_value = first_response.json()
        second_value = second_response.json()
        assert isinstance(first_value, int)
        assert isinstance(second_value, int)
        assert second_value >= first_value

    @allure.title("健康检查 deviceList 字段允许为空或列表")
    def test_health_check_device_list_uses_nullable_list_contract(self, system_api):
        """校验健康检查中的 deviceList 字段保持列表或空值契约，避免前端解析出错。"""
        response = system_api.get_health()
        body = response.json()

        for item in body["data"]:
            assert isinstance(item["serviceUp"], bool)
            assert item["deviceList"] is None or isinstance(item["deviceList"], list)

class TestSystemAccessRuntimeContractsMore:
    """补充校验系统接口在匿名和公共场景下的运行时契约。"""

    @allure.title("匿名访问时间戳接口默认落到登录页 HTML")
    def test_timestamp_default_anonymous_request_returns_login_html(self, request_util, config):
        """校验匿名访问时间戳接口时默认仍落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["system"]["timestamp_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "/sso/ajaxcheck" in response.text
        assert 'id="loginForm"' in response.text

    @allure.title("匿名访问告警数量接口默认落到登录页 HTML")
    def test_alarm_count_default_anonymous_request_returns_login_html(self, request_util, config):
        """校验匿名访问告警数量接口时默认仍落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["system"]["alarm_count_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert 'name="password"' in response.text
        assert 'id="btnLogin"' in response.text

    @allure.title("健康检查公共接口保持精确成功消息与顶层字段")
    def test_health_check_public_keeps_exact_result_keys_and_message(self, system_api):
        """校验健康检查公共接口仍保持精确成功消息和顶层字段。"""
        body = system_api.get_health().json()

        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == "查询成功"
        assert isinstance(body["data"], list)

class TestSystemLogoContracts:
    """补充校验系统公共接口契约。"""

    @allure.title("系统 logo 公共接口返回标准成功消息")
    def test_sys_logo_public_message_is_success_text(self, system_api):
        """校验公共 logo 接口保持标准成功提示文案。"""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"

class TestSystemRuntimeContractsExtra:
    """补充校验系统公共接口和运行时字段。"""

    @allure.title("系统 logo 公共接口默认值保持空字符串")
    def test_sys_logo_public_default_values_are_empty_strings(self, system_api):
        """校验系统 logo 公共接口在当前环境下仍返回空字符串默认值。"""
        body = system_api.get_sys_logo().json()

        assert body["status"] == 0
        assert body["data"]["sys_logo_a"] == ""
        assert body["data"]["sys_logo_b"] == ""

    @allure.title("告警数量接口登录后返回标准三段式结果")
    def test_alarm_count_after_login_keeps_standard_result_keys(self, auth_api, system_api, test_user):
        """校验登录后的告警数量接口仍返回 status、message、data 三段式结果。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = system_api.get_alarm_count().json()
        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert isinstance(body["data"], int)

    @allure.title("时间戳接口登录后返回 13 位毫秒时间戳")
    def test_timestamp_after_login_returns_exact_13_digit_epoch_millis(self, auth_api, system_api, test_user):
        """校验登录后的时间戳接口仍返回 13 位毫秒级 Unix 时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        timestamp = system_api.get_timestamp().json()
        assert isinstance(timestamp, int)
        assert len(str(timestamp)) == 13
