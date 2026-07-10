# -*- coding: utf-8 -*-
"""图像识别配置接口异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("图像识别配置")
class TestImageRecognitionAbnormalContracts:
    """覆盖错误分页、无效详情、空校验和损坏 JSON 场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保异常响应来自业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("图像识别 rows 传入非整数时返回校验错误")
    def test_image_recognition_page_rejects_invalid_rows(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误分页大小被查询对象参数校验拒绝。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "Validation failed" in response.text
        assert "imageRecognitionConfigQuery" in response.text

    @allure.title("图像识别 page 传入非整数时返回校验错误")
    def test_image_recognition_page_rejects_invalid_page(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误页码不会被静默转换为默认页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "Validation failed" in response.text

    @allure.title("不存在的图像识别配置详情返回业务失败")
    def test_image_recognition_unknown_detail_returns_failure(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验无效配置标识不会返回其他配置详情。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.get_detail("NO_SUCH_CONFIG_ID").json()

        assert body == {"code": 1000, "msg": "操作失败", "data": "操作失败"}

    @allure.title("空图像识别配置校验提示识别项不能为空")
    def test_image_recognition_validate_empty_payload_returns_prompt(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验空配置不会进入保存流程，并返回明确业务提示。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.validate_config({}).json()

        assert body["code"] == 1
        assert body["msg"] == "识别项不能为空，请配置识别项！"
        assert body["data"] is None

    @allure.title("预置位查询收到损坏 JSON 时返回解析错误")
    def test_image_recognition_preset_rejects_malformed_json(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验无法解析的级联请求体被明确拒绝而不是返回错误数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["preset_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "JsonParseException" in response.text
