# -*- coding: utf-8 -*-
"""AMCS 首页字典补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeDictContractsExtra:
    """补充校验首页模块使用的公共字典返回契约。"""

    @allure.title("设备区域字典编码保持唯一")
    def test_equip_area_dict_codes_are_unique(self, auth_api, home_api, test_user):
        """校验 EQUIP_AREA 字典编码保持唯一，便于下拉展示和筛选。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        codes = [item["code"] for item in body]
        assert len(codes) == len(set(codes))

    @allure.title("设备区域字典项保持 text 与 name 一致且 typekey 正确")
    def test_equip_area_dict_entries_keep_text_name_and_typekey_contract(self, auth_api, home_api, test_user):
        """校验 EQUIP_AREA 字典项的展示字段和 typekey 保持一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        for item in body:
            assert item["text"] == item["name"]
            assert item["typekey"] == "EQUIP_AREA"
            assert item["name"]
