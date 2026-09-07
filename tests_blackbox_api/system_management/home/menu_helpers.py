# -*- coding: utf-8 -*-
"""首页菜单测试使用的 AMCS 节点查找辅助函数。"""


def find_node(nodes, node_id):
    """按业务标识查找同级节点，不依赖接口返回顺序。"""
    node = next((item for item in nodes if item.get("id") == node_id), None)
    assert node is not None, f"菜单中未找到节点：{node_id}"
    return node


def amcs_host(init_menu_body):
    """从首页初始化响应中查找 GM300-AMCS 主插件。"""
    return find_node(init_menu_body["data"]["hostMenuList"], "GM300-AMCS")


def amcs_top_modules(init_menu_body):
    """返回 GM300-AMCS 主插件的一级业务模块。"""
    return amcs_host(init_menu_body)["leaf"]


def amcs_tree_root(menu_tree_body):
    """从用户菜单树中查找 GM300-AMCS 根节点。"""
    return find_node(menu_tree_body, "GM300-AMCS")
