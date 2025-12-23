@echo off
chcp 65001 > nul
title 序列帧特效预览器 - 打包脚本

echo.
echo ========================================
echo   序列帧特效预览器 - 打包工具
echo ========================================
echo.

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

:: 检查pip是否可用
pip --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip不可用
    pause
    exit /b 1
)

echo ✅ pip工具检查通过

:: 显示菜单
echo.
echo 请选择操作:
echo.
echo 1. 安装打包依赖
echo 2. 检查依赖状态  
echo 3. 开始打包
echo 4. 清理构建文件
echo 5. 退出
echo.

set /p choice=请输入选择 (1-5): 

if "%choice%"=="1" goto install_deps
if "%choice%"=="2" goto check_deps
if "%choice%"=="3" goto build
if "%choice%"=="4" goto clean
if "%choice%"=="5" goto exit
goto invalid_choice

:install_deps
echo.
echo 🔧 安装打包依赖...
echo.
pip install pyinstaller pillow tkinterdnd2
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
pause
goto menu

:check_deps
echo.
echo 🔍 检查依赖状态...
python build.py check
pause
goto menu

:build
echo.
echo 🚀 开始打包应用...
echo.
python build.py
if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)
echo.
echo 🎉 打包完成! 
echo 📁 输出文件在 output 目录中
echo.
set /p open_folder=是否打开输出目录? (y/n): 
if /i "%open_folder%"=="y" (
    start "" "output"
)
pause
goto exit

:clean
echo.
echo 🧹 清理构建文件...
python build.py clean
echo ✅ 清理完成
pause
goto menu

:invalid_choice
echo ❌ 无效选择，请重新输入
pause
goto menu

:menu
cls
goto start

:exit
echo 👋 再见!
exit /b 0

:start
goto menu