# GM300-AMCS 自动化

当前先按 `GM700` 的风格落了一版 AMCS 接口自动化骨架，采用：

- `pytest`
- `requests.Session`
- `allure`
- `yaml` 配置化环境与账号

## 目录

- `config/`：环境地址、接口路径、测试账号
- `common/`：通用请求工具
- `api/`：接口封装
- `testcase/`：测试用例

## 首批覆盖

- 登录页获取 `CSRFToken`
- 正常登录
- 错误密码登录失败
- 系统 logo 公共接口
- 告警数量接口登录态校验
- 时间戳接口登录态校验
- 系统健康检查接口

## 运行

```bash
pip install -r requirements.txt
pytest
```

生成 Allure 报告：

```bash
python run.py
```
