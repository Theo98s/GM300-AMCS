# GM300-AMCS 自动化

本项目参考 `D:\gm\GM300-CAMS` 的目录方式整理，当前主要维护黑盒接口自动化用例，UI / E2E 目录作为后续扩展预留。

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

tests_blackbox_ui/                 # 黑盒 UI / E2E 测试预留目录
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
