#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序列帧特效预览器打包脚本
使用PyInstaller将Python应用打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class AppBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.dist_dir = self.script_dir / "dist"
        self.build_dir = self.script_dir / "build"
        self.output_dir = self.script_dir / "output"
        
        # 应用信息
        self.app_name = "序列帧特效预览器"
        self.app_version = "1.0.0"
        self.app_description = "用于预览序列帧特效动画的工具"
        
        # 要打包的应用
        self.apps = {
            "effect_preview": {
                "script": "effect_preview.py",
                "name": "序列帧特效预览器",
                "icon": None,
                "console": False,
                "onefile": True
            },
            "effect_preview_simple": {
                "script": "effect_preview_simple.py", 
                "name": "序列帧特效预览器_简化版",
                "icon": None,
                "console": False,
                "onefile": True
            }
        }
    
    def check_dependencies(self):
        """检查打包依赖"""
        print("🔍 检查打包依赖...")
        
        # 检查PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller 已安装: {PyInstaller.__version__}")
        except ImportError:
            print("❌ PyInstaller 未安装")
            print("请运行: pip install pyinstaller")
            return False
        
        # 检查其他依赖
        dependencies = [
            ("PIL", "Pillow"),
            ("tkinterdnd2", "tkinterdnd2")
        ]
        
        missing_deps = []
        for module, package in dependencies:
            try:
                __import__(module)
                print(f"✅ {package} 已安装")
            except ImportError:
                print(f"❌ {package} 未安装")
                missing_deps.append(package)
        
        if missing_deps:
            print(f"\n请安装缺失的依赖:")
            for dep in missing_deps:
                print(f"  pip install {dep}")
            return False
        
        return True
    
    def clean_build(self):
        """清理构建目录"""
        print("🧹 清理构建目录...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir, self.output_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  删除: {dir_path}")
        
        # 清理spec文件
        for spec_file in self.script_dir.glob("*.spec"):
            spec_file.unlink()
            print(f"  删除: {spec_file}")
    
    def create_output_dir(self):
        """创建输出目录"""
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 创建输出目录: {self.output_dir}")
    
    def build_app(self, app_key, app_config):
        """构建单个应用"""
        script_path = self.script_dir / app_config["script"]
        if not script_path.exists():
            print(f"❌ 脚本文件不存在: {script_path}")
            return False
        
        print(f"\n🔨 构建应用: {app_config['name']}")
        print(f"   脚本: {app_config['script']}")
        
        # 构建PyInstaller命令
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
        ]
        
        # 单文件模式
        if app_config.get("onefile", True):
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
        
        # 控制台模式
        if not app_config.get("console", False):
            cmd.append("--windowed")
        
        # 应用名称
        cmd.extend(["--name", app_config["name"]])
        
        # 图标
        if app_config.get("icon"):
            cmd.extend(["--icon", app_config["icon"]])
        
        # 添加数据文件
        # 如果有资源文件需要打包，可以在这里添加
        # if (self.script_dir / "resources").exists():
        #     cmd.extend(["--add-data", f"resources{os.pathsep}resources"])
        
        # 隐藏导入
        hidden_imports = [
            "PIL._tkinter_finder",
            "tkinterdnd2",
            "PIL.Image",
            "PIL.ImageTk"
        ]
        
        for imp in hidden_imports:
            cmd.extend(["--hidden-import", imp])
        
        # 排除不需要的模块
        excludes = [
            "matplotlib",
            "numpy",
            "scipy",
            "pandas",
            "jupyter",
            "IPython"
        ]
        
        for exc in excludes:
            cmd.extend(["--exclude-module", exc])
        
        # 脚本路径
        cmd.append(str(script_path))
        
        print(f"   命令: {' '.join(cmd)}")
        
        # 执行构建
        try:
            result = subprocess.run(cmd, cwd=self.script_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 构建成功: {app_config['name']}")
                return True
            else:
                print(f"❌ 构建失败: {app_config['name']}")
                print(f"错误输出: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 构建异常: {e}")
            return False
    
    def copy_outputs(self):
        """复制输出文件到统一目录"""
        print("\n📦 整理输出文件...")
        
        if not self.dist_dir.exists():
            print("❌ 没有找到构建输出")
            return False
        
        success_count = 0
        
        for item in self.dist_dir.iterdir():
            if item.is_file() and item.suffix == ".exe":
                # 复制exe文件
                dest_path = self.output_dir / item.name
                shutil.copy2(item, dest_path)
                print(f"  ✅ {item.name} -> {dest_path}")
                success_count += 1
            elif item.is_dir():
                # 复制目录
                dest_path = self.output_dir / item.name
                shutil.copytree(item, dest_path)
                print(f"  ✅ {item.name}/ -> {dest_path}/")
                success_count += 1
        
        return success_count > 0
    
    def create_readme(self):
        """创建说明文件"""
        readme_content = f"""# {self.app_name} v{self.app_version}

## 应用说明

{self.app_description}

## 包含的程序

### 1. 序列帧特效预览器.exe
- 完整版本，支持拖拽功能
- 需要 tkinterdnd2 库支持
- 功能最全面

### 2. 序列帧特效预览器_简化版.exe  
- 简化版本，不依赖 tkinterdnd2
- 功能与完整版相同，但不支持拖拽
- 兼容性更好

## 使用方法

1. 双击对应的exe文件启动程序
2. 选择或拖拽包含序列帧的文件夹
3. 在特效列表中选择要预览的特效
4. 使用播放控制按钮控制动画播放

## 功能特性

- 🎬 支持多种图片格式 (PNG, JPG, JPEG, GIF)
- 📁 多层目录扫描和分类显示
- 🔍 特效筛选功能
- ⚡ 播放速度调节
- 🔄 正序/反序播放
- 📊 详细的特效信息显示
- 🎯 自动播放下一个特效

## 系统要求

- Windows 7/8/10/11
- 无需安装Python环境
- 建议内存: 512MB以上

## 版本信息

- 版本: {self.app_version}
- 构建时间: {self.get_build_time()}
- 系统架构: {platform.machine()}

## 技术支持

如有问题请联系开发者。
"""
        
        readme_path = self.output_dir / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print(f"📝 创建说明文件: {readme_path}")
    
    def get_build_time(self):
        """获取构建时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_batch_files(self):
        """创建批处理文件"""
        # 创建启动脚本
        batch_content = f"""@echo off
chcp 65001 > nul
title {self.app_name}

echo.
echo ========================================
echo   {self.app_name} v{self.app_version}
echo ========================================
echo.
echo 请选择要启动的程序:
echo.
echo 1. 序列帧特效预览器 (完整版)
echo 2. 序列帧特效预览器 (简化版)  
echo 3. 退出
echo.

set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    echo 启动完整版...
    start "" "序列帧特效预览器.exe"
) else if "%choice%"=="2" (
    echo 启动简化版...
    start "" "序列帧特效预览器_简化版.exe"
) else if "%choice%"=="3" (
    echo 退出程序
    exit
) else (
    echo 无效选择，请重新运行
    pause
)

