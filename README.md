# 手柄投影 (Controller Overlay)

Windows 桌面游戏手柄实时可视化工具。在屏幕上显示一个半透明、置顶、鼠标穿透的悬浮窗，实时反映手柄的按键、摇杆、扳机和方向键操作。

## 功能特性

- **实时渲染** — 约 120Hz 轮询频率，QPainter 绘制 Xbox 风格手柄图形
- **悬浮覆盖** — 无边框、始终置顶、鼠标点击穿透，不影响正常操作
- **系统托盘** — 无任务栏图标，右键托盘菜单控制主题、透明度和退出
- **三种主题** — 白色 / 黑色 / 霓虹
- **三级透明度** — 100% / 80% / 60%
- **热插拔** — 手柄连接/断开自动检测，无需重启
- **零外部资源** — 手柄图形全部由 QPainter 绘制，无图片文件依赖

## 系统要求

- Windows 10/11
- Python 3.10+
- SDL2 运行时（PySDL2 会自动查找系统已安装的 SDL2）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

启动后系统托盘会出现手柄图标，连接手柄即可看到实时可视化。

### 运行测试

```bash
pytest tests/ -v
```

## 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name ControllerOverlay main.py
```

生成的可执行文件位于 `dist/ControllerOverlay.exe`。

## 项目结构

```
├── main.py              # 入口：初始化应用并连接各模块信号
├── gamepad.py           # SDL2 手柄抽象层：按键映射、轴归一化、热插拔
├── overlay.py           # 透明悬浮窗 + QPainter 手柄渲染
├── tray.py              # 系统托盘图标与右键菜单
├── themes.py            # 颜色主题定义（白色 / 黑色 / 霓虹）
├── requirements.txt     # Python 依赖
├── ControllerOverlay.spec  # PyInstaller 打包配置
└── tests/
    ├── test_gamepad.py  # 轴归一化与按键映射测试
    └── test_themes.py   # 主题数据完整性测试
```

## 技术栈

| 组件       | 技术                          |
| ---------- | ----------------------------- |
| GUI        | PyQt5                         |
| 手柄输入   | PySDL2 (SDL2 Joystick 子系统) |
| 窗口穿透   | Win32 API (ctypes)            |
| 渲染       | QPainter (纯代码绘制)          |
| 打包       | PyInstaller                   |
| 测试       | pytest                        |

## 架构

```
系统托盘图标 (右键菜单: 透明度 / 主题 / 退出)
       │
透明悬浮窗 (始终置顶, 鼠标穿透)
       │
QTimer (8ms / ~120Hz) → PySDL2 轮询 → 状态更新 → QPainter 重绘
```

所有逻辑在 PyQt5 主线程中单线程运行，无跨线程通信。

## 已知限制

- **仅 Windows** — 鼠标穿透依赖 Win32 API，macOS/Linux 需另行适配
- **单手柄** — 仅追踪第一个连接的手柄，暂不支持多手柄切换
- **Xbox 布局** — 按键映射基于 Xbox 风格 ABXY，其他布局控制器通过 SDL2 兼容

## 许可证

MIT
