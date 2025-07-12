import os
import sys
import PyInstaller.__main__
from pathlib import Path
import shutil
import subprocess
import traceback

def package_app():
    print("="*50)
    print("PicPlus 打包脚本启动")
    print("="*50)
    
    try:
        # 获取当前脚本所在目录
        base_dir = Path(__file__).parent.absolute()
        print(f"基础目录: {base_dir}")
        
        # 设置应用程序入口文件
        entry_file = base_dir / "image_converter.py"
        print(f"入口文件: {entry_file}")
        if not entry_file.exists():
            raise FileNotFoundError(f"找不到主程序文件: {entry_file}")
        
        # 设置图标文件路径
        icon_file = base_dir.parent / "assets" / "picpp_icon.ico"
        print(f"图标文件路径: {icon_file}")
        
        # 确保图标文件存在
        if not icon_file.exists():
            print("图标文件不存在，创建默认图标...")
            create_fallback_icon(icon_file)
            if not icon_file.exists():
                print("警告: 默认图标创建失败，继续打包但不使用图标")
                icon_file = None
        
        # PyInstaller 配置
        params = [
            str(entry_file),         # 主脚本文件
            '--name=PicPlus',        # 应用程序名称
            '--onefile',             # 打包为单个 EXE 文件
            '--windowed',            # 不显示控制台窗口
            '--noconsole',           # 不显示控制台
            '--clean',               # 清理临时文件
            '--hidden-import=pillow_avif',
            '--hidden-import=PySide6',
            '--add-data', f'{get_package_path("pillow_avif")};pillow_avif',
            '--add-data', f'{get_package_path("PIL")};PIL',
            '--add-data', f'{get_package_path("PySide6")};PySide6',
        ]
        
        # 添加图标（如果存在）
        if icon_file and icon_file.exists():
            params.append(f'--icon={str(icon_file)}')
        
        print("打包命令:", " ".join(params))
        
        # 运行 PyInstaller
        PyInstaller.__main__.run(params)
        
        # 创建额外的资源目录
        dist_dir = base_dir / "dist"
        if not dist_dir.exists():
            raise RuntimeError(f"打包失败: 输出目录 {dist_dir} 不存在")
        
        avif_plugin_dir = dist_dir / "pillow_avif"
        avif_plugin_dir.mkdir(exist_ok=True)
        
        # 复制 AVIF 插件所需的 DLL 文件
        try:
            import pillow_avif
            plugin_path = Path(pillow_avif.__file__).parent
            for file in plugin_path.glob("*.dll"):
                shutil.copy(file, avif_plugin_dir)
            print(f"已复制 AVIF 插件 DLL 文件到 {avif_plugin_dir}")
        except Exception as e:
            print(f"复制 AVIF 插件 DLL 文件失败: {e}")
        
        # 复制图标文件到 dist 目录
        if icon_file and icon_file.exists():
            shutil.copy(icon_file, dist_dir)
        
        # 检查生成的 EXE
        exe_file = dist_dir / "PicPlus.exe"
        if exe_file.exists():
            print(f"打包成功! EXE 文件位于: {exe_file}")
            print(f"文件大小: {exe_file.stat().st_size/1024/1024:.2f} MB")
        else:
            raise RuntimeError("打包失败: 未生成 EXE 文件")
        
        print("="*50)
        print("打包完成!")
        print("="*50)
        
        # 尝试自动打开输出目录
        try:
            os.startfile(dist_dir)
        except:
            print(f"请手动打开输出目录: {dist_dir}")
    
    except Exception as e:
        print("="*50)
        print("打包过程中出错!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("="*50)
        traceback.print_exc()
        sys.exit(1)

def get_package_path(package_name):
    """获取包安装路径"""
    try:
        import site
        for path in site.getsitepackages():
            package_path = Path(path) / package_name
            if package_path.exists():
                print(f"找到 {package_name}: {package_path}")
                return str(package_path)
    except:
        pass
    
    # 尝试在虚拟环境中查找
    venv_path = Path(sys.prefix) / "Lib" / "site-packages" / package_name
    if venv_path.exists():
        print(f"找到 {package_name}: {venv_path}")
        return str(venv_path)
    
    print(f"警告: 找不到 {package_name} 的安装路径")
    return package_name

def create_fallback_icon(icon_path):
    """创建备用图标"""
    print(f"创建备用图标: {icon_path}")
    try:
        from PIL import Image, ImageDraw
        # 创建简单的图标
        img = Image.new('RGB', (256, 256), (70, 130, 180))
        draw = ImageDraw.Draw(img)
        
        # 绘制相机图标
        draw.rectangle([(50, 80), (206, 180)], fill=(255, 255, 255))
        draw.ellipse([(100, 50), (156, 106)], fill=(200, 200, 255))
        
        # 绘制加号
        draw.rectangle([(220, 120), (240, 180)], fill=(255, 255, 255))
        draw.rectangle([(200, 140), (260, 160)], fill=(255, 255, 255))
        
        # 保存为ICO文件
        img.save(icon_path, format='ICO')
        print(f"备用图标已创建: {icon_path}")
        return True
    except Exception as e:
        print(f"创建备用图标失败: {e}")
        return False

if __name__ == "__main__":
    package_app()