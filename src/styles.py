"""
声隐 SoundShield - UI 样式定义
现代浅色主题，清新专业
"""

# 主题颜色 - 浅色主题
COLORS = {
    # 主色调 - 靛蓝色
    "primary": "#6366F1",
    "primary_hover": "#4F46E5",
    "primary_pressed": "#4338CA",
    "primary_light": "#E0E7FF",
    
    # 背景色 - 浅色
    "bg_main": "#F8FAFC",         # 主背景
    "bg_card": "#FFFFFF",          # 卡片背景
    "bg_input": "#F1F5F9",         # 输入框背景
    "bg_hover": "#E2E8F0",         # 悬停背景
    
    # 文字颜色
    "text_primary": "#1E293B",     # 主要文字
    "text_secondary": "#64748B",   # 次要文字
    "text_muted": "#94A3B8",       # 淡化文字
    
    # 状态颜色
    "success": "#10B981",
    "success_bg": "#D1FAE5",
    "warning": "#F59E0B",
    "warning_bg": "#FEF3C7",
    "error": "#EF4444",
    "error_bg": "#FEE2E2",
    "info": "#3B82F6",
    "info_bg": "#DBEAFE",
    
    # 边框
    "border": "#E2E8F0",
    "border_focus": "#6366F1",
    
    # 阴影
    "shadow": "rgba(0, 0, 0, 0.05)",
}

# 主样式表
MAIN_STYLESHEET = f"""
/* 全局样式 */
QMainWindow {{
    background-color: {COLORS["bg_main"]};
}}

QWidget {{
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 14px;
    color: {COLORS["text_primary"]};
}}

/* 标题标签 */
QLabel#titleLabel {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS["text_primary"]};
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}

/* 拖拽区域 */
QFrame#dropZone {{
    background-color: {COLORS["bg_card"]};
    border: 2px dashed {COLORS["border"]};
    border-radius: 16px;
}}

QFrame#dropZone:hover {{
    border-color: {COLORS["primary"]};
    background-color: {COLORS["primary_light"]};
}}

/* 按钮样式 */
QPushButton {{
    background-color: {COLORS["primary"]};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {COLORS["primary_hover"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["primary_pressed"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_input"]};
    color: {COLORS["text_muted"]};
}}

QPushButton#secondaryBtn {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {COLORS["bg_input"]};
    border-color: {COLORS["primary"]};
    color: {COLORS["primary"]};
}}

/* 文本编辑区域 */
QTextEdit {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 12px;
    padding: 16px;
    font-size: 15px;
    line-height: 1.6;
    selection-background-color: {COLORS["primary_light"]};
}}

QTextEdit:focus {{
    border-color: {COLORS["primary"]};
    border-width: 2px;
}}

/* 进度条 */
QProgressBar {{
    background-color: {COLORS["bg_input"]};
    border: none;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: {COLORS["text_primary"]};
    font-size: 12px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS["primary"]},
        stop:1 {COLORS["primary_hover"]});
    border-radius: 8px;
}}

/* 状态栏 */
QStatusBar {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_secondary"]};
    border-top: 1px solid {COLORS["border"]};
    padding: 8px;
}}

/* 滚动条 */
QScrollBar:vertical {{
    background-color: {COLORS["bg_main"]};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["primary"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* 文件标签 */
QLabel#fileLabel {{
    color: {COLORS["text_secondary"]};
    font-size: 13px;
}}

/* 状态标签 */
QLabel#statusLabel {{
    color: {COLORS["success"]};
    font-size: 13px;
    font-weight: 500;
}}

/* 消息框样式 */
QMessageBox {{
    background-color: {COLORS["bg_card"]};
}}

QMessageBox QLabel {{
    color: {COLORS["text_primary"]};
}}
"""

# 拖拽区域激活样式
DROP_ZONE_ACTIVE = f"""
QFrame#dropZone {{
    background-color: {COLORS["primary_light"]};
    border: 2px dashed {COLORS["primary"]};
    border-radius: 16px;
}}
"""

# 拖拽区域正常样式
DROP_ZONE_NORMAL = f"""
QFrame#dropZone {{
    background-color: {COLORS["bg_card"]};
    border: 2px dashed {COLORS["border"]};
    border-radius: 16px;
}}
"""