exit
"""
        
        batch_path = self.output_dir / "启动程序.bat"
        with open(batch_path, "w", encoding="gbk") as f:
            f.write(batch_content)
        
        print(f"📜 创建启动脚本: {batch_path}")
    
    def get_total_size(self):
        """获取输出文件总大小"""
        total_size = 0
        for file_path in self.output_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def build_all(self):
        """构建所有应用"""
        print(f"🚀 开始构建 {self.app_name} v{self.app_version}")
        print(f"📍 工作目录: {self.script_dir}")
        print(f"💻 系统平台: {platform.system()} {platform.machine()}")
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 清理构建目录
        self.clean_build()
        
        # 创建输出目录
        self.create_output_dir()
        
        # 构建所有应用
        success_count = 0
        total_count = len(self.apps)
        
        for app_key, app_config in self.apps.items():
            if self.build_app(app_key, app_config):
                success_count += 1
        
        # 复制输出文件
        if success_count > 0:
            if self.copy_outputs():
                # 创建说明文件
                self.create_readme()
                
                # 创建批处理文件
                self.create_batch_files()
                
                # 显示构建结果
                total_size = self.get_total_size()
                print(f"\n🎉 构建完成!")
                print(f"✅ 成功构建: {success_count}/{total_count} 个应用")
                print(f"📁 输出目录: {self.output_dir}")
                print(f"📊 总大小: {self.format_size(total_size)}")
                
                # 列出输出文件
                print(f"\n📋 输出文件列表:")
                for file_path in sorted(self.output_dir.iterdir()):
                    if file_path.is_file():
                        size = self.format_size(file_path.stat().st_size)
                        print(f"  📄 {file_path.name} ({size})")
                    elif file_path.is_dir():
                        print(f"  📁 {file_path.name}/")
                
                return True
            else:
                print("❌ 复制输出文件失败")
                return False
        else:
            print("❌ 没有成功构建任何应用")
            return False

def main():
    """主函数"""
    builder = AppBuilder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clean":
            builder.clean_build()
            print("✅ 清理完成")
            return
        elif command == "check":
            if builder.check_dependencies():
                print("✅ 所有依赖都已安装")
            else:
                print("❌ 存在缺失的依赖")
            return
    
    # 默认执行完整构建
    success = builder.build_all()
    
    if success:
        print(f"\n🎊 恭喜! {builder.app_name} 构建成功!")
        print(f"可以在 {builder.output_dir} 目录中找到所有可执行文件")
    else:
        print(f"\n💥 构建失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()