# -*- coding: utf-8 -*-
"""AMCS 首页字典参考数据更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeDictReferenceContracts:
    """补充校验稳定的 EQUIP_AREA 参考数据。"""

    @allure.title("设备区域字典数量保持为十三项")
    def test_equip_area_dict_count_is_stable(self, auth_api, home_api, test_user):
        """校验当前 EQUIP_AREA 字典仍暴露十三条记录。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        assert len(body) == 13

    @allure.title("设备区域字典关键编码映射保持稳定")
    def test_equip_area_dict_core_code_mapping_is_stable(self, auth_api, home_api, test_user):
        """校验核心 EQUIP_AREA 编码仍映射到预期区域名称。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        area_map = {item["code"]: item["name"] for item in body}
        assert area_map["02"] == "主变区"
        assert area_map["04"] == "控制室"
        assert area_map["10"] == "屋顶"
        assert area_map["12"] == "其他"
