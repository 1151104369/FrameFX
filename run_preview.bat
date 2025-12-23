@echo off
chcp 65001 >nul
echo 序列帧特效预览器启动脚本
echo ========================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在检查依赖包...
python -c "import tkinter, PIL" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install Pillow
    if errorlevel 1 (
        echo 依赖包安装失败，请手动安装：pip install Pillow
        pause
        exit /b 1
    )
)

echo.
echo 选择要运行的版本：
echo 1. 完整版（支持拖拽功能）
echo 2. 简化版（不需要额外依赖）
echo.
set /p choice=请输入选择 (1 或 2): 

if "%choice%"=="1" (
    echo 正在检查拖拽依赖...
    python -c "import tkinterdnd2" >nul 2>&1
    if errorlevel 1 (
        echo 正在安装拖拽依赖...
        pip install tkinterdnd2
        if errorlevel 1 (
            echo 拖拽依赖安装失败，将启动简化版
            python effect_preview_simple.py
        ) else (
            echo 启动完整版...
            python effect_preview.py
        )
    ) else (
        echo 启动完整版...
        python effect_preview.py
    )
) else if "%choice%"=="2" (
    echo 启动简化版...
    python effect_preview_simple.py
) else (
    echo 无效选择，启动简化版...
    python effect_preview_simple.py
)

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)