# -*- coding: utf-8 -*-
"""基础数据导出与联动辅助查询异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestDatabaseExportAbnormalContractsMore:
    """补充模板下载、导出和联动辅助查询的异常参数行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证异常断言不受权限拦截干扰。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_empty_binary_response(response):
        """统一校验服务端对未知导出资源返回空响应体。"""
        assert response.status_code == 200
        assert response.content == b""
        assert response.headers.get("Content-Type") is None
        assert response.headers.get("Content-Disposition") is None

    @allure.title("模板下载接口缺少 templateName 时返回 400")
    def test_template_download_missing_template_name_returns_400(self, auth_api, request_util, config, test_user):
        """校验模板下载缺少必填模板名时返回明确参数错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_template_download_url"],
            allow_redirects=False,
        )

        assert response.status_code == 400
        assert "Required String parameter 'templateName' is not present" in response.text

    @allure.title("模板下载接口未知模板名时返回空响应")
    def test_template_download_unknown_template_returns_empty_response(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """校验不存在的模板文件不会返回错误页，而是返回 200 空体。"""
        self._login(auth_api, test_user)

        response = database_api.download_template("NO_SUCH_TEMPLATE", "bad.xls")

        self._assert_empty_binary_response(response)

    @allure.title("Excel 导出接口缺少导出参数时返回空响应")
    def test_excel_export_missing_params_returns_empty_response(self, auth_api, request_util, config, test_user):
        """校验导出接口缺少模板参数时保持 200 空体契约。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_excel_export_url"],
            allow_redirects=False,
        )

        self._assert_empty_binary_response(response)

    @allure.title("Excel 导出接口未知模板名时返回空响应")
    def test_excel_export_unknown_template_returns_empty_response(self, auth_api, database_api, test_user):
        """校验未知导出模板不会生成文件，也不会返回错误页。"""
        self._login(auth_api, test_user)

        response = database_api.export_excel("NO_SUCH_EXPORT", "bad.xls")

        self._assert_empty_binary_response(response)

    @allure.title("监控点 XML 导出接口使用 GET 方法时返回 405")
    def test_monitor_xml_export_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验 XML 点表导出只接受 POST 方法，GET 会明确返回方法不支持。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_xml_export_url"],
            allow_redirects=False,
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("联动摄像机查询使用未知设备 ID 时返回空数据")
    def test_linkage_camera_unknown_equip_id_returns_empty_data(self, auth_api, database_api, test_user):
        """校验不存在的关联设备 ID 不会报错，而是返回成功空列表。"""
        self._login(auth_api, test_user)

        response = database_api.query_camera_list("NO_SUCH_EQUIP_001")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "成功"
        assert body["data"] == []

    @allure.title("联动预置位查询缺少参数时返回空列表")
    def test_linkage_preset_missing_params_returns_empty_list(self, auth_api, request_util, config, test_user):
        """校验预置位辅助查询缺少摄像机和关联设备参数时返回空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert response.json() == []

    @allure.title("联动预置位查询使用未知参数时返回空列表")
    def test_linkage_preset_unknown_params_returns_empty_list(self, auth_api, database_api, test_user):
        """校验不存在的摄像机和设备组合不会返回脏数据。"""
        self._login(auth_api, test_user)

        response = database_api.query_preset_list("NO_SUCH_CAMERA_001", "NO_SUCH_EQUIP_001")

        assert response.status_code == 200
        assert response.json() == []
