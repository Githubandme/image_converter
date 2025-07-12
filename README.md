# PicPlus Converter - 批量图片格式转换工具

![PicPlus Converter Logo](src/picpp_icon.ico)

## ✨ 功能说明

PicPlus Converter 是一个功能强大的批量图片格式转换工具，主要功能包括：

- **多格式转换**：支持 JPG、WEBP、AVIF 等多种流行图片格式之间的相互转换
- **批量处理**：可一次性选择并转换多个图片文件
- **质量调节**：提供 10-100% 的质量滑块，精确控制输出文件质量
- **两种处理模式**：
  - ✅ **覆盖模式**：直接替换原文件（格式不同时会自动删除原文件）
  - ✅ **保存模式**：将转换后的文件保存到指定目录
- **错误处理**：自动识别并备份处理失败的图片文件到"处理错误"目录
- **实时日志**：详细记录转换过程和结果，便于排查问题
- **进度显示**：实时显示转换进度百分比

## 📚 使用的开源项目

PicPlus Converter 基于以下优秀开源项目构建：

1. **[PySide6](https://pypi.org/project/PySide6/)** (LGPL-3.0) - Qt for Python，提供GUI框架
2. **[Pillow](https://pypi.org/project/Pillow/)** (HPND) - 强大的图像处理库
3. **[pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/)** (MIT) - AVIF格式支持插件

## 📜 许可证

PicPlus Converter 采用 **GPL-3.0 许可证**发布：

```text
PicPlus Converter - 批量图片格式转换工具
Copyright (C) 2023 YourName

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

🚀 快速开始
安装依赖：

bash
----
pip install PySide6 Pillow pillow-avif-plugin
----

运行程序：

bash
-----
python src/image_converter.py
----
按照GUI界面指示操作即可

⚠️ 注意事项
转换JPG格式时，透明背景会自动填充为白色
AVIF格式需要安装pillow-avif-plugin插件
转换过程中可以随时取消
失败的文件会自动保存到"处理错误"目录