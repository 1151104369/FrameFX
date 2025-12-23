# 序列帧特效预览器 - 打包指南

## 📋 目录结构

```
序列帧特效/
├── effect_preview.py              # 主程序 (完整版)
├── effect_preview_simple.py       # 主程序 (简化版)
├── build.py                      # 完整打包脚本
├── build.bat                     # Windows批处理脚本
├── quick_build.py                # 快速构建脚本
├── pyinstaller_config.py         # PyInstaller配置
├── requirements_build.txt        # 打包依赖列表
└── BUILD_GUIDE.md               # 本文档
```

## 🚀 快速开始

### 方法1: 使用批处理脚本 (推荐 - Windows)

1. 双击运行 `build.bat`
2. 选择 "1" 安装依赖
3. 选择 "3" 开始打包
4. 等待完成，输出文件在 `output/` 目录

### 方法2: 使用Python脚本

```bash
# 1. 安装依赖
pip install -r requirements_build.txt

# 2. 检查依赖
python build.py check

# 3. 开始打包
python build.py

# 4. 清理构建文件 (可选)
python build.py clean
```

### 方法3: 快速构建单个应用

```bash
# 构建完整版
python quick_build.py effect_preview.py

# 构建简化版
python quick_build.py effect_preview_simple.py
```

## 📦 打包依赖

### 必需依赖
- `PyInstaller>=5.0.0` - 打包工具
- `Pillow>=9.0.0` - 图像处理
- `tkinterdnd2>=0.3.0` - 拖拽支持

### 安装命令
```bash
pip install pyinstaller pillow tkinterdnd2
```

或使用requirements文件:
```bash
pip install -r requirements_build.txt
```

## 🔧 自定义配置

### 修改应用信息
编辑 `build.py` 中的配置:

```python
self.app_name = "你的应用名称"
self.app_version = "1.0.0"
self.app_description = "应用描述"
```

### 添加图标
1. 准备 `.ico` 格式的图标文件
2. 在 `build.py` 中设置图标路径:

```python
"icon": "path/to/your/icon.ico"
```

### 添加资源文件
在 `build.py` 的 `build_app` 方法中添加:

```python
cmd.extend(["--add-data", f"resource_folder{os.pathsep}resource_folder"])
```

## 📊 输出说明

### 构建成功后的输出结构
```
output/
├── 序列帧特效预览器.exe           # 完整版 (约15-25MB)
├── 序列帧特效预览器_简化版.exe     # 简化版 (约15-25MB)  
├── 启动程序.bat                  # 启动菜单
└── README.txt                   # 使用说明
```

### 文件大小优化
- 单文件模式: 15-25MB (包含Python运行时)
- 目录模式: 可能更大但启动更快
- UPX压缩: 可减小30-50%大小 (可能被杀毒软件误报)

## 🛠️ 高级选项

### 启用UPX压缩
1. 下载并安装 [UPX](https://upx.github.io/)
2. 将UPX添加到系统PATH
3. 在构建命令中添加 `--upx-dir=path/to/upx`

### 添加版本信息
创建 `version_info.txt` 文件:
```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # ...
  ),
  # ...
)
```

然后在构建时添加: `--version-file=version_info.txt`

### 自定义启动画面
```python
cmd.extend(["--splash", "splash_image.png"])
```

## 🐛 常见问题

### 1. PyInstaller未找到
```bash
pip install pyinstaller
```

### 2. 缺少模块错误
在构建命令中添加:
```python
cmd.extend(["--hidden-import", "missing_module"])
```

### 3. 文件过大
- 使用 `--exclude-module` 排除不需要的模块
- 启用UPX压缩
- 考虑使用目录模式而非单文件模式

### 4. 杀毒软件误报
- 不使用UPX压缩
- 添加数字签名
- 向杀毒软件厂商报告误报

### 5. 启动缓慢
- 使用目录模式 (`--onedir`)
- 减少隐藏导入
- 优化代码导入

## 📝 构建脚本说明

### build.py - 完整构建脚本
- 支持批量构建多个应用
- 自动依赖检查
- 生成说明文档和启动脚本
- 详细的构建日志

### quick_build.py - 快速构建
- 单个应用快速构建
- 最小化配置
- 适合开发测试

### build.bat - Windows批处理
- 图形化菜单界面
- 自动环境检查
- 一键式操作

## 🎯 最佳实践

1. **开发阶段**: 使用 `quick_build.py` 快速测试
2. **发布阶段**: 使用 `build.py` 完整构建
3. **定期清理**: 使用 `python build.py clean` 清理缓存
4. **版本管理**: 及时更新版本号和说明文档
5. **测试验证**: 在干净的系统上测试打包后的程序

## 📞 技术支持

如果遇到打包问题:
1. 检查Python和pip版本
2. 确认所有依赖已正确安装
3. 查看构建日志中的错误信息
4. 尝试在虚拟环境中构建