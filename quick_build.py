#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速构建脚本 - 简化版本
适合快速测试和构建
"""

import os
import sys
import subprocess
from pathlib import Path

def quick_build(script_name, app_name=None):
    """快速构建单个应用"""
    script_path = Path(script_name)
    
    if not script_path.exists():
        print(f"❌ 脚本文件不存在: {script_name}")
        return False
    
    if not app_name:
        app_name = script_path.stem
    
    print(f"🔨 快速构建: {app_name}")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",           # 单文件
        "--windowed",          # 无控制台
        "--clean",             # 清理缓存
        "--noconfirm",         # 不确认覆盖
        f"--name={app_name}",  # 应用名称
        script_name
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ 构建成功: {app_name}.exe")
        
        # 检查输出文件
        exe_path = Path("dist") / f"{app_name}.exe"
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📁 输出文件: {exe_path}")
            print(f"📊 文件大小: {size:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python quick_build.py <script_name> [app_name]")
        print("")
        print("示例:")
        print("  python quick_build.py effect_preview.py")
        print("  python quick_build.py effect_preview_simple.py 简化版预览器")
        return
    
    script_name = sys.argv[1]
    app_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = quick_build(script_name, app_name)
    
    if success:
        print("\n🎉 快速构建完成!")
    else:
        print("\n💥 构建失败")
        sys.exit(1)

if __name__ == "__main__":
    main()