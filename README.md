<div align="center">

# ControllerOverlay（手柄投影）

**实时游戏手柄可视化桌面悬浮窗 — 按键、摇杆、扳机，一目了然**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078D4?logo=windows11&logoColor=white)](https://www.microsoft.com/windows)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)

</div>

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
  - [前置环境](#前置环境)
  - [克隆项目](#克隆项目)
  - [安装依赖](#安装依赖)
  - [启动运行](#启动运行)
  - [运行测试](#运行测试)
  - [打包构建](#打包构建)
- [项目目录结构](#项目目录结构)
- [架构设计](#架构设计)
- [配置说明](#配置说明)
- [添加新手柄布局](#添加新手柄布局)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

**ControllerOverlay（手柄投影）** 是一款 Windows 桌面工具，在屏幕上显示一个**半透明、始终置顶、鼠标穿透**的悬浮窗，**实时反映游戏手柄的全部输入状态**：按键高亮、摇杆偏移、扳机填充、方向键分区。

适用于手柄测试、游戏直播演示、手柄输入教学、无障碍辅助等场景。连接手柄后自动识别控制器类型并切换对应布局，无需手动配置。

### 为什么选择 ControllerOverlay

| 特性 | ControllerOverlay | 常见游戏内手柄 UI |
|------|-------------------|-------------------|
| 覆盖在任意窗口之上 | 支持（鼠标穿透） | 仅限游戏内 |
| 自动识别手柄型号 | Xbox / DualSense 自动切换 | 固定布局 |
| 透明悬浮窗 | 可调透明度 60%–100% | 不支持 |
| 无需安装 | 单 EXE 或 Python 运行 | 需安装完整软件 |
| 系统托盘控制 | 右键菜单即用 | 多数无托盘模式 |

---

## 核心特性

- **双布局自动适配** — 自动检测 Xbox / DualSense（PS5）控制器，切换对应 SVG 布局；未知手柄回退至 Xbox 布局
- **~120Hz 实时渲染** — QTimer 8ms 轮询 + 脏标记缓存，仅在状态变化时重建 SVG，高效流畅
- **SVG 原生渲染** — 直接操作 SVG XML 元素属性（fill、stroke、transform），通过 `QSvgRenderer` 渲染为 `QPixmap`，无需光栅图片
- **完整输入可视化** — 按键高亮、摇杆位移（translate 变换）、扳机比例填充（QPainter 裁剪）、方向键四象限分区（clipPath 裁剪）
- **热插拔支持** — 手柄连接/断开自动检测，无需重启应用
- **系统托盘交互** — 无任务栏图标，所有操作通过右键托盘菜单完成
- **三套配色主题** — 白色（White）/ 黑色（Black）/ 霓虹（Neon），按键颜色与手柄面键对应（A 绿、B 红、X 蓝、Y 黄）
- **实时设置面板** — 可调悬浮窗位置（水平/垂直 0–100%）、显示大小（0–100%）、透明度（60%/80%/100%），拖动滑块即时生效
- **单线程架构** — 全部逻辑运行于 PyQt5 主线程，无多线程、无锁、无竞态

---

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| GUI 框架 | **PyQt5** (>= 5.15) | 窗口系统、SVG 渲染、系统托盘 |
| 手柄输入 | **PySDL2** (>= 0.9) | SDL2 GameController / Joystick API |
| 窗口穿透 | **Win32 API** (ctypes) | `WS_EX_TRANSPARENT` + `WS_EX_LAYERED` |
| SVG 渲染 | **xml.etree.ElementTree** + **QSvgRenderer** | XML 模板深拷贝 → 属性修改 → QPixmap |
| 构建 | **PyInstaller** | 单文件 EXE 打包，内嵌 assets 目录 |
| 测试 | **pytest** | 纯逻辑测试（无 GUI / SDL2 硬件依赖） |

---

## 快速开始

### 前置环境

- **操作系统**：Windows 10 / 11（窗口穿透依赖 Win32 API）
- **Python**：3.10 或更高版本
- **SDL2 运行时**：通过 `pysdl2-dll` 自动安装，无需手动配置

### 克隆项目

```bash
git clone https://github.com/your-username/ControllerMapping.git
cd ControllerMapping
```

### 安装依赖

```bash
# 建议使用虚拟环境
python -m venv .venv
.venv\Scripts\activate       # Windows CMD
# source .venv/bin/activate  # Git Bash / WSL

pip install -r requirements.txt
```

`requirements.txt` 包含：

- `PyQt5>=5.15` — GUI 框架
- `PySDL2>=0.9` — 手柄输入（自动拉取 `pysdl2-dll` 提供 SDL2 运行时）

### 启动运行

```bash
python main.py
```

启动后系统托盘会出现手柄图标，连接手柄即可看到实时可视化叠加层。

**常见问题：**

| 问题 | 解决方案 |
|------|----------|
| `Failed to initialize SDL2` | 确认 `pysdl2-dll` 已安装：`pip install pysdl2-dll` |
| 悬浮窗不显示 | 检查是否被其他窗口覆盖，或调整托盘菜单中的位置/大小设置 |
| 手柄连接但未识别 | 确认手柄在 Windows 设备管理器中正常显示，尝试重新插拔 |

### 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_gamepad.py -v

# 运行单个测试用例
pytest tests/test_gamepad.py::test_axis_normalization -v
```

测试覆盖纯逻辑部分（轴归一化、按键映射、主题数据、渲染器映射），**无需连接真实手柄或启动 GUI**。

### 打包构建

```bash
pip install pyinstaller
pyinstaller ControllerOverlay.spec
```

生成的可执行文件位于 `dist/ControllerOverlay.exe`，已内嵌 `assets/` 目录中的所有 SVG 资源，可独立分发。

---

## 项目目录结构

```
ControllerMapping/
├── main.py                              # 应用入口：初始化 PyQt5、连接各模块信号
├── requirements.txt                     # Python 依赖声明
├── ControllerOverlay.spec               # PyInstaller 打包配置（含 assets 内嵌）
├── CLAUDE.md                            # AI 辅助开发指引
├── README.md                            # 本文件
│
├── src/controller_overlay/              # 应用核心包
│   ├── __init__.py                      # 包初始化
│   ├── gamepad.py                       # SDL2 手柄管理：按键映射、轴归一化、热插拔检测
│   ├── overlay.py                       # 透明悬浮窗：窗口属性、轮询驱动、绘制布局
│   ├── svg_renderer.py                  # SVG 渲染引擎：模板加载、元素属性修改、QPixmap 生成
│   ├── renderers.py                     # 渲染数据：按键→SVG元素映射、触发器偏移、摇杆中心
│   ├── themes.py                        # 颜色主题：三套主题定义（white/black/neon）
│   └── tray.py                          # 系统托盘：右键菜单、设置对话框
│
├── assets/                              # SVG 图像资源
│   ├── xbox.svg                         # Xbox 手柄布局（viewBox 0 0 427 240）
│   ├── dualsense.svg                    # DualSense/PS5 布局（viewBox 0 0 128 128）
│   ├── left_trigger.svg                 # 左扳机形状（viewBox 0 0 90 138）
│   ├── right_trigger.svg                # 右扳机形状（viewBox 0 0 90 138）
│   ├── xbox_logo.svg                    # Xbox 标识 SVG
│   └── ps_logo.svg                      # PlayStation 标识 SVG
│
├── tests/                               # 测试套件
│   ├── conftest.py                      # 测试配置：将 src/ 加入 sys.path
│   ├── test_gamepad.py                  # 轴归一化、按键映射、控制器类型检测测试
│   ├── test_renderers.py                # 渲染器映射数据完整性测试
│   ├── test_themes.py                   # 主题数据结构与颜色覆盖测试
│   └── test_render.py                   # 独立渲染验证脚本
│
└── docs/                                # 文档
    └── superpowers/specs/               # 设计规格文档
```

---

## 架构设计

**单线程、定时器驱动**的 PyQt5 应用，所有模块运行于主线程，无跨线程通信。

```
系统托盘 (TrayController)
  │  pyqtSignal: theme_changed / opacity_changed / position_changed / scale_changed / quit_requested
  ▼
main.py — 信号连接（闭包中转）
  │
  ├── GamepadManager (gamepad.py)
  │     SDL2 初始化 → GameController/Joystick 打开 → 8ms 轮询 → GamepadState
  │
  └── ControllerOverlay (overlay.py)
        │
        ├── _poll() ← QTimer 8ms
        │     ├── gamepad.poll() → 获取 GamepadState
        │     ├── _sync_state() → 推送到 SvgRenderer
        │     └── self.update() → 触发 paintEvent
        │
        ├── SvgRenderer (svg_renderer.py)
        │     ├── on_button_pressed/released → 脏标记
        │     ├── on_trigger_changed → 脏标记（阈值 0.5%）
        │     ├── on_joystick_changed → 脏标记（阈值 2%）
        │     └── render() → 深拷贝 SVG 模板 → 修改元素 → QPixmap 缓存
        │
        └── paintEvent
              绘制主控制器 + 扳机图像（定位于肩键上方）
```

**渲染管线：**

1. `GamepadManager.poll()` 通过 SDL2 读取手柄状态 → `GamepadState`
2. `_sync_state()` 比对前后状态差异，仅推送变化到 `SvgRenderer`
3. `SvgRenderer.render()` 仅在脏标记为 `True` 时重建：深拷贝 SVG XML → 修改 fill/stroke/transform → 序列化 → `QSvgRenderer` → `QPixmap`
4. `paintEvent` 绘制缓存的主控制器 pixmap 和扳机 pixmap

---

## 配置说明

所有配置通过**系统托盘右键菜单**或**设置对话框**完成，无配置文件。

| 设置项 | 选项 | 默认值 | 说明 |
|--------|------|--------|------|
| 配色主题 | White / Black / Neon | White | 按键高亮配色方案 |
| 透明度 | 100% / 80% / 60% | 100%（实际 0.9） | 悬浮窗整体透明度 |
| 水平位置 | 0–100 | 90 | 悬浮窗水平位置百分比 |
| 垂直位置 | 0–100 | 85 | 悬浮窗垂直位置百分比 |
| 显示大小 | 0–100 | 30 | 0 = 隐藏，100 = 全屏 |

设置变更通过 `pyqtSignal` 实时传递，无需重启。

---

## 添加新手柄布局

如需支持新的控制器类型，按以下步骤操作：

1. **添加 SVG 图像** — 将控制器 SVG 放入 `assets/` 目录，为每个可交互元素设置唯一 `id`
2. **添加枚举值** — 在 `gamepad.py` 的 `ControllerType` 中新增枚举
3. **添加检测逻辑** — 在 `detect_controller_type()` 中添加名称识别规则
4. **创建按键映射** — 在 `renderers.py` 中添加 `BUTTON_MAP`、`TRIGGER_OFFSETS`、`JOYSTICK_MAPS`、`STICK_CENTERS`
5. **加载 SVG 模板** — 在 `svg_renderer.py` 的 `_load_templates()` 中注册新模板
6. **添加渲染逻辑** — 如需特殊渲染（如 DualSense 的缩放摇杆），在 `svg_renderer.py` 中新增 `_apply_*` 方法

---

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

# 示例
feat(gamepad): add Nintendo Switch Pro controller support
fix(overlay): resolve high-DPI scaling issue
docs(readme): update quick start guide
```

**类型标识：** `feat`（新功能）、`fix`（修复）、`docs`（文档）、`refactor`（重构）、`test`（测试）、`chore`（构建/工具）

### 提交流程

1. **Fork** 本仓库并创建功能分支：`git checkout -b feat/my-feature`
2. 编写代码并确保**测试通过**：`pytest tests/ -v`
3. 提交代码：`git commit -m "feat: add my feature"`
4. 推送分支：`git push origin feat/my-feature`
5. 创建 **Pull Request**，描述变更内容和动机

### Issue 提交

- 描述问题或需求的具体表现
- 附上系统环境（Windows 版本、手柄型号、Python 版本）
- 如有报错，贴出完整错误信息

### 代码风格

- **命名**：`snake_case` 函数/变量，`PascalCase` 类，`UPPER_CASE` 模块常量
- **导入**：标准库 → 第三方 → 本地，包内使用相对导入（`from .xxx`）
- **测试**：测试文件与源文件对应（`test_gamepad.py` 对应 `gamepad.py`），仅覆盖纯逻辑

---

## 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。
