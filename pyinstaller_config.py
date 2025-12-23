#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller配置文件
用于自定义打包参数
"""

# 通用配置
COMMON_CONFIG = {
    # 基本设置
    "clean": True,
    "noconfirm": True,
    "onefile": True,  # 打包成单个exe文件
    "windowed": True,  # 无控制台窗口
    
    # 优化设置
    "optimize": 2,  # Python字节码优化级别
    "strip": True,  # 去除调试信息
    
    # 排除模块 (减小文件大小)
    "excludes": [
        "matplotlib",
        "numpy", 
        "scipy",
        "pandas",
        "jupyter",
        "IPython",
        "notebook",
        "qtconsole",
        "spyder",
        "anaconda",
        "conda",
        "setuptools",
        "distutils",
        "email",
        "html",
        "http",
        "urllib3",
        "xml",
        "xmlrpc",
        "pydoc",
        "doctest",
        "unittest",
        "test",
        "tests",
        "_pytest",
        "pytest"
    ],
    
    # 隐藏导入 (确保必要模块被包含)
    "hidden_imports": [
        "PIL._tkinter_finder",
        "PIL.Image",
        "PIL.ImageTk", 
        "tkinterdnd2",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox"
    ]
}

# 应用特定配置
APP_CONFIGS = {
    "effect_preview": {
        "name": "序列帧特效预览器",
        "script": "effect_preview.py",
        "icon": None,  # 可以指定.ico文件路径
        "add_data": [
            # ("source_path", "dest_path")
            # 如果有资源文件需要打包，在这里添加
        ],
        "upx": True,  # 使用UPX压缩 (需要安装UPX)
    },
    
    "effect_preview_simple": {
        "name": "序列帧特效预览器_简化版", 
        "script": "effect_preview_simple.py",
        "icon": None,
        "add_data": [],
        "upx": True,
    }
}

# UPX配置 (可选，用于进一步压缩)
UPX_CONFIG = {
    "enabled": False,  # 默认关闭，因为可能被杀毒软件误报
    "exclude": [
        "vcruntime140.dll",
        "msvcp140.dll", 
        "api-*.dll"
    ]
}

# 版本信息 (Windows)
VERSION_INFO = {
    "version": "1.0.0.0",
    "company_name": "序列帧特效预览器",
    "file_description": "序列帧特效预览工具",
    "internal_name": "EffectPreview",
    "legal_copyright": "Copyright (C) 2024",
    "original_filename": "EffectPreview.exe",
    "product_name": "序列帧特效预览器",
    "product_version": "1.0.0"
}