# -*- coding: utf-8 -*-
"""监控点查询、写操作与预检请求异常测试。"""
from __future__ import annotations

import allure
import pytest


class TestMonitorMutationAbnormalContractsMore:
    """补充监控点写入类接口在空请求、错误方法和错误请求体下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证异常请求进入监控点业务接口。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_json_parse_error(response):
        """统一校验错误文本请求体触发 JSON 解析失败。"""
        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "Unrecognized token 'not'" in response.text

    @staticmethod
    def _assert_method_not_supported(response, method: str):
        """统一校验错误 HTTP 方法返回 405。"""
        assert response.status_code == 405
        assert f"Request method '{method}' not supported" in response.text

    @allure.title("监控点保存前校验接口空 JSON 返回成功空消息")
    def test_monitor_validate_empty_json_returns_success(self, auth_api, database_api, test_user):
        """校验空对象只做格式校验时不会失败，返回成功但不携带数据。"""
        self._login(auth_api, test_user)

        response = database_api.validate_monitor({})

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == ""
        assert body["data"] is None

    @allure.title("监控点保存前校验接口无请求体时返回 400")
    def test_monitor_validate_missing_body_returns_400(self, auth_api, request_util, config, test_user):
        """校验校验接口缺少 JSON 请求体时明确返回缺失请求体错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_validate_url"],
            json=None,
            allow_redirects=False,
        )

        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "validateMonitor" in response.text

    @allure.title("监控点保存前校验接口文本请求体时返回 JSON 解析错误")
    def test_monitor_validate_plain_text_body_returns_json_parse_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验校验接口接收非 JSON 文本时由框架层返回解析错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_validate_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)

    @allure.title("监控点保存前校验接口使用 GET 方法时返回 405")
    def test_monitor_validate_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点保存前校验只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_validate_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点保存接口空 JSON 返回保存失败")
    def test_monitor_save_empty_json_returns_business_failure(self, auth_api, database_api, test_user):
        """校验空对象保存不会创建脏数据，而是返回保存失败。"""
        self._login(auth_api, test_user)

        response = database_api.save_or_update_monitor({})

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 1
        assert body["message"] == "保存监控点失败！"
        assert body["data"] is None

    @allure.title("监控点保存接口文本请求体时返回 JSON 解析错误")
    def test_monitor_save_plain_text_body_returns_json_parse_error(self, auth_api, request_util, config, test_user):
        """校验保存接口接收非 JSON 文本时不会进入业务保存流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_save_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)

    @allure.title("监控点保存接口使用 GET 方法时返回 405")
    def test_monitor_save_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点保存接口只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_save_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点删除接口使用 GET 方法时返回 405")
    def test_monitor_delete_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点批量删除接口只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_delete_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点删除接口文本请求体时返回 JSON 解析错误")
    def test_monitor_delete_plain_text_body_returns_json_parse_error(self, auth_api, request_util, config, test_user):
        """校验删除接口接收非 JSON 文本时不会进入删除流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_delete_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)


class TestMonitorMutationOptionsMore:
    """校验校验、保存、删除校验及删除接口的预检请求不会写入数据。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保受保护写接口正常接收预检请求。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("monitor_validate_url", "保存前校验", id="validate"),
            pytest.param("monitor_save_url", "保存或修改", id="save"),
            pytest.param("monitor_can_delete_url", "删除前校验", id="can-delete"),
            pytest.param("monitor_delete_url", "批量删除", id="delete"),
        ],
    )
    @allure.title("监控点写接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_mutation_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验预检请求只返回空响应，不执行任何数据写操作。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["database"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""


class TestMonitorQueryAbnormalContractsMore:
    """校验监控点查询接口在错误分页、缺参和方法切换时的实际响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保请求命中业务接口而非登录页。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_monitor_page(response):
        """统一校验监控点列表的分页结果结构。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert isinstance(body, dict)
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @allure.title("监控点列表的 rows 传入非整数时返回参数转换错误")
    def test_monitor_page_rejects_non_integer_rows(self, auth_api, request_util, config, test_user):
        """校验错误的 rows 参数被明确拒绝，避免服务端静默返回错误分页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert '"bad"' in response.text

    @allure.title("监控点列表的 page 传入非整数时返回参数转换错误")
    def test_monitor_page_rejects_non_integer_page(self, auth_api, request_util, config, test_user):
        """校验错误的 page 参数不会被解析为不可预期的页码。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert '"bad"' in response.text

    @allure.title("监控点列表使用 GET 访问时仍返回默认分页数据")
    def test_monitor_page_get_method_keeps_default_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录服务端对 GET 的兼容行为，防止路由改造造成前端列表不可用。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["database"]["monitor_page_url"])

        self._assert_monitor_page(response)

    @allure.title("联动关联设备接口使用 POST 访问时仍返回设备列表")
    def test_related_equip_list_post_method_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验关联设备只读接口对 POST 的兼容响应，列表结构保持稳定。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_related_equip_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("联动摄像机接口缺少设备参数时返回默认数据包装")
    def test_camera_list_without_equip_id_returns_default_data_wrapper(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少 equipId 时接口返回标准业务包装，而不是服务端异常。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_camera_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "成功"
        assert isinstance(body["data"], list)
        if body["data"]:
            assert set(body["data"][0]) >= {"equipId", "cameraName", "channelNo"}

    @allure.title("联动预置位接口缺少参数时返回空列表")
    def test_preset_list_without_query_params_returns_empty_list(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少摄像机和关联设备标识时预置位查询可安全退化为空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == []
