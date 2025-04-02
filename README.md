
# 图片水印添加工具 - 项目介绍

## 📌 项目概述
一款基于Python开发的批量图片水印处理工具，采用Pillow进行图像处理，Tkinter构建GUI界面。支持多格式输入输出，提供专业级水印参数配置，兼顾易用性与功能性。

###已构建EXE版本下载：https://pan.baidu.com/s/1aAzdsTPO_5wNHiYFLgHnzA?pwd=jmz1
## ✨技术特点

### 1.用户友好提示：
    - 可视化错误弹窗
    - 操作引导提示
### 2.设置持久化
    - 自动保存配置
    - 跨会话记忆
    - 自动加载上次使用配置
### 3.性能优化
    - 批量处理引擎
    - 多文件队列处理
    - 实时进度反馈：
    
## 🛠️ 核心功能

### 1. 基础处理
- ✅ 批量处理文件夹内所有图片
- 🖼️ 支持输入格式：JPG/PNG/JPEG
- 💾 输出格式可选：JPG/PNG/TIFF/WEBP
- 🔄 图片尺寸智能调整（保持宽高比）

### 2. 水印配置
| 功能 | 参数范围 | 说明 |
|------|---------|------|
| 透明度 | 0.1-1.0 | 水印半透明效果 |
| 大小比例 | 0.1-1.0 | 基于原图尺寸的百分比 |
| 位置预设 | 5种 | 左上/右上/左下/右下/居中 |
| 实时预览 | - | 可视化水印效果 |

# ![image](https://github.com/user-attachments/assets/12c3f56c-78be-48f6-9f6e-b163df49dd31)

### 3. 高级设置
```python
# 各格式专有参数示例
"JPEG": {
    "quality": 95,       # 1-100
    "progressive": True, # 渐进式加载
    "subsampling": 0     # 0=最佳质量
},
"PNG": {
    "compress_level": 6, # 0-9
    "optimize": True     # 霍夫曼编码优化
}
```

# 🚀 使用场景

摄影师版权保护
电商产品图批量处理
社交媒体内容制作
印刷品预处理流程

# 📦 部署方式
    安装依赖
    pip install pillow pyinstaller
    打包为EXE
    pyinstaller --onefile --windowed --icon=watermark.ico watermark_tool.py
# ⚠️ 注意事项
    水印图片建议使用PNG透明背景
    
    大尺寸图片处理需要2GB+内存
    
    输出TIFF格式文件体积较大

# 📜 版本更新
    - v4.0 (当前)
    - ✨ 新增WebP格式支持
    - 🐛 修复DPI设置失效问题
    - 📊 优化进度显示精度

## 📍 项目地址：https://github.com/xujmzd/AddWatermark
## 📧 维护者：xujmzd@gmail.com


