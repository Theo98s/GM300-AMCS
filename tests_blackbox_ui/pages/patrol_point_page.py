"""巡检点位列表的可见控件操作及逐行展示校验。"""
from urllib.parse import urlsplit
from playwright.sync_api import expect


class PatrolPointPage:
    """操作 EasyUI 实际渲染的输入框，不调用页面脚本代替点击。"""

    fields = {"equipName": "设备名称", "cameraName": "摄像机名称", "keyword": "预置位名称"}

    def __init__(self, page):
        """绑定当前页面和表格数据行。"""
        self.page = page
        self.rows = page.locator(".datagrid-view2 .datagrid-body tr.datagrid-row")

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
                expect(cell).to_have_text(str(row.get(field) or ""))
        if not body["rows"]:
            assert body["total"] == 0, "空首页与总数不一致"
        return body
