@echo off
chcp 65001 >nul
echo 启动序列帧特效预览器（简化版）
echo ================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    pause
    exit /b 1
)

echo 正在启动...
python effect_preview_simple.py

if errorlevel 1 (
    echo 程序运行出错
    pause
)