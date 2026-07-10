# -*- coding: utf-8 -*-
"""设备管理异常参数与方法边界测试。"""
from __future__ import annotations

import allure


class TestEquipmentAbnormalContracts:
    """覆盖错误分页、删除前缺参和不存在标识的幂等处理。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("设备列表 rows 传入非整数时返回参数错误")
    def test_equipment_page_rejects_invalid_rows(self, auth_api, request_util, config, test_user):
        """校验错误分页大小被明确拒绝。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["equipment"]["page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("设备列表 page 传入非整数时返回参数错误")
    def test_equipment_page_rejects_invalid_page(self, auth_api, request_util, config, test_user):
        """校验错误页码不会被静默转换为默认页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["equipment"]["page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("设备删除前校验缺少请求体时返回 400")
    def test_equipment_can_delete_requires_body(self, auth_api, request_util, config, test_user):
        """校验空请求不会误进入设备依赖检查流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["equipment"]["can_delete_url"])

        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "couldDelete" in response.text

    @allure.title("不存在的设备删除前校验返回可以删除")
    def test_equipment_unknown_row_is_safe_to_delete(self, auth_api, equipment_api, test_user):
        """校验不存在设备不会产生虚假的监控点或业务依赖。"""
        self._login(auth_api, test_user)

        body = equipment_api.can_delete(
            [{"id": "NO_SUCH_EQUIPMENT_ID", "equipName": "NO_SUCH_EQUIPMENT"}]
        ).json()

        assert body == {
            "status": 0,
            "message": "操作成功",
            "data": {"msg": "可以删除", "code": 0},
        }

    @allure.title("删除不存在的设备保持幂等成功")
    def test_equipment_delete_unknown_id_is_idempotent(self, auth_api, equipment_api, test_user):
        """校验重复清理或无效设备标识不会导致接口报错。"""
        self._login(auth_api, test_user)

        response = equipment_api.delete_by_ids(["NO_SUCH_EQUIPMENT_ID"])

        assert response.status_code == 200
        assert response.json() == {"status": 0, "message": "操作成功", "data": None}


class TestEquipmentMethodContractsMore:
    """校验首页、分页和类型树接口使用其他方法时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求进入设备管理路由。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("设备列表使用 GET 时仍返回分页数据")
    def test_equipment_page_get_keeps_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备列表兼容 GET 并遵守分页大小。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["equipment"]["page_url"],
            params={"page": 1, "rows": 2},
        )

        body = response.json()
        assert response.status_code == 200
        assert isinstance(body["total"], int)
        assert len(body["rows"]) <= 2

    @allure.title("设备列表使用 OPTIONS 时返回空成功响应")
    def test_equipment_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备分页预检请求不会执行查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("options", config["equipment"]["page_url"])

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("设备类型树使用 POST 时仍返回节点列表")
    def test_equipment_type_tree_post_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备类型树兼容 POST 并保持层级节点响应。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["equipment"]["type_tree_url"])

        assert response.status_code == 200
        assert isinstance(response.json(), list)
