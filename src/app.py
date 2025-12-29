"""
声隐 SoundShield - 主应用窗口
现代化浅色主题桌面应用
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QProgressBar, QFileDialog,
    QFrame, QStatusBar, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QThread, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon

from .styles import MAIN_STYLESHEET, DROP_ZONE_ACTIVE, DROP_ZONE_NORMAL, COLORS
from .audio_utils import is_supported_format, get_supported_formats_filter, get_file_info, is_video_file, prepare_audio_file
from .transcriber import get_transcriber


class ModelLoaderThread(QThread):
    """模型加载线程"""
    progress = Signal(str)
    finished = Signal(bool)
    
    def run(self):
        transcriber = get_transcriber()
        success = transcriber.load_model(
            progress_callback=lambda msg: self.progress.emit(msg)
        )
        self.finished.emit(success)


class TranscribeThread(QThread):
    """转写处理线程"""
    progress = Signal(str, int)
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, audio_path: str):
        super().__init__()
        self.audio_path = audio_path
    
    def run(self):
        transcriber = get_transcriber()
        
        # 如果是视频文件，先提取音频
        audio_path = prepare_audio_file(self.audio_path)
        if audio_path is None:
            self.error.emit("视频音频提取失败，请确保已安装 FFmpeg")
            return
        
        result = transcriber.transcribe(
            audio_path,
            progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
        )
        
        if result is not None:
            self.finished.emit(result)
        else:
            self.error.emit("识别失败，请检查音频文件")


class DropZone(QFrame):
    """拖拽上传区域"""
    file_dropped = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        # 图标
        icon_label = QLabel("🎵")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 主文字
        main_label = QLabel("拖拽音频文件到此处")
        main_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']};")
        main_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(main_label)
        
        # 副文字
        sub_label = QLabel("或点击选择文件")
        sub_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_label)
        
        # 格式提示
        format_label = QLabel("支持格式: MP3, WAV, M4A, FLAC, OGG, MP4, MKV, AVI, MOV")
        format_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_muted']}; margin-top: 8px;")
        format_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(format_label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(DROP_ZONE_ACTIVE)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(DROP_ZONE_NORMAL)
    
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(DROP_ZONE_NORMAL)
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if is_supported_format(file_path):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "格式不支持", "请选择支持的音频或视频格式文件")
    
    def mousePressEvent(self, event):
        self.open_file_dialog()
    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频文件",
            "",
            get_supported_formats_filter()
        )
        if file_path:
            self.file_dropped.emit(file_path)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_file: Optional[str] = None
        self.model_loaded = False
        self.transcribe_thread: Optional[TranscribeThread] = None
        
        self.init_ui()
        self.load_model()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("声隐 SoundShield - 隐私语音转文字")
        self.setMinimumSize(800, 700)
        self.resize(900, 750)
        
        # 应用样式
        self.setStyleSheet(MAIN_STYLESHEET)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)
        
        # === 标题区域 ===
        title_layout = QHBoxLayout()
        
        # Logo + 标题
        title_left = QVBoxLayout()
        title_label = QLabel("🛡️ 声隐 SoundShield")
        title_label.setObjectName("titleLabel")
        title_left.addWidget(title_label)
        
        subtitle_label = QLabel("您的隐私听写专家 · 100% 本地运行")
        subtitle_label.setObjectName("subtitleLabel")
        title_left.addWidget(subtitle_label)
        
        title_layout.addLayout(title_left)
        title_layout.addStretch()
        
        # 状态指示
        self.model_status_label = QLabel("⏳ 正在加载模型...")
        self.model_status_label.setStyleSheet(f"color: {COLORS['warning']};")
        title_layout.addWidget(self.model_status_label)
        
        main_layout.addLayout(title_layout)
        
        # === 拖拽区域 ===
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.on_file_selected)
        main_layout.addWidget(self.drop_zone)
        
        # === 文件信息 & 进度 ===
        info_layout = QHBoxLayout()
        
        self.file_label = QLabel("未选择文件")
        self.file_label.setObjectName("fileLabel")
        info_layout.addWidget(self.file_label)
        
        info_layout.addStretch()
        
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        info_layout.addWidget(self.status_label)
        
        main_layout.addLayout(info_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v")
        main_layout.addWidget(self.progress_bar)
        
        # === 结果区域 ===
        result_label = QLabel("识别结果")
        result_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']}; margin-top: 8px;")
        main_layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("识别结果将显示在这里...\n\n提示：\n• 拖拽或点击上方区域选择文件\n• 支持音频: MP3, WAV, M4A, FLAC, OGG\n• 支持视频: MP4, MKV, AVI, MOV\n• 所有处理均在本地完成，数据不会上传")
        self.result_text.setMinimumHeight(200)
        main_layout.addWidget(self.result_text, 1)
        
        # === 操作按钮 ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.start_btn = QPushButton("🎯 开始识别")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_transcription)
        button_layout.addWidget(self.start_btn)
        
        button_layout.addStretch()
        
        self.copy_btn = QPushButton("📋 复制文本")
        self.copy_btn.setObjectName("secondaryBtn")
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)
        
        self.export_btn = QPushButton("💾 导出 TXT")
        self.export_btn.setObjectName("secondaryBtn")
        self.export_btn.clicked.connect(self.export_result)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
        
        # === 状态栏 ===
        self.statusBar().showMessage("🔒 离线模式 · 数据安全")
    
    def load_model(self):
        """后台加载模型"""
        self.loader_thread = ModelLoaderThread()
        self.loader_thread.progress.connect(self.on_model_progress)
        self.loader_thread.finished.connect(self.on_model_loaded)
        self.loader_thread.start()
    
    def on_model_progress(self, message: str):
        """模型加载进度"""
        self.model_status_label.setText(f"⏳ {message}")
        self.statusBar().showMessage(message)
    
    def on_model_loaded(self, success: bool):
        """模型加载完成"""
        if success:
            self.model_loaded = True
            self.model_status_label.setText("✅ 模型就绪")
            self.model_status_label.setStyleSheet(f"color: {COLORS['success']};")
            self.statusBar().showMessage("🔒 离线模式 · 模型已加载 · 数据安全")
            
            # 如果已经选了文件，启用开始按钮
            if self.current_file:
                self.start_btn.setEnabled(True)
        else:
            self.model_status_label.setText("❌ 模型加载失败")
            self.model_status_label.setStyleSheet(f"color: {COLORS['error']};")
            QMessageBox.critical(
                self,
                "模型加载失败",
                "无法加载语音识别模型。\n\n"
                "可能原因：\n"
                "1. 网络问题（首次需要下载模型）\n"
                "2. 磁盘空间不足\n"
                "3. 内存不足\n\n"
                "请检查后重试。"
            )
    
    def on_file_selected(self, file_path: str):
        """文件选择处理"""
        self.current_file = file_path
        
        # 获取文件信息
        info = get_file_info(file_path)
        self.file_label.setText(f"📁 {info['name']} ({info['size_str']}, {info['duration_str']})")
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet(f"color: {COLORS['info']};")
        
        # 启用开始按钮
        if self.model_loaded:
            self.start_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"已选择: {file_path}")
    
    def start_transcription(self):
        """开始转写"""
        if not self.current_file or not self.model_loaded:
            return
        
        # 禁用按钮
        self.start_btn.setEnabled(False)
        self.drop_zone.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 清空之前的结果
        self.result_text.clear()
        
        # 启动转写线程
        self.transcribe_thread = TranscribeThread(self.current_file)
        self.transcribe_thread.progress.connect(self.on_transcribe_progress)
        self.transcribe_thread.finished.connect(self.on_transcribe_finished)
        self.transcribe_thread.error.connect(self.on_transcribe_error)
        self.transcribe_thread.start()
    
    def on_transcribe_progress(self, message: str, percent: int):
        """转写进度更新"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {COLORS['warning']};")
        self.statusBar().showMessage(message)
    
    def on_transcribe_finished(self, result: str):
        """转写完成"""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        
        self.result_text.setText(result)
        
        self.status_label.setText("✅ 识别完成")
        self.status_label.setStyleSheet(f"color: {COLORS['success']};")
        self.statusBar().showMessage("识别完成！")
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.drop_zone.setEnabled(True)
    
    def on_transcribe_error(self, error: str):
        """转写错误"""
        self.progress_bar.setVisible(False)
        
        self.status_label.setText(f"❌ {error}")
        self.status_label.setStyleSheet(f"color: {COLORS['error']};")
        
        QMessageBox.warning(self, "识别失败", error)
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.drop_zone.setEnabled(True)
    
    def copy_result(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("已复制到剪贴板！", 3000)
        else:
            self.statusBar().showMessage("没有可复制的内容", 3000)
    
    def export_result(self):
        """导出结果为 TXT 文件"""
        text = self.result_text.toPlainText()
        if not text:
            QMessageBox.information(self, "提示", "没有可导出的内容")
            return
        
        # 默认文件名
        default_name = "识别结果.txt"
        if self.current_file:
            default_name = Path(self.current_file).stem + "_识别结果.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出识别结果",
            default_name,
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.statusBar().showMessage(f"已导出到: {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"无法保存文件: {e}")


def create_app():
    """创建并返回应用程序"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用 Fusion 风格以获得更好的跨平台一致性
    
    window = MainWindow()
    window.show()
    
    return app, window
