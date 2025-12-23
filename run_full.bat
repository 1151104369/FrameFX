@echo off
chcp 65001 >nul
echo 启动序列帧特效预览器（完整版）
echo ================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    pause
    exit /b 1
)

echo 正在检查拖拽依赖...
python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo 正在安装拖拽依赖 tkinterdnd2...
    pip install tkinterdnd2
    if errorlevel 1 (
        echo 依赖安装失败，请手动安装：pip install tkinterdnd2
        pause
        exit /b 1
    )
)

echo 正在启动...
python effect_preview.py

if errorlevel 1 (
    echo 程序运行出错
    pause
)