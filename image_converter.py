import os
import shutil
from PIL import Image, UnidentifiedImageError
import pillow_avif  # 插件自动注册支持AVIF
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog,
    QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QProgressBar, QMessageBox, QTextEdit,
    QGroupBox, QRadioButton, QButtonGroup, QLineEdit, QSizePolicy, QSpacerItem, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QPalette, QIcon


class ConverterThread(QThread):
    progress = Signal(int)
    status = Signal(str, str)  # 参数1: 消息类型, 参数2: 消息内容
    finished = Signal(int, int, int, str, str, str)

    def __init__(self, files, fmt, mode, quality, out_dir):
        super().__init__()
        self.files = files
        self.format = fmt
        self.mode = mode
        self.quality = quality
        self.out_dir = out_dir
        self.is_running = True

    def run(self):
        total = len(self.files)
        success = 0
        fail = 0
        
        # 确定错误目录位置
        if self.mode == "覆盖":
            base_dir = os.path.dirname(self.files[0])
        else:
            base_dir = self.out_dir
        
        err_dir = os.path.join(base_dir, "处理错误")
        os.makedirs(err_dir, exist_ok=True)
        
        self.status.emit("info", f"🛠️ 开始处理 {total} 个图片文件...")
        self.status.emit("info", f"🔄 输出格式: {self.format}")
        self.status.emit("info", f"📁 保存方式: {self.mode}")
        if self.mode == "路径选择":
            self.status.emit("info", f"📂 输出目录: {self.out_dir}")
        self.status.emit("info", f"⚖️ 图片质量: {self.quality}%")
        self.status.emit("info", f"⚠️ 错误文件将保存到: {err_dir}")
        self.status.emit("info", "="*60)
        
        # 映射格式到Pillow的格式标识符
        format_map = {
            "JPG": "JPEG",
            "WEBP": "WEBP",
            "AVIF": "AVIF"
        }
        save_format = format_map.get(self.format, self.format)

        for idx, filepath in enumerate(self.files, 1):
            if not self.is_running:
                break
                
            try:
                filename = os.path.basename(filepath)
                self.status.emit("processing", f"🔧 正在处理 {idx}/{total}: {filename}...")
                
                with Image.open(filepath) as img:
                    base_name = os.path.splitext(filename)[0]
                    file_ext = os.path.splitext(filename)[1].lower().replace(".", "")
                    
                    # 确定目标目录和输出路径
                    if self.mode == "覆盖":
                        target_dir = os.path.dirname(filepath)
                        # 如果格式相同，则直接覆盖原文件
                        if file_ext == self.format.lower():
                            out_path = filepath
                        else:
                            out_path = os.path.join(target_dir, f"{base_name}.{self.format.lower()}")
                    else:
                        target_dir = self.out_dir
                        out_path = os.path.join(target_dir, f"{base_name}.{self.format.lower()}")
                    
                    # 确保目录存在
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 如果目标文件已存在且与源文件相同，则跳过
                    if out_path != filepath and os.path.exists(out_path):
                        self.status.emit("info", f"ℹ️ 跳过: {filename} (目标文件已存在)")
                        continue
                    
                    # 特殊处理JPG格式
                    if save_format == "JPEG":
                        # 将图像转换为RGB模式（JPEG不支持透明通道）
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        # 保存JPEG图像
                        img.save(out_path, format=save_format, quality=self.quality, optimize=True)
                    else:
                        # 保存其他格式图像
                        img.save(out_path, format=save_format, quality=self.quality)
                    
                    # 如果是覆盖模式且格式改变，删除原文件
                    if self.mode == "覆盖" and out_path != filepath:
                        os.remove(filepath)
                        self.status.emit("success", f"✅ 成功: {filename} → {os.path.basename(out_path)}")
                    else:
                        self.status.emit("success", f"✅ 成功: {filename} (已更新)")
                    
                    success += 1
                    
            except (UnidentifiedImageError, OSError, ValueError) as e:
                error_filename = f"error_{filename}"
                error_path = os.path.join(err_dir, error_filename)
                
                try:
                    shutil.copy(filepath, error_path)
                    self.status.emit("error", f"❌ 处理失败: {filename} (已备份到错误目录)")
                except:
                    self.status.emit("error", f"❌ 处理失败且无法备份: {filename}")
                
                # 记录错误详情
                error_detail = f"错误类型: {type(e).__name__}\n错误信息: {str(e)}"
                self.status.emit("error_detail", error_detail)
                fail += 1
                
            progress_percent = int((idx / total) * 100)
            self.progress.emit(progress_percent)

        self.finished.emit(total, success, fail, self.out_dir, err_dir, os.path.dirname(self.files[0]))
        self.status.emit("info", "="*60)
        self.status.emit("info", "✨ 处理完成！")

    def stop(self):
        self.is_running = False


class ImageConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量图片格式转换工具")
        self.resize(800, 700)
        
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(__file__), "picpp_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
                padding: 10px;
            }
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
                color: #666666;
            }
            QRadioButton {
                padding: 4px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #4a86e8;
                border-radius: 3px;
            }
        """)

        self.selected_files = []
        self.output_path = ""
        self.thread = None

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        file_info_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setWordWrap(True)
        file_info_layout.addWidget(self.file_label)
        
        self.select_button = QPushButton("选择图片文件")
        self.select_button.setFixedWidth(140)
        self.select_button.clicked.connect(self.select_files)
        file_info_layout.addWidget(self.select_button)
        
        file_layout.addLayout(file_info_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 转换设置区域
        settings_group = QGroupBox("转换设置")
        settings_layout = QVBoxLayout()
        
        # 格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("目标格式:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPG", "WEBP", "AVIF"])
        self.format_combo.setFixedWidth(140)
        format_layout.addWidget(self.format_combo)
        format_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        settings_layout.addLayout(format_layout)

        # 处理方式选择（单选按钮）
        mode_group = QGroupBox("处理方式")
        mode_layout = QHBoxLayout()
        
        self.mode_overwrite = QRadioButton("覆盖原文件")
        self.mode_select_path = QRadioButton("选择保存路径")
        self.mode_overwrite.setChecked(True)
        
        mode_layout.addWidget(self.mode_overwrite)
        mode_layout.addWidget(self.mode_select_path)
        mode_group.setLayout(mode_layout)
        settings_layout.addWidget(mode_group)

        # 路径选择区域
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("输出路径:"))
        
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText("选择路径或使用覆盖模式")
        path_layout.addWidget(self.path_display)
        
        self.path_button = QPushButton("选择文件夹")
        self.path_button.setFixedWidth(120)
        self.path_button.clicked.connect(self.select_output_path)
        self.path_button.setEnabled(False)  # 默认禁用
        path_layout.addWidget(self.path_button)
        
        settings_layout.addLayout(path_layout)

        # 质量滑块
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("图片质量"))
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("小文件"))
        
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(10)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(80)
        slider_layout.addWidget(self.quality_slider)
        
        slider_layout.addWidget(QLabel("高质量"))
        quality_layout.addLayout(slider_layout)
        
        self.quality_value = QLabel("80%")
        self.quality_value.setAlignment(Qt.AlignCenter)
        self.quality_value.setStyleSheet("font-weight: bold; color: #1a5fb4;")
        quality_layout.addWidget(self.quality_value)
        
        settings_layout.addLayout(quality_layout)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # 进度条
        progress_group = QGroupBox("转换进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # 创建分隔器，使日志区域可以调整大小
        splitter = QSplitter(Qt.Vertical)
        
        # 日志显示区域
        log_group = QGroupBox("转换日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # 设置日志文本区域的最小高度
        self.log_text.setMinimumHeight(250)
        
        # 设置日志字体
        log_font = QFont()
        log_font.setFamily("Consolas")
        log_font.setPointSize(10)
        self.log_text.setFont(log_font)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        splitter.addWidget(log_group)
        splitter.setSizes([300])  # 初始高度为300像素
        
        # 添加分隔器到主布局
        main_layout.addWidget(splitter)

        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始转换")
        self.start_button.setFixedHeight(40)
        self.start_button.setStyleSheet("font-weight: bold;")
        self.start_button.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("取消转换")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_conversion)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 连接信号
        self.mode_overwrite.toggled.connect(self.mode_changed)
        self.mode_select_path.toggled.connect(self.mode_changed)
        self.quality_slider.valueChanged.connect(self.quality_changed)

    def mode_changed(self):
        """处理模式改变时的UI更新"""
        if self.mode_select_path.isChecked():
            self.path_button.setEnabled(True)
            self.path_display.setPlaceholderText("请选择输出文件夹")
        else:
            self.path_button.setEnabled(False)
            self.path_display.clear()
            self.path_display.setPlaceholderText("选择路径或使用覆盖模式")

    def quality_changed(self, value):
        """质量滑块值改变时的更新"""
        self.quality_value.setText(f"{value}%")
        # 根据质量值设置不同的颜色
        if value < 50:
            color = "#c01c28"  # 红色
        elif value < 80:
            color = "#e5a50a"  # 黄色
        else:
            color = "#26a269"  # 绿色
        self.quality_value.setStyleSheet(f"font-weight: bold; color: {color};")

    def select_files(self):
        """选择图片文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择图片文件", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.webp *.bmp *.avif *.tiff);;所有文件 (*.*)"
        )
        
        if files:
            self.selected_files = files
            if len(files) == 1:
                self.file_label.setText(f"已选择文件: {os.path.basename(files[0])}")
            else:
                self.file_label.setText(f"已选择 {len(files)} 个文件")
                self.file_label.setToolTip("\n".join([os.path.basename(f) for f in files]))
    
    def select_output_path(self):
        """选择输出文件夹"""
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_path = path
            self.path_display.setText(path)
            self.path_display.setToolTip(path)

    def start_conversion(self):
        """开始转换过程"""
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择图片文件")
            return
            
        if self.mode_select_path.isChecked() and not self.output_path:
            QMessageBox.warning(self, "警告", "请选择输出文件夹")
            return
            
        # 获取设置
        fmt = self.format_combo.currentText()
        mode = "路径选择" if self.mode_select_path.isChecked() else "覆盖"
        quality = self.quality_slider.value()
        out_dir = self.output_path if mode == "路径选择" else ""
        
        # 清空日志
        self.log_text.clear()
        
        # 更新UI状态
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.select_button.setEnabled(False)
        self.path_button.setEnabled(False)
        self.mode_overwrite.setEnabled(False)
        self.mode_select_path.setEnabled(False)
        self.quality_slider.setEnabled(False)
        self.format_combo.setEnabled(False)
        
        # 创建并启动线程
        self.thread = ConverterThread(self.selected_files, fmt, mode, quality, out_dir)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.status.connect(self.update_log)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()
        
        # 添加日志头
        self.append_log("info", "=" * 60)
        self.append_log("info", "📝 开始新的转换任务")
        self.append_log("info", "=" * 60)
    
    def update_log(self, msg_type, message):
        """更新日志显示"""
        self.append_log(msg_type, message)
        
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def append_log(self, msg_type, message):
        """根据消息类型添加带格式的日志"""
        cursor = self.log_text.textCursor()
        format = QTextCharFormat()
        
        if msg_type == "info":
            format.setForeground(QColor("#1a5fb4"))  # 蓝色 - 信息
        elif msg_type == "success":
            format.setForeground(QColor("#26a269"))  # 绿色 - 成功
        elif msg_type == "error":
            format.setForeground(QColor("#c01c28"))  # 红色 - 错误
            format.setFontWeight(QFont.Bold)
        elif msg_type == "error_detail":
            format.setForeground(QColor("#a51d2d"))  # 深红色 - 错误详情
        elif msg_type == "processing":
            format.setForeground(QColor("#9141ac"))  # 紫色 - 处理中
        else:
            format.setForeground(QColor("#000000"))  # 黑色 - 默认
        
        cursor.insertText(message + "\n", format)
    
    def cancel_conversion(self):
        """取消转换过程"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.append_log("info", "⏹️ 用户请求取消转换...")
            self.append_log("info", "🔄 等待当前任务完成...")
            self.thread.wait(2000)  # 等待线程结束
        
        # 重置UI状态
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.select_button.setEnabled(True)
        self.path_button.setEnabled(self.mode_select_path.isChecked())
        self.mode_overwrite.setEnabled(True)
        self.mode_select_path.setEnabled(True)
        self.quality_slider.setEnabled(True)
        self.format_combo.setEnabled(True)
        
        self.append_log("info", "🚫 转换已取消")
        self.append_log("info", "=" * 60)

    def on_finished(self, total, success, fail, out_dir, err_dir, origin_dir):
        """转换完成时的处理"""
        # 更新UI状态
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.select_button.setEnabled(True)
        self.path_button.setEnabled(self.mode_select_path.isChecked())
        self.mode_overwrite.setEnabled(True)
        self.mode_select_path.setEnabled(True)
        self.quality_slider.setEnabled(True)
        self.format_combo.setEnabled(True)
        
        # 显示结果摘要
        self.append_log("info", "=" * 60)
        self.append_log("info", f"✨ 转换完成!")
        self.append_log("info", f"📊 总数: {total}")
        self.append_log("success", f"✅ 成功: {success}")
        if fail > 0:
            self.append_log("error", f"❌ 失败: {fail}")
        else:
            self.append_log("success", f"❌ 失败: {fail}")
        
        self.append_log("info", f"📂 原路径: {origin_dir}")
        if out_dir:
            self.append_log("info", f"📁 输出路径: {out_dir}")
        self.append_log("info", f"⚠️ 错误路径: {err_dir}")
        self.append_log("info", "=" * 60)
        
        # 显示完成消息框
        QMessageBox.information(
            self, 
            "处理完成", 
            f"图片转换完成！\n\n"
            f"📊 总数: {total}\n"
            f"✅ 成功: {success}\n"
            f"❌ 失败: {fail}\n\n"
            f"📂 原路径: {origin_dir}\n"
            f"📁 输出路径: {out_dir or origin_dir}\n"
            f"⚠️ 错误路径: {err_dir}"
        )


if __name__ == "__main__":
    app = QApplication([])
    window = ImageConverterApp()
    window.show()
    app.exec()