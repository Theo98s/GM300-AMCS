# GM300-AMCS 自动化

本项目参考 `D:\gm\GM300-CAMS` 的目录方式整理，维护黑盒接口自动化及独立的浏览器 UI 测试。

## 目录结构

```text
config/
  config.yaml                      # 稳定接口路径、默认超时、SSL 校验等公共配置
  test_config.example.yaml          # 访问地址、账号、线路、所亭等环境配置模板

src/
  amcs/                            # 项目公共代码
    api/
      core/                        # 登录、认证等基础能力
      platform/                    # 首页、菜单、系统、GIS 等平台接口
      modules/                     # 视频、巡检、报警、历史、RDAC、基础数据库
    common/                        # 通用请求工具

tests_blackbox_api/                # 黑盒接口测试
  conftest.py                      # 夹具、登录会话、配置合并、Allure 编号
  auth/
  alarm_event/
  base_data/
  gis/
  history_records/
  patrol_management/
  rdac/
  system_management/
  video_monitor/

tests_blackbox_ui/                 # 黑盒 UI 测试：登录、巡检点位查询
  conftest.py
  pages/

artifacts/
  reverse_engineering/             # 页面逆向、路由探测等分析产物

reports/                           # Allure 结果与报告输出目录
```

## 外部环境配置

`config/config.yaml` 只放接口路径等相对稳定的内容；访问地址、账号、线路、所亭、RDAC 协议等会随环境变化的内容放到外部测试配置中。

默认会读取 `config/test_config.example.yaml`，如果要测试其他环境，复制一份本地配置并通过环境变量指定：

```powershell
Copy-Item config\test_config.example.yaml config\test_config.local.yaml
$env:AMCS_CONFIG_FILE = "D:\gm\GM300-AMCS\config\test_config.local.yaml"
pytest
```

也可以指向任意环境文件：

```powershell
$env:AMCS_CONFIG_FILE = "D:\gm\envs\amcs-test.yaml"
pytest tests_blackbox_api
```

本地配置文件 `config/test_config.local.yaml` 已加入 `.gitignore`，可以放心写入不同环境的地址、账号和所亭线路信息。

## 当前覆盖

- 登录认证
- 首页、菜单、插件
- 系统接口
- GIS
- 视频监控
- 巡检管理
- 报警事件
- 历史记录
- RDAC
- 基础数据库

## 运行方式

UI 测试单独安装并运行，默认 `pytest` 仍只运行接口用例：

```powershell
.env\Scripts\python.exe -m pip install -r requirements-ui.txt
.env\Scripts\python.exe -m playwright install chromium
.env\Scripts\python.exe -m pytest tests_blackbox_ui --alluredir reports/ui-results
```

已有 Edge 时可跳过 Chromium 下载，直接执行：

```powershell
.env\Scripts\python.exe -m pytest tests_blackbox_ui --ui-channel msedge --alluredir reports/ui-results
```

UI 同样读取 `AMCS_CONFIG_FILE` 指定的环境文件。可在该文件添加以下可选配置：

```yaml
ui:
  headless: false  # 显示浏览器窗口；不配置时默认无界面运行
  timeout_ms: 15000  # 页面操作与响应等待超时
  # channel: msedge  # 可选：使用已安装的 Edge 浏览器
```

首批 UI 用例通过真实登录和可见输入框操作，覆盖巡检点位设备名称、摄像机名称、
预置位名称筛选、空结果、组合查询和清空恢复；同时核对响应中的每条记录与页面展示。
当前列表校验覆盖返回的首页，尚未覆盖全部分页；列表恢复用例需在数据稳定的环境运行。
失败截图附加到 Allure 结果，可能包含业务数据，请按测试环境权限管理报告。

```powershell
cd D:\gm\GM300-AMCS
pip install -r requirements.txt
pytest
```

生成 Allure 原始结果：

```powershell
python run.py
```

如果本机安装了 Allure CLI，会继续生成 `reports/allure-report/`；未安装时会保留 `reports/allure-results/`。
