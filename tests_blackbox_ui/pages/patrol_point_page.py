"""巡检点位列表的可见控件操作及逐行展示校验。"""
from urllib.parse import urlsplit
import re
from playwright.sync_api import expect


class PatrolPointPage:
    """操作 EasyUI 实际渲染的输入框，不调用页面脚本代替点击。"""

    fields = {"equipName": "设备名称", "cameraName": "摄像机名称", "keyword": "预置位名称"}

    def __init__(self, page):
        """绑定当前页面和表格数据行。"""
        self.page = page
        self.rows = page.locator(".datagrid-view2 .datagrid-body tr.datagrid-row")

    def change_page(self, action):
        """点击主表分页按钮，并等待对应请求及表格更新。"""
        button = self.page.locator(f'.datagrid-pager a:has(.pagination-{action})')
        expect(button).not_to_have_class(re.compile(r".*l-btn-disabled.*"))
        with self.page.expect_response(self.is_list_response) as pending:
            button.click()
        return self.assert_table(pending.value)

    def change_page_size(self, size):
        """通过可见下拉框切换每页条数。"""
        with self.page.expect_response(self.is_list_response) as pending:
            self.page.locator(".datagrid-pager select.pagination-page-list").select_option(str(size))
        return self.assert_table(pending.value)

    def all_filtered_rows(self, first_page):
        """遍历筛选结果全部分页，校验记录无重复且条数与总数一致。"""
        result = list(first_page["rows"])
        expected_total = first_page["total"]
        seen = {row["id"] for row in result}
        assert len(seen) == len(result), "首页出现重复记录"
        while len(result) < expected_total:
            body = self.change_page("next")
            assert body["total"] == expected_total, "遍历期间总数发生变化，请在稳定环境复测"
            assert body["rows"], "尚有未读取数据但下一页为空"
            ids = [row["id"] for row in body["rows"]]
            assert len(set(ids)) == len(ids) and not seen.intersection(ids), "分页返回重复记录"
            seen.update(ids)
            result.extend(body["rows"])
        assert len(result) == expected_total
        return result

    def open_import(self):
        """通过工具栏打开导入弹窗，不选择或上传文件。"""
        self.page.locator('#areaToolbar a[onclick="showImportDialog();"]').click()
        dialog = self.page.locator("#import_dialog")
        expect(dialog).to_be_visible()
        return dialog

    @staticmethod
    def is_list_response(response):
        """只捕获目标分页请求，排除后台轮询。"""
        return urlsplit(response.url).path == "/amcs/monitorArea/findPage" and response.request.method == "POST"

    def open(self):
        """等待页面初始查询完成并核对表格。"""
        with self.page.expect_response(self.is_list_response) as pending:
            self.page.goto("/amcs/monitorArea/index")
        return self.assert_table(pending.value)

    def search(self, **filters):
        """清空旧条件，填写新条件并点击过滤按钮。"""
        for field, placeholder in self.fields.items():
            self.page.get_by_placeholder(placeholder, exact=True).fill(filters.get(field, ""))
        with self.page.expect_response(self.is_list_response) as pending:
            self.page.locator('#conditionForm a[onclick="queryData()"]').click()
        return self.assert_table(pending.value)

    def assert_table(self, response):
        """逐行比对页面和响应；空结果必须同时清空表格。"""
        assert response.status == 200
        body = response.json()
        assert isinstance(body["total"], int)
        assert body["total"] >= len(body["rows"])
        expect(self.rows).to_have_count(len(body["rows"]))
        for index, row in enumerate(body["rows"]):
            for field in ("equipName", "cameraName", "presetName"):
                cell = self.rows.nth(index).locator(f'td[field="{field}"] .datagrid-cell')
                # 设备名称缺失时，页面格式化函数会显示占位符。
                value = row.get(field) or ("--" if field == "equipName" else "")
                expect(cell).to_have_text(str(value))
        if not body["rows"]:
            assert body["total"] == 0, (
                f"查询返回空页但总数为 {body['total']}，请检查是否沿用旧页码；"
                f"请求参数：{response.request.post_data}"
            )
        return body
