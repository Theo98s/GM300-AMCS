# -*- coding: utf-8 -*-
"""图像识别配置接口方法与请求体异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("图像识别配置")
class TestImageRecognitionMethodContractsMore:
    """校验页面、分页、类型、详情和校验接口的方法边界。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除鉴权跳转对方法断言的影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("图像识别配置首页使用 POST 时仍返回完整页面")
    def test_image_recognition_config_post_keeps_html_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验配置首页兼容 POST 并保留分页与导入导出入口。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["config_page_url"],
        )

        assert response.status_code == 200
        assert "<title>图像识别配置首页</title>" in response.text

    @allure.title("图像识别分页接口使用 OPTIONS 时返回空成功响应")
    def test_image_recognition_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验分页预检请求不会执行配置查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["image_recognition"]["page_url"],
        )

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("图像识别类型接口使用 POST 时仍返回类型列表")
    def test_image_recognition_type_post_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验识别类型字典兼容 POST 并保持标准成功包装。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["recognition_type_url"],
        )

        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    @allure.title("图像识别校验接口使用 GET 时返回方法不支持")
    def test_image_recognition_validate_get_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验保存前校验接口拒绝 GET，避免空查询误触发业务逻辑。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["image_recognition"]["validate_url"],
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("图像识别校验收到损坏 JSON 时返回识别项为空提示")
    def test_image_recognition_validate_malformed_json_returns_empty_item_prompt(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录校验接口当前将损坏 JSON 按空配置处理的兼容行为。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["validate_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 1
        assert body["msg"] == "识别项不能为空，请配置识别项！"

    @allure.title("图像识别详情缺少配置标识时返回业务失败")
    def test_image_recognition_detail_missing_id_returns_failure(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少详情主键不会返回任意已有图像识别配置。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["image_recognition"]["detail_url"],
        )

        assert response.status_code == 200
        assert response.json() == {"code": 1000, "msg": "操作失败", "data": "操作失败"}
