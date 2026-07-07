# GM300-AMCS 自动化

本项目参考 `D:\gm\GM300-CAMS` 的目录方式整理，当前主要维护黑盒接口自动化用例，UI / E2E 目录作为后续扩展预留。

## 目录结构

```text
config/
  config.yaml                 # 环境地址、接口路径
  test.yaml                   # 测试账号

src/
  amcs/                       # 项目公共代码
    api/
      core/                   # 登录、认证等基础能力
      platform/               # 首页、菜单、系统、GIS 等平台接口
      modules/                # 视频、巡检、报警、历史、RDAC、基础数据库
    common/                   # 通用请求工具

tests_blackbox_api/           # 黑盒接口测试
  conftest.py
  auth/
  alarm_event/
  base_data/
  gis/
  history_records/
  patrol_management/
  rdac/
  system_management/
  video_monitor/

tests_blackbox_ui/            # 黑盒 UI / E2E 测试预留目录
  conftest.py
  pages/

artifacts/
  reverse_engineering/        # 页面逆向、路由探测等分析产物

reports/                      # Allure 结果与报告输出目录
```

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
