# -*- coding: utf-8 -*-
"""监控点查询、写操作及 HTTP 方法异常测试。"""
from __future__ import annotations

from pathlib import Path
import tempfile
import allure
import pytest


class TestDatabaseAbnormalContractsMore:
    """补充校验基础数据库对空参数、非法 ID 和错误文件的兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证异常请求运行在已认证会话下。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("监控点删除前校验在空请求体下返回 400")
    def test_monitor_can_delete_empty_body_returns_http_400(self, auth_api, database_api, test_user):
        """校验删除前校验接口在空 ID 集合下不会伪成功，而是明确返回缺少请求体。"""
        self._login(auth_api, test_user)

        response = database_api.can_delete_monitor([])
        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "checkCanDeleteMonitor" in response.text

    @allure.title("监控点删除接口在空数组下保持幂等成功")
    def test_monitor_delete_empty_id_list_keeps_idempotent_success(self, auth_api, database_api, test_user):
        """校验批量删除接口在空数组下仍返回成功结果，便于前端直接透传空选择。"""
        self._login(auth_api, test_user)

        response = database_api.delete_monitor_by_ids([])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "操作成功!"
        assert body["data"] is None

    @allure.title("监控点导入接口在上传非 Excel 文件时返回结构化校验错误")
    def test_monitor_import_rejects_non_excel_file_with_validation_message(self, auth_api, database_api, test_user):
        """校验导入接口在上传文本文件时不会 500，而是返回结构化导入失败提示。"""
        self._login(auth_api, test_user)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write("not excel")
            temp_path = temp_file.name

        try:
            response = database_api.import_excel("monitorImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入出错:数据验证失败"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            assert "InputStream" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("监控点编辑页在非法 ID 下仍返回标准页面壳")
    def test_monitor_edit_page_invalid_id_still_returns_standard_html_shell(self, auth_api, database_api, test_user):
        """校验编辑页在非法监控点 ID 下仍能返回标准编辑页 HTML，而不是 500 错页。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_edit_page("bad-id")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert 'function appendToken()' in response.text


class TestDatabaseMethodBoundariesMore:
    """校验页面、导出和联动辅助接口使用非默认方法时的实际响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，避免接口响应被登录页替代。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_empty_success(response):
        """统一校验方法探测接口返回成功状态和空响应体。"""
        assert response.status_code == 200
        assert response.content == b""

    @allure.title("监控点列表接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_page_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验浏览器预检请求不会触发分页查询或服务端错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_page_url"],
        )

        self._assert_empty_success(response)

    @allure.title("监控点编辑页面使用 POST 时仍返回标准页面")
    def test_monitor_edit_page_post_method_keeps_html_shell(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验使用 POST 打开无效监控点编辑页时仍返回可渲染页面骨架。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_edit_page_url"],
            data={"id": "NO_SUCH_MONITOR_ID"},
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert "var csrftoken" in response.text

    @allure.title("监控点导入页面使用 POST 时仍返回完整页面")
    def test_monitor_import_page_post_method_keeps_html_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验导入页面兼容 POST 访问并保留页面标题和核心脚本。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_import_page_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>导入页面</title>" in response.text
        assert "function importExcel" in response.text

    @allure.title("模板下载接口使用 POST 时返回空成功响应")
    def test_template_download_post_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录模板下载接口对 POST 的空响应行为，避免误判为文件下载成功。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_template_download_url"],
            data={"templateName": "monitor", "downloadName": "monitor"},
        )

        self._assert_empty_success(response)

    @allure.title("Excel 导出接口使用 POST 时返回空成功响应")
    def test_excel_export_post_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验导出接口错误使用 POST 时不会返回伪造的 Excel 文件内容。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_excel_export_url"],
            data={"templateName": "monitor", "downloadName": "monitor"},
        )

        self._assert_empty_success(response)

    @allure.title("联动关联设备接口使用 OPTIONS 时返回空成功响应")
    def test_related_equip_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验关联设备查询支持浏览器预检且不会返回业务数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_related_equip_url"],
        )

        self._assert_empty_success(response)

    @allure.title("联动摄像机接口使用 POST 时返回方法不支持")
    def test_camera_list_post_method_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验摄像机只读接口严格限制为约定方法，错误方法不执行查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_camera_list_url"],
        )

        assert response.status_code == 405
        assert "Request method 'POST' not supported" in response.text

    @allure.title("联动预置位接口使用 POST 且缺参时返回空列表")
    def test_preset_list_post_without_params_returns_empty_list(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验预置位查询兼容 POST，缺少设备标识时安全退化为空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == []

    @allure.title("监控点 XML 导出接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_xml_export_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验 XML 导出预检请求不会触发文件生成和下载。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_xml_export_url"],
        )

        self._assert_empty_success(response)


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
