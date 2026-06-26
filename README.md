# GM300-AMCS 自动化

项目已经整理为“源码分层 + 白盒测试分层 + UI 预留骨架”的结构，根目录只保留需要长期维护的内容，临时分析产物和测试报告也已经归档。

## 目录结构

```text
GM300-AMCS/
├─ src/
│  └─ amcs/
│     ├─ api/
│     │  ├─ core/              # 登录、认证等基础能力
│     │  ├─ platform/          # 首页、菜单、系统、GIS 等平台公共能力
│     │  └─ modules/           # 视频、巡检、报警、历史、RDAC、基础数据库
│     └─ common/               # 通用请求工具与公共能力
├─ tests_whitebox/
│  ├─ conftest.py              # 白盒测试公共夹具、账号、Allure 编号
│  └─ cases/
│     ├─ core/                 # 认证登录等基础能力
│     ├─ platform/             # 首页、菜单、系统、GIS 等平台能力
│     └─ modules/              # 业务模块接口测试
├─ tests_blackbox_ui/
│  ├─ conftest.py              # UI 黑盒测试公共夹具预留
│  └─ pages/                   # Page Object 预留目录
├─ config/                     # 环境地址、接口路径、测试账号
├─ artifacts/
│  └─ reverse_engineering/     # 页面逆向、路由探测等分析产物
├─ reports/                    # Allure 结果与报告输出目录
├─ pytest.ini
├─ run.py
└─ requirements.txt
```

## 当前覆盖

- 认证登录
- 首页、菜单、插件
- 系统接口
- GIS
- 视频监控
- 巡检管理
- 报警事件
- 历史记录
- RDAC
- 基础数据库

## 运行

```bash
pip install -r requirements.txt
pytest
```

生成 Allure 报告：

```bash
python run.py
```

报告输出位置：

```text
reports/
├─ allure-results/
└─ allure-report/
```
