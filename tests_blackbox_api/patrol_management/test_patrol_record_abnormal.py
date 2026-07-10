# -*- coding: utf-8 -*-
"""巡检记录接口异常参数与方法边界测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检记录")
class TestPatrolRecordAbnormal:
    """覆盖错误分页、无效记录、空详情和预检请求场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("巡检记录 rows 传入非整数时返回参数错误")
    def test_patrol_record_page_rejects_invalid_rows(self, auth_api, request_util, config, test_user):
        """校验错误分页大小被明确拒绝。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_record"]["page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("巡检记录 page 传入非整数时返回参数错误")
    def test_patrol_record_page_rejects_invalid_page(self, auth_api, request_util, config, test_user):
        """校验错误页码不会被静默转换为默认页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol_record"]["page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "NumberFormatException" in response.text

    @allure.title("不存在的巡检记录详情仍返回标准页面骨架")
    def test_patrol_record_unknown_detail_keeps_html_shell(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验无效记录标识不会导致详情页面服务端异常。"""
        self._login(auth_api, test_user)

        response = patrol_record_api.get_detail_page("NO_SUCH_RECORD_ID")

        assert response.status_code == 200
        assert "<title>巡检记录详情</title>" in response.text
        assert "/amcs/patrol/record/findPatrolRecordById" in response.text

    @allure.title("不存在的巡检记录主信息返回空响应体")
    def test_patrol_record_unknown_record_returns_empty_body(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验无效主键不会返回其他巡检记录内容。"""
        self._login(auth_api, test_user)

        response = patrol_record_api.get_record("NO_SUCH_RECORD_ID")

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("不存在的巡检记录返回空明细分页")
    def test_patrol_record_unknown_record_returns_empty_details(
        self,
        auth_api,
        patrol_record_api,
        test_user,
    ):
        """校验无效记录标识不会命中其他任务的点位明细。"""
        self._login(auth_api, test_user)

        body = patrol_record_api.list_record_details("NO_SUCH_RECORD_ID").json()

        assert body == {"total": 0, "rows": []}

    @allure.title("巡检记录列表使用 GET 时仍返回分页数据")
    def test_patrol_record_page_get_keeps_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验巡检记录列表兼容 GET 并遵守分页大小。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["patrol_record"]["page_url"],
            params={"page": 1, "rows": 2},
        )

        body = response.json()
        assert response.status_code == 200
        assert isinstance(body["total"], int)
        assert len(body["rows"]) <= 2

    @allure.title("巡检记录列表使用 OPTIONS 时返回空成功响应")
    def test_patrol_record_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验巡检记录分页预检请求不会执行查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("options", config["patrol_record"]["page_url"])

        assert response.status_code == 200
        assert response.content == b""
